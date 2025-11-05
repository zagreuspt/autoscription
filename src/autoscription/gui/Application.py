import asyncio
import base64
import os
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import webbrowser
from datetime import date, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import diskcache
import pandas as pd
import ttkthemes
from babel.dates import Locale, format_date
from cryptography.fernet import Fernet
from opentelemetry.metrics import get_meter
from opentelemetry.metrics._internal.instrument import Counter
from pandas import read_csv
from PIL import Image, ImageTk
from tkcalendar import DateEntry

from src.autoscription.backend.core import Backend
from src.autoscription.core import core, report
from src.autoscription.core.certificate_manager import use_combined_certs
from src.autoscription.core.config import (
    get_download_dir,
    get_project_root,
    get_report_dir,
    get_scan_dir,
)
from src.autoscription.core.core import Output
from src.autoscription.core.data_types import index_dtype
from src.autoscription.core.errors import (
    ApiFullPrescriptionsSummariesParsingException,
    ApiPartialPrescriptionsSummariesParsingException,
    EmptyOutputException,
    ExtractMetadataFailedException,
    FewScansException,
    IdikaAuthenticationException,
    ScanDirNotFoundException,
    SignInException,
    UserConfigurationRetrievalFailedException,
    WrongDayException,
)
from src.autoscription.core.logging import Monitoring
from src.autoscription.gui.CheckWindow import CheckWindow
from src.autoscription.gui.InfoText import InfoText
from src.autoscription.gui.ScrollableMenu import ScrollableMenu
from src.autoscription.gui.ThreadWithTrace import ThreadWithTrace
from src.autoscription.gui.utils import (
    OPERATION_FAILED_MESSAGE,
    get_prescriptions_for_manual_check,
)
from src.autoscription.idika_client.api_client import IdikaAPIClient, IdikaHttpClient
from src.autoscription.selenium_components.utils import _get_daily_pres_list_df

MAX_NUMBER_OF_DAYS_BEFORE_SCANNER_CLEANUP: int = 8
DEFAULT_WINDOW_WIDTH: int = 410
DEFAULT_WINDOW_HEIGHT: int = 680
WINDOW_WITH_INFO_HEIGHT: int = DEFAULT_WINDOW_HEIGHT + 80


def has_run_inthepast(run_date: date) -> bool:
    return True if list(get_report_dir().glob(f"report_{run_date.strftime('%Y%m%d')}-*.pdf")) else False


def last_scan_exists(last_scan_dir: str) -> bool:
    return os.path.isdir(last_scan_dir)


def last_scan_not_empty(last_scan_dir: str) -> bool:
    jpg_files1 = [f for f in os.listdir(last_scan_dir) if f.endswith(".jpg")]
    return True if len(jpg_files1) != 0 else False


def is_password_less_than_four(password: str) -> bool:
    return len(password) < 4


def space_fill(string: str) -> str:
    return "\n".join([line.ljust(140 - len(line)) for line in string.split("\n")])


def should_user_be_notified(cached_data: diskcache.Cache) -> bool:
    if cached_data["scanner_clean_count"] < MAX_NUMBER_OF_DAYS_BEFORE_SCANNER_CLEANUP:
        return True
    else:
        return False


def update_scanner_clean_cache(cached_data: diskcache.Cache) -> None:
    if cached_data.get("scanner_clean_month", None) is None:
        cached_data["scanner_clean_month"] = 0
    if datetime.today().month != cached_data["scanner_clean_month"]:
        cached_data["scanner_clean_month"] = datetime.today().month
        cached_data["scanner_clean_count"] = 0
    else:
        if cached_data["scanner_clean_count"] < MAX_NUMBER_OF_DAYS_BEFORE_SCANNER_CLEANUP:
            cached_data["scanner_clean_count"] += 1


class Application(ttk.Frame):
    info_frame: ttk.Frame
    reports_menu: Optional[ScrollableMenu]
    reports_button: Optional[ttk.Button]
    backend: Backend
    run_date: datetime  # argument time
    run_datetime: datetime  # execution time

    def __init__(
        self, master: ttkthemes.ThemedTk, application_configuration: Dict[str, Any], monitoring: Monitoring
    ) -> None:
        super().__init__(master)
        self.first_run = True
        self.rundate = None
        self.init_help_button()
        self.reports_menu = None
        self.reports_button = None
        self.processed_dates: List[str] = list()
        self.init_reports_button()
        # Initialize instance variables
        self.run_date: datetime  # argument time
        self.run_datetime: datetime  # execution time
        self.t: Optional[ThreadWithTrace] = None
        self.stop_event = threading.Event()
        self.check_window: CheckWindow
        self.master: ttkthemes.ThemedTk = master
        self.pack()
        self.progress_bar = {"counter": None, "text": None, "queue": None, "total_prescriptions": None}
        self.application_configuration = application_configuration
        self.is_test_user = bool(application_configuration["backend"]["file_uploader"]["test_user"])
        self.monitoring = monitoring

        # Set up the themed style and configure the appearance
        self.master.style = ttkthemes.ThemedStyle()
        self.master.withdraw()  # Hide the window initially
        self.master.style.theme_use("breeze")
        self.master.style.configure("white.TFrame", background="white")
        self.master.style.configure("white.TButton", background="white")
        self.master.configure(background="white")
        self.configure(style="white.TFrame")

        # Configure the main window
        self.master.title("Autoscription")

        self.set_window_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # Initialize username and password variables
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.password_showing = False
        self.fentet_key = application_configuration["fernet_key"]
        # Load cached values, if available
        self.cached_data = diskcache.Cache("cache")
        # self.scanner_clean_month = self.cached_data.get("scanner_clean_month")
        # self.scanner_clean_count = self.cached_data.get("scanner_clean_count")
        cached_username = self.cached_data.get("username")
        cached_encrypted_password = self.cached_data.get("encrypted_password")

        self.info_message_shown: Counter = get_meter("Autoscription").create_counter(
            name="info_message_shown", unit="1", description="Counts Number of Times Info Message is Shown"
        )

        self.handle_user_notification()

        # Set the window icon
        self.icon = ImageTk.PhotoImage(Image.open("resources/gui/app_icon.png"))
        self.master.wm_iconphoto(False, self.icon)

        if cached_username:
            self.username.set(cached_username)
        if cached_encrypted_password:
            self.encrypted_password = cached_encrypted_password
            self.password.set(self.decrypt_password(cached_encrypted_password))

        eye_image = Image.open("resources/gui/eye-regular.png").resize((22, 16))
        eye_slash_image = Image.open("resources/gui/eye-slash-regular.png").resize((22, 16))

        self.eye_open_img = ImageTk.PhotoImage(eye_image)
        self.eye_closed_img = ImageTk.PhotoImage(eye_slash_image)

        # Load and display the image
        pil_image = Image.open("resources/gui/load_image.png").resize((250, 250))
        self.image = ImageTk.PhotoImage(pil_image)
        image_label = tk.Label(self, image=self.image, width=250, height=250, background="white")
        image_label.pack(side=tk.TOP, pady=(55, 40))

        # Create input form and labels
        self.frame = ttk.Frame(self, style="white.TFrame")
        username_label = ttk.Label(self.frame, text="Όνομα Χρήστη", background="white")
        password_label = ttk.Label(self.frame, text="Κωδικός", background="white")
        date_label = ttk.Label(self.frame, text="Ημερομηνία ελέγχου", background="white")

        # Create input form entries
        self.username_entry = ttk.Entry(self.frame, textvariable=self.username, name="username_entry")
        self.password_entry = ttk.Entry(self.frame, textvariable=self.password, show="*", name="password_entry")
        self.username_entry.bind("<FocusOut>", self.on_entry_change)
        self.password_entry.bind("<FocusOut>", self.on_entry_change)

        self.frame_date: DateEntry = DateEntry(
            self.frame, name="date", date_pattern="dd/mm/y", mindate=datetime(2022, 12, 1), maxdate=datetime.today()
        )

        # Place form elements using grid layout
        username_label.grid(row=0, column=0, padx=5, pady=5)
        password_label.grid(row=1, column=0, padx=5, pady=5)
        date_label.grid(row=3, column=0, padx=5, pady=5)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.frame_date.grid(row=3, column=1, padx=5, pady=5)
        # initial image is the closed eye
        self.eye_btn = tk.Button(
            self.frame,
            image=self.eye_closed_img,
            command=self.toggle_password,
            bg="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.eye_btn.grid(row=1, column=2)  # Change Grid position accordingly

        # Pack the frame and other UI elements
        self.frame.pack()
        self.info_label = ttk.Label(self, text="", background="white", justify="center", wraplength=300)
        self.info_label.pack(pady=(10, 10))

        # Create and pack the submit button
        self.submit_button = ttk.Button(
            self, text="Έναρξη ελέγχου", command=self.submit, style="white.TButton", name="start", state="enabled"
        )
        self.submit_button.pack(side=tk.BOTTOM, pady=(10, 10))

        # Force focus and bring the window to the front
        # self.bring_window_to_front()

        # Center the window on the screen
        # self.master.update_idletasks()
        self.show_ui()

        self.monitoring.logger_adapter.warning("Application opened")

        # Handle window close event
        self.master.protocol("WM_DELETE_WINDOW", self.handle_close)

        # Define an operation dictionary with some initial values
        self.operation = {"failed": False, "message": "OperationFailed"}
        self.backend = Backend(configuration=application_configuration["backend"], monitoring=self.monitoring)
        self.core = core.Core(monitoring=self.monitoring)
        self.output = Output(None, None, None, None, None)
        self.master.after(500, self.show_ui)  # Schedule UI to appear after a 500ms delay

    def show_ui(self) -> None:
        self.master.after_idle(self.center_and_show)
        self.master.after_idle(self.bring_window_to_front)

    def center_and_show(self) -> None:
        self.center_window()
        self.master.deiconify()

    def bring_window_to_front(self) -> None:
        self.master.attributes("-topmost", True)
        self.master.after_idle(self.master.attributes, "-topmost", False)
        self.master.focus_force()

    def center_window(self) -> None:
        self.master.update_idletasks()
        width = 410
        height = 625
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    def on_entry_change(self, event: tk.Event) -> None:  # type: ignore[type-arg]   # noqa: [U100]
        # Encrypt the password before caching it
        raw_password = self.password.get()
        if raw_password:
            encrypted_password = self.encrypt_password(raw_password)
            self.cached_data["encrypted_password"] = encrypted_password
        else:
            # If the password is empty, don't cache it
            self.cached_data.pop("encrypted_password", None)

        # Update cached username
        self.cached_data["username"] = self.username.get()

    def encrypt_password(self, password: str) -> bytes:
        cipher_suite: Fernet = Fernet(self.fentet_key)
        encrypted_password: bytes = cipher_suite.encrypt(password.encode("utf-8"))
        return encrypted_password

    def decrypt_password(self, encrypted_password: bytes) -> str:
        cipher_suite: Fernet = Fernet(self.fentet_key)
        try:
            return cipher_suite.decrypt(encrypted_password).decode("utf-8")  # type: ignore[no-any-return]
        except TypeError:
            self.monitoring.logger_adapter.warning(
                f"Password decrypt failed for encrypted_password type: {type(encrypted_password)}"
            )
            return ""
        except Exception:
            self.monitoring.logger_adapter.warning("Password decrypt failed returned empty string")
            return ""

    # After password entry creation, define a function to toggle password visibility
    def toggle_password(self) -> None:
        if self.password_entry["show"] == "*":
            self.password_entry["show"] = ""
            self.eye_btn["image"] = self.eye_open_img
        else:
            self.password_entry["show"] = "*"
            self.eye_btn["image"] = self.eye_closed_img

    def open_pdf(self, path: Path) -> None:
        # Function to open the PDF report
        # For this example, I'm using os.system and the default PDF reader on Windows.
        # You can adjust this based on your specific needs.
        self.monitoring.logger_adapter.warning(f"User opened {path}")
        os.system(f"start {path}")  # TODO: This should use os.open

    def extract_date_time(self, filename: str) -> Tuple[str, str, str]:
        """
        Extract the date for analysis and the run date from the report filename.
        Returns a tuple for sorting.
        """
        # Split the filename to extract date and time components
        if filename.count("_"):
            parts = filename.split("_")
        else:
            parts = ["00000000", "00000000", "000000"]

        if parts[1].count("-"):
            analysis_date, run_date = parts[1].split("-")
        else:
            analysis_date, run_date = "00000000", "00000000"

        # Check if time part exists, if not, set a default value for time
        time_part = parts[2] if len(parts) > 2 else "000000"

        # Return tuple (analysis_date, run_date, time_part) for sorting
        return (analysis_date, run_date, time_part)

    def report_format_date(self, date_time_obj: Tuple[str, str, str]) -> str:
        # Convert the analysis date string from the tuple to a datetime.date object
        analysis_date_str = date_time_obj[0]  # Analysis date is the first item in the tuple
        analysis_date_obj = datetime.strptime(analysis_date_str, "%Y%m%d").date()

        # Format the date as desired
        formatted_date = format_date(analysis_date_obj, format="full", locale=Locale("el", "GR"))
        return str(formatted_date)

    def remove_last_scans(self) -> None:
        self.monitoring.logger_adapter.warning("Last scanned prescriptions cleanup. pop-up shown")
        agree_to_remove_temp_scans = messagebox.askyesno(
            "Καθαρισμός προσωρινών σαρώσεων",
            "Πρόκειται να διαγράψετε τις σαρωμένες συνταγές που υπάρχουν στην προσωρινή μνήμη."
            + "\nΘα χρειαστεί να σαρώσετε πάλι τις συνταγές της ημέρας προς έλεγχο.\nΕίστε σίγουροι ;",
        )
        if agree_to_remove_temp_scans:
            self.monitoring.logger_adapter.warning("Last scanned prescriptions cleanup. Confirmed.")
            core.remove_last_scan_dir(Path(self.application_configuration["last_scan_dir"]))
            messagebox.showinfo(
                "Επιτυχής καθαρισμός",
                "Οι σαρωμένες συντάγες που υπάρχουν στην προσωρινή μνήμη διεγράφησαν."
                + "\nΠαρακαλώ σαρώστε πάλι τις συνταγές της ημέρας προς έλεγχο.",
            )
        else:
            self.monitoring.logger_adapter.warning("Last scanned prescriptions cleanup. Declined.")

    def init_reports_button(self) -> None:
        if not self.reports_menu:
            self.reports_menu = ScrollableMenu(self.master)
            self.reports_menu.hide()

        # Scan the directory for report files
        report_files = [file for file in get_report_dir().glob("report_*.pdf")]

        # Sort by extracted datetime and reverse to get newest first
        report_files_sorted = sorted(report_files, key=lambda x: self.extract_date_time(x.stem), reverse=True)
        recent_files_len = 62
        # Get the {recent_files_len} most recent
        report_files_sorted = report_files_sorted[:recent_files_len]

        # Process these reports from oldest to newest
        files_for_menu: List[Path] = list()
        for report_file in report_files_sorted:  # reverse the list to go from oldest to newest
            if len(self.processed_dates) > recent_files_len:
                break
            date_time_obj = self.extract_date_time(report_file.stem)
            formatted_date = self.report_format_date(date_time_obj)

            if formatted_date not in self.processed_dates:
                # This date hasn't been processed yet, so add it to the menu
                self.processed_dates.append(formatted_date)
                files_for_menu.append(report_file)

        self.reports_menu.option_clear()
        for formatted_date, report_file in zip(reversed(self.processed_dates), reversed(files_for_menu)):
            self.reports_menu.add_command(label=formatted_date, command=self.open_pdf, report_file=report_file)

        if not self.reports_button:
            # Create the style object
            style = ttk.Style()

            # Define a new style that inherits from the main TButton style
            style.configure(
                "Reports.TButton",
                borderwidth=5,
                relief="groove",
                foreground="black",
                background="white",
                font=("Arial", 8),
                padding=(0, 0, 0, 0),
            )

            # Create the button with the defined style
            self.reports_button = ttk.Button(
                self.master, text="Αναφορές", style="Reports.TButton", command=self.show_reports_menu
            )

            # Place the Help button at the bottom right
            self.reports_button.place(relx=0.81, rely=0.99, anchor="se")

    def show_reports_menu(self) -> None:
        self.init_reports_button()
        # Calculate the x-coordinate such that the menu's right end aligns with the button's right end
        if self.reports_menu is not None and self.reports_button is not None:
            x = (
                self.reports_button.winfo_rootx()
                + self.reports_button.winfo_width()
                - self.reports_menu.winfo_reqwidth()
            )

            # Calculate the y-coordinate to position the menu above the button
            # Manually adjust for the button's height
            y = (
                self.reports_button.winfo_rooty()
                - self.reports_menu.winfo_reqheight()
                - self.reports_button.winfo_height()
            )

            # Ensure the menu doesn't overflow outside the window's top edge
            if y < 0:
                y = 0
            self.monitoring.logger_adapter.warning("Reports_menu_opened")
            self.reports_menu.post(x, y)

    def init_help_button(self) -> None:
        # Create the menu
        self.help_menu = tk.Menu(
            self.master, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )

        # Here we are adding the functionality to open the user manual PDF when "Εγχειρίδιο χρήστη" is pressed
        user_manual_path = get_project_root() / "resources" / "gui" / "Autoscription_Process_Manual.pdf"
        user_process_path = get_project_root() / "resources" / "gui" / "Autoscription_Process.pdf"
        scanner_process_path = get_project_root() / "resources" / "gui" / "Scanner_Process_Manual.pdf"
        sync_errors_path = get_project_root() / "resources" / "gui" / "Sync_errors.pdf"
        operation_failed_path = get_project_root() / "resources" / "gui" / "OperationFailed.pdf"
        process_cleanup_guide = get_project_root() / "resources" / "gui" / "Process_Cleanup_Guide.pdf"
        menu_small_font = ("Arial", 8)

        # Create the submenu for "Ανταλλακτικά"
        self.scanner_maint_cons_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.scanner_maint_cons_menu.add_command(
            label="Ανταλλακτικά",
            command=lambda: webbrowser.open(
                "https://www.pfu.ricoh.com/imaging/"
                "downloads/manual/ss_webhelp/en/help/webhelp/"
                "topic/ma_prepare_consumable.html"
            ),
            font=menu_small_font,
        )
        self.scanner_maint_cons_menu.add_command(
            label="Αλλαγή rollers (video)",
            command=lambda: webbrowser.open("https://www.youtube.com/watch?v=p3GpR-LrrdA"),
            font=menu_small_font,
        )

        # Create the submenu for "Καθαρισμός"
        self.scanner_maint_clean_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.scanner_maint_clean_menu.add_command(
            label="Καθαρισμός τζαμάκια (video)",
            command=lambda: webbrowser.open("https://youtu.be/3ENooWtnCJo"),
            font=menu_small_font,
        )
        self.scanner_maint_clean_menu.add_command(
            label="Καθαρισμός rollers (video)",
            command=lambda: (
                webbrowser.open("https://youtu.be/VkCBLUouRvA"),
                webbrowser.open("https://youtu.be/u7ikBFqx-a0"),
            ),
            font=menu_small_font,
        )

        # Create the submenu for "Συντήρηση"
        self.scanner_maint_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.scanner_maint_menu.add_command(
            label="Ειδοποίησεις οθόνης",
            command=lambda: webbrowser.open(
                (
                    "https://www.pfu.ricoh.com/imaging/"
                    "downloads/manual/ss_webhelp/en/help/webhelp/"
                    "topic/ma_notice_check.html"
                )
            ),
            font=menu_small_font,
        )
        self.scanner_maint_menu.add_cascade(
            label="Καθαρισμός", menu=self.scanner_maint_clean_menu, font=menu_small_font
        )
        self.scanner_maint_menu.add_cascade(
            label="Ανταλλακτικά", menu=self.scanner_maint_cons_menu, font=menu_small_font
        )

        # Create the submenu for "Σαρωτής"
        self.scanner_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.scanner_menu.add_command(
            label="Σύνδεση με υπολογιστή",
            command=lambda: webbrowser.open(
                "https://www.pfu.ricoh.com/imaging/"
                "downloads/manual/ss_webhelp/en/help/webhelp/"
                "topic/tb_connect_usb.html"
            ),
            font=menu_small_font,
        )
        self.scanner_menu.add_command(
            label="Πολλαπλή ανίχνευση τροφοδοσίας",
            command=lambda: webbrowser.open(
                "https://www.pfu.ricoh.com/imaging/"
                "downloads/manual/ss_webhelp/en/help/webhelp/"
                "topic/tb_multi_detect.html"
            ),
            font=menu_small_font,
        )
        self.scanner_menu.add_cascade(label="Συντήρηση", menu=self.scanner_maint_menu, font=menu_small_font)

        # Create the submenu for "Εφαρμογή"
        self.app_problems_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.app_problems_menu.add_command(
            label="Αποτυχία Συγχρονισμού με ΗΔΙΚΑ",
            command=lambda: self.open_pdf(sync_errors_path),
            font=menu_small_font,
        )
        self.app_problems_menu.add_command(
            label="OperationFailed", command=lambda: self.open_pdf(operation_failed_path), font=menu_small_font
        )
        self.app_problems_menu.add_command(
            label="Οδηγίες Τερματισμού Διεργασιών",
            command=lambda: self.open_pdf(process_cleanup_guide),
            font=menu_small_font,
        )

        self.app_problems_menu.add_command(
            label="Καθαρισμός προσωρινών σαρώσεων",
            command=lambda: self.remove_last_scans(),
            font=menu_small_font,
        )

        # Create the submenu for "Οδηγίες Χρήσης"
        self.help_maual_menu = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )
        self.help_maual_menu.add_command(
            label="Σύνοψη Διαδικασίας", command=lambda: self.open_pdf(user_process_path), font=menu_small_font
        )
        self.help_maual_menu.add_command(
            label="Οδηγίες σάρωσης", command=lambda: self.open_pdf(scanner_process_path), font=menu_small_font
        )
        self.help_maual_menu.add_command(
            label="Οδηγίες εφαρμογής", command=lambda: self.open_pdf(user_manual_path), font=menu_small_font
        )

        self.privacy_and_security = tk.Menu(
            self.help_menu, tearoff=0, activeforeground="white", activebackground="lightblue", bg="white"
        )

        self.privacy_and_security.add_command(
            label="Πολιτική Απορρήτου",
            command=lambda: webbrowser.open(
                "https://materiatechnica.com/wp-content/uploads/2024/05/Privacy-Policy.pdf"
            ),
            font=menu_small_font,
        )

        # Add the submenu to the main menu under "Προβλήματα σαρωτή"
        self.help_menu.add_cascade(label="Σαρωτής", menu=self.scanner_menu, font=menu_small_font)

        # Add items to the menu
        self.help_menu.add_cascade(label="Εφαρμογή", menu=self.app_problems_menu, font=menu_small_font)
        self.help_menu.add_cascade(label="Οδηγίες χρήσης", menu=self.help_maual_menu, font=menu_small_font)
        self.help_menu.add_cascade(label="Απόρρητο και ασφάλεια", menu=self.privacy_and_security, font=menu_small_font)

        # Create the style object
        style = ttk.Style()

        # Define a new style that inherits from the main TButton style
        style.configure(
            "Help.TButton",
            borderwidth=5,
            relief="groove",
            foreground="black",
            background="white",
            font=("Arial", 8),
            padding=(0, 0, 0, 0),
        )

        # Create the button with the defined style
        self.help_button = ttk.Button(self.master, text="Βοήθεια", style="Help.TButton", command=self.show_help_menu)

        # Place the Help button at the bottom right
        self.help_button.place(relx=0.98, rely=0.99, anchor="se")

    def show_help_menu(self) -> None:
        # Calculate the x-coordinate such that the menu's right end aligns with the button's right end
        x = self.help_button.winfo_rootx() + self.help_button.winfo_width() - self.help_menu.winfo_reqwidth()

        # Calculate the y-coordinate to position the menu above the button
        # Manually adjust for the button's height
        y = self.help_button.winfo_rooty() - self.help_menu.winfo_reqheight() - self.help_button.winfo_height()
        self.monitoring.logger_adapter.warning("Help_menu_opened")
        # Ensure the menu doesn't overflow outside the window's top edge
        if y < 0:
            y = 0

        self.help_menu.post(x, y)

    def submit(self) -> None:
        # Retrieving the username and password from the GUI form
        username_low_case = self.username.get().lower()
        password = self.password.get()

        # Getting the current datetime
        self.run_datetime = datetime.now()
        # Getting the date entered in the GUI form
        self.run_date = self.frame_date.get_date()
        # Set to Greek locale
        # Format the datetime object into the format you want
        formatted_date = format_date(self.run_date, format="full", locale=Locale("el", "GR"))
        # If the response from the whitelist URL verifies that the user is whitelisted and
        # returns the same check string that we sent, the user is allowed to proceed

        #
        last_scan_dir = self.application_configuration["last_scan_dir"]
        try:
            user_configuration = self.backend.get_user_configuration(username_low_case)
        except Exception as e:
            self.monitoring.logger_adapter.error("Failed to retrieve user configuration")
            self.info_label["text"] = "Αποτυχία ελέγχου άδειας λογισμικού. Παρακαλώ προσπαθήστε ξανά."
            self.operation["failed"] = True
            raise UserConfigurationRetrievalFailedException(e)
        self.application_configuration["reporting"]["execution_time_ordering"] = user_configuration["time_order"]
        self.application_configuration["reporting"]["show_overview"] = user_configuration["reporting_show_overview"]
        self.application_configuration["reporting"]["category_breakdown"] = user_configuration[
            "report_category_breakdown"
        ]
        self.application_configuration["detectors"]["max_threads"] = user_configuration["detectors_max_threads"]
        self.application_configuration["idika_integration"]["guessing_pharmacy_id"]["is_enabled"] = user_configuration[
            "should_guess_pharmacy_id"
        ]

        self.update_config_for_test_user()

        if user_configuration["use_selfsigned_certificates"]:
            use_combined_certs(get_project_root())

        if user_configuration["is_user_allowed"]:
            if is_password_less_than_four(password):
                self.info_label[
                    "text"
                ] = "Παρακαλώ συμπληρώστε τον \nκωδικό πρόσβασης, πρέπει να περιέχει τουλάχιστον 4 χαρακτήρες"
                self.monitoring.logger_adapter.warning("Submit clicked with empty password in application.")
            else:
                # Add a confirmation dialog here to ask user if they're sure
                is_user_sure = messagebox.askyesno(
                    "Έπιβεβαίωση ημέρομηνίας ελέγχου",
                    f"Να ξεκινήσει ο έλεγχος των συνταγών για \n{formatted_date};",
                )
                if is_user_sure:
                    idika_api_client = IdikaAPIClient(
                        idika_http_client=IdikaHttpClient(
                            base_url=self.application_configuration["api"]["base_url"],
                            api_key=self.application_configuration["api"]["api_key"],
                            username=username_low_case,
                            password=password,
                        ),
                    )
                    # TODO: do not pass credentials through configuration
                    # Combine the username and password into a single string in the format "username:password"
                    credentials = f"{username_low_case}:{password}"

                    # Encode the credentials as base64
                    credentials_base64 = base64.b64encode(credentials.encode()).decode()
                    self.application_configuration["api"]["credentials_base64"] = credentials_base64
                    # TODO: add generic Exception in except
                    try:
                        idika_api_client.authenticate()
                        try:
                            total_active_pharmacist_units = len(idika_api_client.get_active_pharmacist_units())
                            self.monitoring.logger_adapter.warning(
                                "Total active pharmacist units for"
                                f" {username_low_case}: {total_active_pharmacist_units}"
                            )
                        except Exception as e:
                            self.monitoring.logger_adapter.warning(
                                f"Failed to retrieve total active pharmacist units for {username_low_case}"
                            )
                            self.monitoring.logger_adapter.exception(e)
                    except IdikaAuthenticationException as e:
                        self.operation["failed"] = True
                        self.info_label["text"] = (
                            "Αποτυχία συγχρονισμού. Ο κωδικός είναι λάθος.\n"
                            "Παρακαλούμε ανανεώστε τον κωδικό και ξαναπροσπαθήστε."
                        )
                        self.monitoring.logger_adapter.error("Idika Sync failed")
                        raise SignInException(e)
                    # Disabling form fields as user is validated and process starts
                    if has_run_inthepast(self.run_date):
                        # Add a confirmation dialog here to ask user if they're sure
                        self.monitoring.logger_adapter.warning(
                            f"Evaluation has been already performed for {self.run_date}"
                        )
                        past_run_question = messagebox.askyesno(
                            "Ελεγμένη ημέρα",
                            f"Έχει ήδη πραγματοποιηθεί έλεγχος για \n{formatted_date}; "
                            + "\nΘέλετε να τρέξετε την διαδικασία πάλι; ",
                        )
                        # TODO: simplify if-else body
                        if past_run_question:
                            self.monitoring.logger_adapter.warning(f"Re-evaluation initiated for {formatted_date}")
                            self.username_entry["state"] = "disabled"
                            self.password_entry["state"] = "disabled"
                            self.frame_date["state"] = "disabled"
                            self.info_label["text"] = "\nΟ έλεγχος των συνταγών βρίσκεται σε εξέλιξη...\n "
                            self.submit_button["state"] = "disabled"
                            self.operation["failed"] = False
                            if self.first_run:
                                self.first_run = False
                                threading.excepthook = self.except_hook
                            self.progress_bar["counter"] = None
                            self.operation["message"] = None
                            self.output = Output(None, None, None, None, None)
                            self.t = ThreadWithTrace(
                                target=lambda: self.core.run(
                                    username=username_low_case,
                                    scanner_output_directory=last_scan_dir,
                                    scan_date=self.run_date,
                                    config=self.application_configuration,
                                    progress_bar=self.progress_bar,
                                    application=self,
                                    idika_api_client=idika_api_client,
                                    output=self.output,
                                ),
                                daemon=True,
                            )
                            self.t.start()
                            self.schedule_check()
                    else:
                        self.username_entry["state"] = "disabled"
                        self.password_entry["state"] = "disabled"
                        self.frame_date["state"] = "disabled"
                        self.info_label["text"] = "\nΟ έλεγχος των συνταγών βρίσκεται σε εξέλιξη...\n "
                        self.submit_button["state"] = "disabled"
                        self.operation["failed"] = False
                        if self.first_run:
                            self.first_run = False
                            threading.excepthook = self.except_hook
                        self.progress_bar["counter"] = None
                        self.operation["message"] = None
                        self.output = Output(None, None, None, None, None)
                        self.t = ThreadWithTrace(
                            target=lambda: self.core.run(
                                username=username_low_case,
                                scanner_output_directory=last_scan_dir,
                                scan_date=self.run_date,
                                config=self.application_configuration,
                                progress_bar=self.progress_bar,
                                application=self,
                                idika_api_client=idika_api_client,
                                output=self.output,
                            )
                        )
                        self.t.start()
                        self.schedule_check()
        else:
            # If the user is not whitelisted or the check string does not match, an error message is displayed
            self.info_label["text"] = "Πρόβλημα με την άδεια λογισμικού. \nΠαρακαλώ επιβεβαιώστε το όνομα χρήστη."
            self.monitoring.logger_adapter.warning(f'Username:"{username_low_case}" not licenced.')

    def schedule_check(self) -> None:
        """Schedule check_if_done() function after one second."""
        self.master.after(1000, self.check_if_done)
        if self.progress_bar["counter"]:
            try:
                total = self.progress_bar["counter"].value
                if self.progress_bar["total_prescriptions"]:
                    progress = int(
                        (self.progress_bar["counter"].value / self.progress_bar["total_prescriptions"]) * 100
                    )
                    total = f"{progress if progress <= 100 else 100}%"
                    # f"/ {self.progress_bar['total_prescriptions']}\n"
                self.info_label[
                    "text"
                ] = f"\nΟ έλεγχος των συνταγών βρίσκεται σε εξέλιξη...\n {self.progress_bar['text']}{total}"
            except Exception:
                pass
            # {self.progress_bar['counter'].value}"

    def check_if_done(self) -> None:
        # If the thread has finished, re-enable the button and show a message.
        if self.t and not self.t.is_alive():
            self.username_entry["state"] = "normal"
            self.password_entry["state"] = "normal"
            self.frame_date["state"] = "normal"
            self.submit_button["state"] = "normal"
            if self.operation["failed"]:
                self.info_label["text"] = self.operation["message"]
                asyncio.run(
                    self.backend.report_run_summary(
                        "failure",
                        scan_date=self.run_date,
                        username_low_case=self.username.get().lower(),
                        total_prescriptions=0,
                        total_scanned_documents=0,
                        total_amount=0,
                        total_insurance_amount=0,
                        total_patient_amount=0,
                        total_eopyy_amount=0,
                        total_other_funds_amount=0,
                    )
                )
            else:
                try:
                    if (
                        self.output.pages is None
                        or self.output.dosages is None
                        or self.output.api_partial_prescriptions_summaries is None
                        or self.output.api_full_prescriptions_summaries is None
                    ):
                        raise EmptyOutputException()

                    pages_df = self.output.pages
                    dosages_df = self.output.dosages
                    partial_prescription_summaries = self.output.api_partial_prescriptions_summaries
                    full_prescription_summaries = self.output.api_full_prescriptions_summaries

                    prescriptions_for_manual_check = get_prescriptions_for_manual_check(
                        pages_df=read_csv(StringIO(pages_df.to_csv(sep="|", index=False)), dtype=object, sep="|"),
                        scan_directory=get_scan_dir(self.run_date),
                    )

                    download_dir = get_download_dir(self.run_date)
                    scan_dir = get_scan_dir(self.run_date)
                    pres_timestamp_df = _get_daily_pres_list_df(download_dir=download_dir)
                    index_df: pd.DataFrame = pd.read_csv(scan_dir / "index.csv").astype(index_dtype)

                except Exception as e:
                    self.monitoring.logger_adapter.error(f"Failed to parse pages file {e}")
                    self.monitoring.logger_adapter.exception(e)
                    self.info_label["text"] = OPERATION_FAILED_MESSAGE
                    return
                self.info_label["text"] = "Ο έλεγχος των συνταγών ολοκληρώθηκε με επιτυχία!"
                # TODO:check if there is any of the checks false.
                # If not then why run the check window. Found as i would
                # like to run without waiting all the time to run
                reports_dir = get_project_root() / "executions" / "reports"
                formatted_datetime: str = self.run_datetime.strftime("%Y%m%d_%H%M%S")
                report_file_name = f"report_{self.run_date.strftime('%Y%m%d')}-{formatted_datetime}.pdf"
                report_file_path = reports_dir / report_file_name

                if prescriptions_for_manual_check:
                    try:
                        CheckWindow(
                            master=self,
                            pages=pages_df,
                            dosages=dosages_df,
                            partial_prescription_summaries=partial_prescription_summaries,
                            full_prescription_summaries=full_prescription_summaries,
                            pres_timestamp_df=pres_timestamp_df,
                            index_df=index_df,
                            prescriptions=prescriptions_for_manual_check,
                            run_date=self.run_date,
                            run_datetime=self.run_datetime,
                            config=self.application_configuration,
                            monitoring=self.monitoring,
                            backend=self.backend,
                            username=self.username.get(),
                        )
                    except Exception as e:
                        self.monitoring.logger_adapter.error(f"Failed during check window instantiation {e}")
                        self.monitoring.logger_adapter.exception(e)
                        self.info_label["text"] = OPERATION_FAILED_MESSAGE
                        return
                else:
                    self.monitoring.logger_adapter.warning("No prescriptions flagged for manual check.")
                    try:
                        if not self.is_test_user:
                            # Convert to prevent float conversion issues, same as in CheckWindow
                            dosages = pd.read_csv(StringIO(dosages_df.to_csv(index=False, sep="|")), sep="|")
                            pages = pd.read_csv(StringIO(pages_df.to_csv(index=False, sep="|")), sep="|")
                            index = pd.read_csv(StringIO(index_df.to_csv(index=False, sep="|")), sep="|")
                            pres_timestamp = pd.read_csv(StringIO(pres_timestamp_df.to_csv(index=False, sep="|")), sep="|")
                            
                            # Ensure 'manual_check' column exists
                            if 'manual_check' not in pages.columns:
                                pages['manual_check'] = None  # or False, depending on your logic

                            self.backend.upload(
                                filename="pages",
                                dataframe=pages,
                                scan_date=self.run_date,
                                execution_timestamp=self.run_datetime,
                                username=self.username.get().lower(),
                                file_format="parquet",
                            )
                            self.backend.upload(
                                filename="dosages",
                                dataframe=dosages,
                                scan_date=self.run_date,
                                execution_timestamp=self.run_datetime,
                                username=self.username.get().lower(),
                                file_format="parquet",
                            )
                            self.backend.upload(
                                filename="index",
                                dataframe=index,
                                scan_date=self.run_date,
                                execution_timestamp=self.run_datetime,
                                username=self.username.get().lower(),
                                file_format="parquet",
                            )
                            self.backend.upload(
                                filename="daily_prescriptions",
                                dataframe=pres_timestamp,
                                scan_date=self.run_date,
                                execution_timestamp=self.run_datetime,
                                username=self.username.get().lower(),
                                file_format="parquet",
                            )
                        
                        report_data = report.get_report_data(
                            pages=pages_df,
                            dosages=dosages_df,
                            partial_prescription_summaries=partial_prescription_summaries,
                            full_prescription_summaries=full_prescription_summaries,
                            run_date=self.run_date,
                            report_config=self.application_configuration["reporting"],
                            business_rules_config=self.application_configuration["business_rules"],
                            monitoring=self.monitoring,
                        )
                        report.generate_report(report_data, report_file_path)
                        self.monitoring.logger_adapter.warning(f"Report Generated: {report_file_path}")
                    except Exception as e:
                        self.monitoring.logger_adapter.error(f"Failed during report generation in Application.py {e}")
                        self.monitoring.logger_adapter.exception(e)
                        self.info_label["text"] = OPERATION_FAILED_MESSAGE
                        return
                    webbrowser.open(url=report_file_path.as_posix(), new=2)
                    if not self.is_test_user:
                        asyncio.run(
                            self.backend.send_report(
                                path=report_file_path, dt=self.run_date, username=self.username.get()
                            )
                        )
                        asyncio.run(
                            self.backend.report_run_summary(
                                "success",
                                scan_date=self.run_date,
                                username_low_case=self.username.get().lower(),
                                total_prescriptions=pages_df.pharmacist_idika_prescription_full.nunique(),
                                total_scanned_documents=pages_df.prescription_scanned_pages.nunique(),
                                total_amount=report_data["total_revenue_value"],
                                total_patient_amount=report_data["total_patient_contribution_value"],
                                total_insurance_amount=report_data["total_gov_contribution_value"],
                                total_eopyy_amount=report_data["total_eopyy_amount_value"],
                                total_other_funds_amount=report_data["total_other_funds_amount_value"],
                            )
                        )
                self.handle_api_files()
                self.init_reports_button()
        else:
            self.schedule_check()

    def handle_api_files(self) -> None:
        if not self.is_test_user:
            try:
                api_dosages: pd.DataFrame = self.output.api_dosages
                self.backend.upload(
                    filename="api_dosages",
                    dataframe=api_dosages,
                    scan_date=self.run_date,
                    execution_timestamp=self.run_datetime,
                    username=self.username.get().lower(),
                    file_format="parquet",
                )
                api_partial_prescriptions_summaries: pd.DataFrame = self.output.api_partial_prescriptions_summaries
                self.backend.upload(
                    filename="api_partial_prescriptions_summaries",
                    dataframe=api_partial_prescriptions_summaries,
                    scan_date=self.run_date,
                    execution_timestamp=self.run_datetime,
                    username=self.username.get().lower(),
                    file_format="parquet",
                )
                api_full_prescriptions_summaries: pd.DataFrame = self.output.api_full_prescriptions_summaries
                self.backend.upload(
                    filename="api_full_prescriptions_summaries",
                    dataframe=api_full_prescriptions_summaries,
                    scan_date=self.run_date,
                    execution_timestamp=self.run_datetime,
                    username=self.username.get().lower(),
                    file_format="parquet",
                )
            except Exception as e:
                self.monitoring.logger_adapter.error("Failed to read or upload api files")
                self.monitoring.logger_adapter.exception(e)

    def except_hook(self, args: threading.ExceptHookArgs) -> None:
        self.operation["failed"] = True
        self.monitoring.logger_adapter.warning(f"OperationFailed for {self.username} {self.run_date}")
        if isinstance(args.exc_value, SignInException):
            self.operation["message"] = (
                "Αποτυχία συγχρονισμού.\n "
                "Αυτή τη στιγμή δεν είναι δυνατός ο συγχρονισμός δεδομένων λόγω προβλήματος απόκρισης "
                "των server της ΗΔΙΚΑ (εμβόλια)."
                "\nΠαρακαλούμε ξαναδοκιμάστε αργότερα."
            )
            self.monitoring.logger_adapter.error("Idika Sync failed")
        elif isinstance(args.exc_value, ScanDirNotFoundException):
            self.operation["message"] = (
                "Δεν βρέθηκαν συνταγές προς έλεγχο.\n Παρακαλώ σαρώστε τις συνταγές της ημέρας"
                + "\n επιλέγοντας το προφίλ 'Autoscription' στον σαρωτή."
            )
            self.monitoring.logger_adapter.warning(
                "Last_scan folder does not exist or empty. No scanned prescriptions in last_scan"
            )
        elif isinstance(args.exc_value, WrongDayException):
            self.operation[
                "message"
            ] = "Παρακαλώ επιλέξτε σωστή ημερομηνία ή σαρώστε πάλι μια ημέρα και ξαναπροσπαθήσετε."
            self.monitoring.logger_adapter.error("The user seen the wrong date warning message.")
        elif isinstance(args.exc_value, ApiFullPrescriptionsSummariesParsingException):
            self.operation["message"] = (
                "Αποτυχία συγχρονισμού.\n "
                "Αυτή τη στιγμή δεν είναι δυνατός ο συγχρονισμός δεδομένων λόγω προβλήματος απόκρισης "
                "των server της ΗΔΙΚΑ (συνταγές)."
                "\nΠαρακαλούμε ξαναδοκιμάστε αργότερα."
            )
            self.monitoring.logger_adapter.error("Idika Full Prescription Sync failed")
        elif isinstance(args.exc_value, ApiPartialPrescriptionsSummariesParsingException):
            self.operation["message"] = (
                "Αποτυχία συγχρονισμού.\n "
                "Αυτή τη στιγμή δεν είναι δυνατός ο συγχρονισμός δεδομένων λόγω προβλήματος απόκρισης "
                "των server της ΗΔΙΚΑ (συνταγές)."
                "\nΠαρακαλούμε ξαναδοκιμάστε αργότερα."
            )
            self.monitoring.logger_adapter.error("Idika Partial Prescription Sync failed")
        elif isinstance(args.exc_value, FewScansException):
            self.operation["message"] = (
                "Ο αριθμός των συνταγών που έχουν σαρωθεί είναι σημαντικά λιγότερος από τις συνταγές της ημέρας."
                + "\nΠαρακαλώ σαρώστε πάλι όλες τις συνταγές της ημέρας προς έλεγχο."
            )
            self.monitoring.logger_adapter.error("The user seen the few scans warning message.")
        elif isinstance(args.exc_value, ExtractMetadataFailedException):
            if isinstance(args.exc_value.args[0], PermissionError):
                self.handle_permission_error()
            else:
                self.operation["message"] = f"{OPERATION_FAILED_MESSAGE}\nΠαρακαλώ δοκιμάστε ξανά."
                self.monitoring.logger_adapter.error("The user seen the extract metadata failed warning message ")
        elif isinstance(args.exc_value, PermissionError):
            self.handle_permission_error()
        else:
            self.operation["message"] = OPERATION_FAILED_MESSAGE
            self.monitoring.logger_adapter.exception(args.exc_value)
            self.monitoring.logger_adapter.error(
                "The user seen the operation failed with unhandled exception type warning message"
            )

    def handle_permission_error(self) -> None:
        self.operation["message"] = (
            f"{OPERATION_FAILED_MESSAGE}\n"
            f"Παρακαλώ ακολουθήσετε τις οδηγίες στο\n\n"
            f"Βοήθεια > Εφαρμογή >\nΟδηγίες Τερματισμού Διεργασιών\n\n"
            f"και επανεκκινήστε την εφαρμογή."
        )
        self.monitoring.logger_adapter.error("The user seen the permission error warning message")

    def wrong_date_review(self) -> bool:
        messagebox.showwarning(
            "Προσοχή! Αναντιστοιχία ημέρας ελέγχου.",
            "Οι σαρωμένες συνταγές δεν αντιστοιχούν στην ημερομηνία επιλογής."
            + "\n\nΠεριπτώσεις:"
            + "\n\n1. Λάθος επιλογή ημερομηνίας από τον χρήστη:"
            + "\n - Επιλέξτε την σωστή ημερομηνία προς έλεγχο. "
            + "\n - Μην σαρώσετε πάλι τις συνταγές."
            + "\n\n2. Σάρωση περίσσότερων από μια ημερών:"
            + "\n - Σαρώστε πάλι τις συνταγές (μιας ημέρας) προς έλεγχο.",
        )
        self.monitoring.logger_adapter.warning("Wrong_date_review: The user selected a wrong date.")
        return False

    def handle_close(self) -> None:
        if self.t and self.t.is_alive():
            should_close_not_finished = messagebox.askyesno(
                "Προσοχή! Ο έλεγχος των συνταγών βρίσκεται ακόμα σε εξέλιξη...",
                "Παρακαλώ περιμένε να τελειώσει η εν ενεργεία διαδικασία πριν κλείσετε το πρόγραμμα.\n"
                "Αν διακοπεί θα πρέπει να ξεκινήσει η διαδικασία από την αρχή."
                + "\nΕίστε βέβαιοι να διακόψετε το σύστημα;",
            )
            if should_close_not_finished:
                self.monitoring.logger_adapter.warning("Application hard-close.")
                self.core.cleanup()
                self.t.kill()
                self.master.destroy()

        else:
            should_close_finished = messagebox.askyesno(
                "Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε " + "να κλείσετε το πρόγραμμα;"
            )

            if should_close_finished:
                self.monitoring.logger_adapter.warning("Application soft-close.")
                self.master.destroy()

    def handle_user_notification(self) -> None:
        update_scanner_clean_cache(cached_data=self.cached_data)
        if should_user_be_notified(cached_data=self.cached_data):
            self.set_window_size(DEFAULT_WINDOW_WIDTH, WINDOW_WITH_INFO_HEIGHT)
            self.info_frame = ttk.Frame(self, width=410, style="white.TFrame")
            self.info_frame.pack(anchor=tk.N)
            InfoText(self.info_frame, monitoring=self.monitoring)
            self.info_message_shown.add(1)
            warning_message = f"Info Message Shown, with counter value: {self.cached_data['scanner_clean_count']}"
            self.monitoring.logger_adapter.warning(warning_message)

    def set_window_size(self, width: int, height: int) -> None:
        self.master.maxsize(width=width, height=height)
        self.master.minsize(width=width, height=height)

    def update_config_for_test_user(self) -> None:
        if self.application_configuration["backend"]["file_uploader"]["test_user"] == True:
            self.application_configuration["turbo_mode"] = True
            self.application_configuration["is_debug_enabled"] = False
            self.application_configuration["detectors"]["signature"]["options"]["preprocessing"]["extract_signatures"][
                "debug"
            ] = False
            self.application_configuration["idika_integration"]["is_enabled"] = True
            self.application_configuration["detectors"]["stamp"]["is_enabled"] = False
            self.application_configuration["detectors"]["signature"]["is_enabled"] = False
            self.application_configuration["detectors"]["signature"]["options"]["preprocessing"]["extract_signatures"][
                "is_enabled"
            ] = False
            self.application_configuration["detectors"]["missing_coupons"]["is_enabled"] = False
            self.application_configuration["detectors"]["missing_coupons"]["options"]["template_matching"] = False
