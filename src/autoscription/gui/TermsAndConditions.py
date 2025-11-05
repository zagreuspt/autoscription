import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, scrolledtext
from typing import Optional

import diskcache
import ttkthemes
from PIL import Image, ImageTk

from src.autoscription.core.logging import Monitoring


class TermsAndConditionsUI(ttk.Frame):
    monitoring: Monitoring

    def __init__(self, master: ttkthemes.ThemedTk, monitoring: Monitoring, terms_version: str) -> None:
        super().__init__(master)
        self.monitoring = monitoring
        self.master = master
        self.master.withdraw()  # type: ignore[attr-defined]
        self.is_window_open = True  # Add this line to track if the window is open
        self.master.style = ttkthemes.ThemedStyle()  # type: ignore[attr-defined]
        self.master.style.configure("white.TFrame", background="white")  # type: ignore[attr-defined]
        self.master.style.configure("white.TButton", background="white")  # type: ignore[attr-defined]
        self.master.title("Σύμβαση Παραχώρησης Άδειας Χρήσης Λογισμικού")  # type: ignore[attr-defined]
        self.master.geometry("800x700")  # type: ignore[attr-defined]
        self.master.maxsize(800, 700)  # type: ignore[attr-defined]
        self.master.minsize(800, 700)  # type: ignore[attr-defined]
        self.cached_data = diskcache.Cache("cache")
        self.terms_version = terms_version

        self.icon = ImageTk.PhotoImage(Image.open("resources/gui/app_icon.png"))
        self.master.wm_iconphoto(False, self.icon)  # type: ignore[attr-defined]
        self.master.after(500, self.show_ui)
        self.center_window()

        self.create_ui()

    def center_window(self) -> None:
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")  # type: ignore[attr-defined]

    def create_ui(self) -> None:
        self.master.deiconify()  # type: ignore[attr-defined]

        label = tk.Label(
            self.master,
            text="Παρακαλούμε διαβάστε προσεκτικά τους όρους χρήσης λογισμικού:",
            anchor="w",
            padx=25,
            pady=10,
        )
        label.pack(pady=10, padx=10, fill="x")

        self.terms_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=100, height=35)
        with open("resources/gui/terms.txt", "r", encoding="utf-8") as file:
            file_contents = file.read()
        self.terms_text.insert(tk.INSERT, file_contents)
        self.terms_text.bind("<MouseWheel>", self.check_scroll_position)
        self.terms_text.bind("<Button-4>", self.check_scroll_position)  # Linux scroll up
        self.terms_text.bind("<Button-5>", self.check_scroll_position)  # Linux scroll down
        self.terms_text.config(state="disabled")
        self.terms_text.pack(padx=5, pady=(5, 5))

        self.accept_btn = ttk.Button(
            self.master, text="Συμφωνώ", command=self.accept_terms, style="accept.TButton", state="disabled"
        )
        decline_btn = ttk.Button(self.master, text="Διαφωνώ", command=self.decline_terms, style="decline.TButton")

        self.accept_btn.bind("<Enter>", lambda event: self.on_enter(event, "accept"))
        self.accept_btn.bind("<Leave>", lambda event: self.on_leave(event, "accept"))
        decline_btn.bind("<Enter>", lambda event: self.on_enter(event, "decline"))
        decline_btn.bind("<Leave>", lambda event: self.on_leave(event, "decline"))

        # self.check_scroll_position()  # type: ignore[attr-defined]
        # Now, instead of binding the scroll event directly to check_scroll_position, we initiate a periodic check.
        self.periodic_scroll_check()
        decline_btn.pack(side="left", padx=20, pady=(5, 10))
        self.accept_btn.pack(side="right", padx=20, pady=(5, 10))

        self.master.protocol("WM_DELETE_WINDOW", self.on_close_request)  # type: ignore[attr-defined]

        self.master.mainloop()

    def show_ui(self) -> None:
        self.center_window()
        self.master.deiconify()  # type: ignore[attr-defined]

    def periodic_scroll_check(self) -> None:
        """Periodically checks if the user has scrolled to the bottom of the terms."""
        if not self.is_window_open:
            return
        self.check_scroll_position()
        self.master.after(100, self.periodic_scroll_check)

    def check_scroll_position(self, event: Optional[tk.Event] = None) -> None:  # type: ignore[type-arg] # noqa: U100
        """Check if the scrollbar is at the bottom and enable the accept button if so."""
        top_fraction, bottom_fraction = self.terms_text.yview()
        if bottom_fraction == 1.0:
            self.accept_btn.config(state="normal")
        else:
            self.accept_btn.config(state="disabled")

    def on_close_request(self) -> None:
        response = messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε να κλείσετε το παράθυρο?")
        if response:
            self.is_window_open = False  # Update the flag
            self.cached_data["accept_terms"] = False
            self.monitoring.logger_adapter.warning("Terms window was closed")
            self.master.destroy()

    def accept_terms(self) -> None:
        self.cached_data["accept_terms"] = True
        self.cached_data["terms_version"] = self.terms_version
        self.monitoring.logger_adapter.warning(
            f"Terms v{self.terms_version} were accepted by {self.cached_data.get('username')}"
        )
        self.is_window_open = False
        self.master.destroy()

    def decline_terms(self) -> None:
        self.cached_data["accept_terms"] = False
        self.monitoring.logger_adapter.warning("Terms were declined")
        self.master.destroy()

    def on_enter(self, event: tk.Event, button_name: str) -> None:  # type: ignore[type-arg] # noqa: U100
        self.master.style.configure(button_name + ".TButton", background="lightblue")  # type: ignore[attr-defined]

    def on_leave(self, event: tk.Event, button_name: str) -> None:  # type: ignore[type-arg]  # noqa: U100
        self.master.style.configure(button_name + ".TButton", background="white")  # type: ignore[attr-defined]
