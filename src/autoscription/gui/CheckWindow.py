import asyncio
import datetime
import tkinter.messagebox as messagebox
import webbrowser
from io import StringIO
from tkinter import FLAT, Button, Event, Toplevel, ttk
from typing import Any, Dict, List

import pandas as pd
from azure.core.exceptions import ClientAuthenticationError
from PIL import Image, ImageTk

from src.autoscription.backend.core import Backend
from src.autoscription.core import config, report
from src.autoscription.core.logging import Monitoring
from src.autoscription.gui.utils import OPERATION_FAILED_MESSAGE, create_tooltip


class CheckWindow(Toplevel):
    # "[{image_path:"", stack number: ""}]"
    # return list on close
    backend: Backend
    username: str

    def __init__(
        self,
        config: Dict[str, Any],
        master: ttk.Frame,
        prescriptions: List[Dict[str, Any]],
        pages: pd.DataFrame,
        dosages: pd.DataFrame,
        partial_prescription_summaries: pd.DataFrame,
        full_prescription_summaries: pd.DataFrame,
        pres_timestamp_df: pd.DataFrame,
        index_df: pd.DataFrame,
        run_date: datetime.date,
        run_datetime: datetime.datetime,
        backend: Backend,
        username: str,
        monitoring: Monitoring,
    ) -> None:
        super().__init__(master)
        self.configuration = config
        # Initialize button states and summary as instance variables
        self.buttons_state: Dict[str, str] = {}
        self.summary = None

        # Set window title, size, and minimum size
        self.title("Χειροκίνητη επιβεβαίωση διφορούμενων συνταγών")
        self.geometry("850x850")
        self.minsize(850, 850)
        # Load and set the window icon
        self.icon = ImageTk.PhotoImage(Image.open("resources/gui/app_icon.png"))
        self.wm_iconphoto(False, self.icon)
        self.stamp_icon = ImageTk.PhotoImage(Image.open("resources/icons/stamp_sign.png").resize((60, 70)))
        self.coupon_icon = ImageTk.PhotoImage(Image.open("resources/icons/coupon.png").resize((60, 60)))

        # Store provided file paths and dates as instance variables
        self.pages = pages
        self.dosages = dosages
        self.partial_prescription_summaries = partial_prescription_summaries
        self.full_prescription_summaries = full_prescription_summaries
        self.index_df = index_df
        self.pres_timestamp_df = pres_timestamp_df
        self.run_date = run_date
        self.run_datetime = run_datetime
        self.monitoring = monitoring

        # Set the close event handler for the window.
        self.protocol("WM_DELETE_WINDOW", self.handle_close)

        # Configure ttk Style
        # Create a new style object and configure it for the window.
        self.s = ttk.Style()
        self.s.configure("labelFrame.TFrame", background="white")

        # Initialize the current image index and sort the
        # prescriptions by the stack number.
        self.current_image = 0
        filtered_prescriptions = [x for x in prescriptions if not isinstance(x["stack_number"], float)]
        sorted_prescriptions = sorted(filtered_prescriptions, key=lambda x: int(float(x["stack_number"])))

        # Set width and height for displaying images (A4 ratio)
        width = 560
        height = int(width * 1.414)  # A4 ration 1:1414
        # TODO: rename to prescriptions
        # TODO: from list of lists to list of dict

        # Sort prescriptions by stack number and store them as a list of lists
        # Load the images and resize them to a suitable size.
        self.images = [
            {
                "image": Image.open(prescription["image_path"]).resize((width, height), resample=Image.ADAPTIVE),
                "manual_check": None,
                "stack_number": prescription["stack_number"],
                "check_coupons": prescription["check_coupons"],
                "check_signatures": prescription["check_signatures"],
                "check_stamps": prescription["check_stamps"],
                "missing_tapes": prescription["missing_tapes"],
                "surplus_tapes": prescription["surplus_tapes"],
            }
            for prescription in sorted_prescriptions
        ]

        # Create and configure main_frame
        self.main_frame = ttk.Frame(self)

        # Create and configure main_frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid_columnconfigure(0, weight=1)  # Set weight for left_side_frame column
        self.main_frame.grid_columnconfigure(1, weight=3)  # Set larger weight for image_frame column
        self.main_frame.grid_columnconfigure(2, weight=1)  # Set weight for right_side_frame column
        self.main_frame.grid_rowconfigure(0, weight=1)  # If needed, set weights for rows

        # Create and configure image_frame
        self.image_frame = ttk.Frame(self.main_frame, width=width, height=height, style="labelFrame.TFrame")
        self.image_frame.pack_propagate(False)
        self.image = ImageTk.PhotoImage(self.images[0]["image"])
        self.label = ttk.Label(self.image_frame, image=self.image, background="white")
        self.label.pack()
        self.image_frame.grid(row=0, column=1, padx=5, pady=5)

        # Create right_side_frame and left_side_frame
        self.main_frame_right_side_frame = ttk.Frame(
            self.main_frame, width=width, height=height, name="right_side_frame"
        )
        self.main_frame_left_side_frame = ttk.Frame(self.main_frame, width=width, height=height, name="left_side_frame")

        self.main_frame_right_side_frame_icon_c = ttk.Label(self.main_frame_right_side_frame, image=self.coupon_icon)
        self.main_frame_right_side_frame_icon_s = ttk.Label(self.main_frame_right_side_frame, image=self.stamp_icon)
        create_tooltip(self.main_frame_right_side_frame_icon_c, "Ταινίες Γνησιότητας")
        create_tooltip(self.main_frame_right_side_frame_icon_s, "Yπογραφές \nΣφραγίδες")

        # Create and configure the Next button
        self.next_image = ImageTk.PhotoImage(Image.open("resources/gui/next.png").resize((60, 90)))
        self.main_frame_right_side_frame_next = Button(
            self.main_frame_right_side_frame,
            text="Next",
            name="next_button",
            image=self.next_image,
            command=self.handle_next,
            state="disabled",
            bd=0,
            highlightthickness=0,
            relief=FLAT,
        )
        self.main_frame_right_side_frame_next.grid(row=0, column=0, padx=10, pady=(350, 0), sticky="n")
        icon_padding = 20
        # Create and configure the Hint label
        self.main_frame_right_side_frame_hint = ttk.Label(self.main_frame_right_side_frame, name="hint")
        self.main_frame_right_side_frame_hint.grid(row=1, column=0, padx=5, pady=(icon_padding, 0), sticky="n")
        self.main_frame_right_side_frame_icon_c.grid(row=2, column=0, padx=5, pady=(icon_padding, 0), sticky="n")
        self.main_frame_right_side_frame_icon_s.grid(row=3, column=0, padx=5, pady=(icon_padding, 0), sticky="n")

        # Create and configure the Green Check button
        self.green_check_default_image = ImageTk.PhotoImage(
            Image.open("resources/gui/green_check_default.png").resize((70, 70))
        )
        self.green_check_selected_image = ImageTk.PhotoImage(
            Image.open("resources/gui/green_check_selected.png").resize((70, 70))
        )
        self.main_frame_right_side_frame_green_check = Button(
            self.main_frame_right_side_frame,
            image=self.green_check_default_image,
            command=self.handle_check,
            name="green_check",
            bd=0,
            highlightthickness=0,
            relief=FLAT,
        )
        self.main_frame_right_side_frame_green_check.grid(row=5, column=0, padx=10, pady=5, sticky="s")

        # Configure right_side_frame's grid

        self.main_frame_right_side_frame.rowconfigure(1, weight=1)
        self.main_frame_right_side_frame.grid(row=0, column=2, padx=5, pady=5, rowspan=2, sticky="nswe")

        # Create and configure the Previous button
        self.previous_image = ImageTk.PhotoImage(Image.open("resources/gui/previous.png").resize((60, 90)))
        self.main_frame_left_side_frame_previous = Button(
            self.main_frame_left_side_frame,
            text="Previous",
            name="previous_button",
            image=self.previous_image,
            command=self.handle_previous,
            state="disabled",
            bd=0,
            highlightthickness=0,
            relief=FLAT,
        )
        self.main_frame_left_side_frame_previous.grid(row=0, column=0, padx=10, pady=(350, 0), sticky="n")

        # Create and configure the Red X button
        self.red_x_default_image = ImageTk.PhotoImage(Image.open("resources/gui/red_x_default.png").resize((70, 70)))
        self.red_x_selected_image = ImageTk.PhotoImage(Image.open("resources/gui/red_x_selected.png").resize((70, 70)))
        self.main_frame_left_side_frame_red_x = Button(
            self.main_frame_left_side_frame,
            image=self.red_x_default_image,
            command=self.handle_deny,
            name="red_x",
            bd=0,
            highlightthickness=0,
            relief=FLAT,
        )

        # Configure left_side_frame's grid
        self.main_frame_left_side_frame_red_x.grid(row=1, column=0, padx=10, pady=5, sticky="s")
        self.main_frame_left_side_frame.rowconfigure(1, weight=1)
        self.main_frame_left_side_frame.grid(row=0, column=0, padx=10, pady=5, rowspan=2, sticky="nsew")

        self.main_frame.pack()

        # Update the widgets
        self.update_widgets()

        # Bind left and right arrow key events
        self.bind("<Left>", self.left_key_pressed)
        self.bind("<Right>", self.right_key_pressed)

        self.initialize_window()
        self.monitoring.logger_adapter.warning("CheckWindow opened")
        self.backend = backend
        self.username = username

    def bring_window_to_front(self) -> None:
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.focus_force()

    def center_window(self, screen_width: int, screen_height: int) -> None:
        width = int(self.winfo_width() * screen_width / self.winfo_screenwidth())
        height = int(self.winfo_height() * screen_height / self.winfo_screenheight())
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    def initialize_window(self) -> None:
        self.bring_window_to_front()
        self.update_idletasks()
        # screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = screen_height * 0.99 / 850  # Use 70% of the screen height
        self.apply_scaling(scale)
        # self.center_window(screen_width, screen_height)
        self.state("zoomed")

    def apply_scaling(self, scale: float) -> None:
        # Resize window, icon, and buttons
        self.geometry(f"{int(850 * scale)}x{int(850 * scale)}")
        self.minsize(int(850 * scale), int(850 * scale))

        # Resize image_frame
        width = int(560 * scale)
        height = int(width * 1.414)  # A4 ratio 1:1.414
        self.image_frame.config(width=width, height=height)

        # Resize images while maintaining aspect ratio
        for i, prescription in enumerate(self.images):
            self.images[i]["image"] = prescription["image"].resize((width, height), resample=Image.ADAPTIVE)

        # Update the displayed image
        self.image = ImageTk.PhotoImage(self.images[self.current_image]["image"])
        self.label.config(image=self.image)
        scale_factor = 20
        # Update padding
        self.image_frame.grid_configure(padx=int(5 * scale), pady=int(5 * scale))
        self.main_frame_right_side_frame_green_check.grid_configure(padx=int(5 * scale), pady=int(5 * scale))
        self.main_frame_left_side_frame_red_x.grid_configure(padx=int(5 * scale), pady=int(5 * scale))

        self.main_frame_right_side_frame_next.grid_configure(padx=int(5 * scale), pady=(int(350 * scale), 0))
        self.main_frame_left_side_frame_previous.grid_configure(padx=int(5 * scale), pady=(int(350 * scale), 0))

        self.main_frame_right_side_frame_hint.grid_configure(padx=int(5 * scale), pady=(int(scale_factor * scale), 0))

    def handle_close(self) -> None:
        self.store_buttons_state()
        self.disable_buttons()
        is_incomplete_check: bool = any(x["manual_check"] is None for x in self.images)
        if is_incomplete_check:
            close_confirm_title: str = "Προσοχή! O Χειροκίνητος έλεγχος δεν έχει ολοκληρωθεί."
            close_confirm_message: str = (
                "Είστε σίγουροι ότι θέλετε να τερματίσετε το "
                "πρόγραμμα; \n"
                "Αν συνεχίσετε οι συνταγές που δεν ελέγξατε θα θεωρηθούν λανθασμένες!!!"
            )
        else:
            close_confirm_title = "Επιβεβαίωση χειροκίνητου έλεγχου"
            close_confirm_message = (
                "Ολοκληρώσατε την διαδικασία.\n Είστε σίγουροι ότι θέλετε να τερματίσετε το πρόγραμμα;"
            )
        if messagebox.askyesno(
            close_confirm_title,
            close_confirm_message,
        ):
            if is_incomplete_check:
                self.monitoring.logger_adapter.warning(
                    "CheckWindow hard-close, all unchecked prescriptions set to False."
                )
                self.images = [{**x, "manual_check": False} if x["manual_check"] is None else x for x in self.images]
            else:
                self.monitoring.logger_adapter.warning("CheckWindow soft-close.")

            manual_check_df = pd.DataFrame(
                self.images,
                columns=[
                    "image",
                    "manual_check",
                    "stack_number",
                    "check_coupons",
                    "check_signatures",
                    "check_stamps",
                ],
            )[["stack_number", "manual_check"]]
            # transformation of pages to object and inferred type to avoid errors in merge
            # manual_check works on object type, code in Application.py
            # TODO: remove this workaround when the issue is resolved
            pages_as_object = pd.read_csv(
                StringIO(self.pages.to_csv(index=False, sep="|")), dtype=object, sep="|"
            ).drop(["manual_check_x", "manual_check_y", "manual_check"], axis=1, errors="ignore")
            pages_as_object_with_manual_check = pages_as_object.merge(manual_check_df, on="stack_number", how="left")
            pages = pd.read_csv(
                StringIO(pages_as_object_with_manual_check.to_csv(index=False, sep="|")), header=0, sep="|"
            )
            if self.configuration["backend"]["file_uploader"]["test_user"]:
                pages.to_csv("pages-final.csv", sep="|", index=False)
            # transformation ends here

            reports_dir = config.get_project_root() / "executions" / "reports"
            formatted_run_datetime: str = self.run_datetime.strftime("%Y%m%d_%H%M%S")
            report_file_name = "report_" f'{self.run_date.strftime("%Y%m%d")}-' f"{formatted_run_datetime}.pdf"
            report_file_path = reports_dir / report_file_name
            try:
                if not self.configuration["backend"]["file_uploader"]["test_user"]:
                    # this fixes issues with float conversion during to_parquet() method
                    dosages = pd.read_csv(StringIO(self.dosages.to_csv(index=False, sep="|")), sep="|")
                    self.try_to_upload_files(dosages, self.index_df, pages, self.pres_timestamp_df)
                report_data = report.get_report_data(
                    pages=pages,
                    dosages=self.dosages,
                    partial_prescription_summaries=self.partial_prescription_summaries,
                    full_prescription_summaries=self.full_prescription_summaries,
                    run_date=self.run_date,
                    report_config=self.configuration["reporting"],
                    business_rules_config=self.configuration["business_rules"],
                    monitoring=self.monitoring,
                )
                report.generate_report(report_data, report_file_path)
            except Exception as e:
                self.monitoring.logger_adapter.error(f"Failed during report generation in Application.py {e}")
                self.monitoring.logger_adapter.exception(e)
                # TODO: statement to be removed on the first opportunity,
                #  it highly couples the Application with CheckWindow
                self.master.info_label["text"] = OPERATION_FAILED_MESSAGE  # type: ignore[attr-defined]
                self.destroy()
                return
            self.monitoring.logger_adapter.warning(f"Report Generated: {report_file_path}")
            webbrowser.open(url=report_file_path.as_posix(), new=2)  # open in new tab
            if not self.configuration["backend"]["file_uploader"]["test_user"]:
                asyncio.run(self.backend.send_report(path=report_file_path, dt=self.run_date, username=self.username))
                asyncio.run(
                    self.backend.report_run_summary(
                        "success",
                        scan_date=self.run_date,
                        username_low_case=self.username,
                        total_prescriptions=pages.pharmacist_idika_prescription_full.nunique(),
                        total_scanned_documents=pages.prescription_scanned_pages.nunique(),
                        total_amount=report_data["total_revenue_value"],
                        total_patient_amount=report_data["total_patient_contribution_value"],
                        total_insurance_amount=report_data["total_gov_contribution_value"],
                        total_eopyy_amount=report_data["total_eopyy_amount_value"],
                        total_other_funds_amount=report_data["total_other_funds_amount_value"],
                    )
                )
            self.destroy()
        else:
            self.restore_buttons_state()

    def try_to_upload_files(
        self, dosages: pd.DataFrame, index_df: pd.DataFrame, pages_data: pd.DataFrame, pres_timestamp_df: pd.DataFrame
    ) -> None:
        try:
            self.upload_files(
                dosages_data=dosages,
                pages_data=pages_data,
                index_df=index_df,
                pres_timestamp_df=pres_timestamp_df,
            )
        except ClientAuthenticationError as e:
            self.monitoring.logger_adapter.error("Failed to upload files due to client authentication error.")
            self.monitoring.logger_adapter.exception(e)
        except Exception as e:
            self.monitoring.logger_adapter.error("Failed to upload files.")
            self.monitoring.logger_adapter.exception(e)

    def handle_check(self) -> None:
        self.images[self.current_image]["manual_check"] = True
        self.update_widgets()
        self.handle_next()

    def handle_deny(self) -> None:
        self.images[self.current_image]["manual_check"] = False
        self.update_widgets()
        self.handle_next()

    def handle_next(self) -> None:
        if self.current_image < len(self.images) - 1:
            self.move_to_next_image()
            if self.images[self.current_image]["manual_check"] is None:
                self.main_frame_right_side_frame_next["state"] = "disabled"
            else:
                self.main_frame_right_side_frame_next["state"] = "normal"
            self.update_widgets()
        else:
            if None not in [x["manual_check"] for x in self.images]:
                self.handle_close()
            else:
                self.handle_close()

    def move_to_next_image(self) -> None:
        self.current_image = self.current_image + 1
        self.image = ImageTk.PhotoImage(self.images[self.current_image]["image"])
        self.label.image = self.image  # type: ignore[attr-defined]  #label has attribute image
        self.label.configure(image=self.image)
        if self.current_image == len(self.images) - 1:
            self.main_frame_right_side_frame_next["text"] = "Finish"
        if self.current_image >= 0:
            self.main_frame_left_side_frame_previous["state"] = "normal"

    def handle_previous(self) -> None:
        if self.current_image > 0:
            self.current_image = self.current_image - 1
            self.image = ImageTk.PhotoImage(self.images[self.current_image]["image"])
            self.label.image = self.image  # type: ignore[attr-defined]  #label has attribute image
            self.label.configure(image=self.image)
            self.update_widgets()
            self.main_frame_right_side_frame_next["state"] = "normal"
            if self.current_image == 0:
                self.main_frame_left_side_frame_previous["state"] = "disabled"
            if self.current_image > 0:
                self.main_frame_right_side_frame_next["text"] = "Next"

    def update_widgets(self) -> None:
        # here we change hint text
        # TODO: extract to method that calculates hint
        stack_int: int
        try:
            stack_int = int(float(self.images[self.current_image]["stack_number"]))
        except (ValueError, TypeError):
            stack_int = 0
        hint = (
            f"Θέση: {stack_int}\nΕπιβεβαίωση:\n"
            + (
                f"Απούσες ταινίες γνησιότητας: {self.images[self.current_image]['missing_tapes']}\n"
                if self.images[self.current_image]["missing_tapes"]
                and self.images[self.current_image]["missing_tapes"].strip() != "nan"
                else ""
            )
            + (
                f"Πλεονάζουσες ταινίες γνησιότητας  {self.images[self.current_image]['surplus_tapes']}"
                if self.images[self.current_image]["missing_tapes"]
                and self.images[self.current_image]["missing_tapes"].strip() != "nan"
                and self.images[self.current_image]["surplus_tapes"]
                and self.images[self.current_image]["surplus_tapes"].strip() != "nan"
                else ""
            )
        )
        if self.images[self.current_image]["check_coupons"] == "False":
            self.main_frame_right_side_frame_icon_c.grid()

        else:
            self.main_frame_right_side_frame_icon_c.grid_remove()

        if (
            self.images[self.current_image]["check_signatures"] == "False"
            or self.images[self.current_image]["check_stamps"] == "False"
        ):
            self.main_frame_right_side_frame_icon_s.grid()
        else:
            self.main_frame_right_side_frame_icon_s.grid_remove()

        self.main_frame_right_side_frame_hint["text"] = hint
        if not self.images[self.current_image]["manual_check"]:
            self.main_frame_right_side_frame_green_check["image"] = self.green_check_default_image
            self.main_frame_left_side_frame_red_x["image"] = self.red_x_selected_image
        if self.images[self.current_image]["manual_check"]:
            self.main_frame_left_side_frame_red_x["image"] = self.red_x_default_image
            self.main_frame_right_side_frame_green_check["image"] = self.green_check_selected_image
        if self.images[self.current_image]["manual_check"] is None:
            self.main_frame_left_side_frame_red_x["image"] = self.red_x_default_image
            self.main_frame_right_side_frame_green_check["image"] = self.green_check_default_image

    def disable_buttons(self) -> None:
        self.main_frame_left_side_frame_previous["state"] = "disabled"
        self.main_frame_left_side_frame_red_x["state"] = "disabled"
        self.main_frame_right_side_frame_next["state"] = "disabled"
        self.main_frame_right_side_frame_green_check["state"] = "disabled"

    def store_buttons_state(self) -> None:
        self.buttons_state = {
            "previous_button": self.main_frame_left_side_frame_previous["state"],
            "red_x": self.main_frame_left_side_frame_red_x["state"],
            "next_button": self.main_frame_right_side_frame_next["state"],
            "green_check": self.main_frame_right_side_frame_green_check["state"],
        }

    def restore_buttons_state(self) -> None:
        self.main_frame_left_side_frame_previous["state"] = self.buttons_state["previous_button"]
        self.main_frame_left_side_frame_red_x["state"] = self.buttons_state["red_x"]
        self.main_frame_right_side_frame_next["state"] = self.buttons_state["next_button"]
        self.main_frame_right_side_frame_green_check["state"] = self.buttons_state["green_check"]

    # Event class has no generic argument
    def left_key_pressed(self, event: Event) -> None:  # type: ignore[type-arg]   # noqa: [U100]
        self.handle_previous()

    # Event class has no generic argument
    def right_key_pressed(self, event: Event) -> None:  # type: ignore[type-arg]   # noqa: [U100]
        self.handle_next()

    def upload_files(
        self,
        dosages_data: pd.DataFrame,
        index_df: pd.DataFrame,
        pages_data: pd.DataFrame,
        pres_timestamp_df: pd.DataFrame,
    ) -> None:
        self.backend.upload(
            filename="pages",
            dataframe=pages_data,
            scan_date=self.run_date,
            execution_timestamp=self.run_datetime,
            username=self.username,
            file_format="parquet",
        )
        self.backend.upload(
            filename="dosages",
            dataframe=dosages_data,
            scan_date=self.run_date,
            execution_timestamp=self.run_datetime,
            username=self.username,
            file_format="parquet",
        )
        self.backend.upload(
            filename="index",
            dataframe=index_df,
            scan_date=self.run_date,
            execution_timestamp=self.run_datetime,
            username=self.username,
            file_format="parquet",
        )
        self.backend.upload(
            filename="daily_prescriptions",
            dataframe=pres_timestamp_df,
            scan_date=self.run_date,
            execution_timestamp=self.run_datetime,
            username=self.username,
            file_format="parquet",
        )
