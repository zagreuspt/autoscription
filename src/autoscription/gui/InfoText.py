from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

from opentelemetry.metrics import get_meter
from opentelemetry.metrics._internal.instrument import Counter

from src.autoscription.core.logging import Monitoring

font_size = 8
normal_font = ("TkDefaultFont", font_size)
bold_font = ("TkDefaultFont", font_size, "bold")
bold_underline_font = ("TkDefaultFont", font_size, "bold underline")


def space_fill(string: str) -> str:
    return "\n".join([line.ljust(140 - len(line)) for line in string.split("\n")])


class InfoText(tk.Text):
    def __init__(self, master: ttk.Frame, monitoring: Monitoring) -> None:
        super().__init__(
            master,
            height=5,
            width=410,
            background="#C0EEF8",
            foreground="#032433",
            borderwidth=1,
            highlightthickness=0,
            relief="flat",
            spacing1=0,  # Spacing above a line
            spacing2=0,  # Spacing between lines
            spacing3=0,  # Spacing below a line
            font=normal_font,  # Apply the font with specified size
            padx=0,  # Horizontal padding; adjust the value as needed
            pady=8,  # Vertical padding; adjust the value as needed
        )

        full_text = space_fill(
            "     Υπενθύμιση:\n"
            + "     Για την ομαλή λειτουργία του ελέγχου θυμηθείτε:\n"
            + "       -  τον καθαρίσμο του σαρωτή (εμπλοκές και σφάλματα τροφοδοσίας)\n"
            + "       -  την ανανέωση του μελανιού στις σφραγίδες (λιγότερες διφορούμενες)\n"
            + "       -  την αντικατάσταση των αναλωσίμων του εκτυπωτή (αναγνώριση barcode)"
        )
        self.insert(tk.END, full_text)

        # Apply the 'bold_underline' tag to "Ενημέρωση:"
        self.tag_add("bold_underline", "1.5", "1.15")
        self.tag_add("bold", "4.27", "4.36")
        self.tag_add("bold", "5.32", "5.42")

        # Configure the tag with bold and underline font
        self.tag_configure("bold", font=bold_font)
        self.tag_configure("bold_underline", font=bold_underline_font)

        # Tagging the word "σαρωτή" with a new tag 'hyperlink'
        hyperlink_start = "3.14"
        hyperlink_end = "3.23"  # Adjust these indices as per the position of "σαρωτή" in your text
        self.tag_add("hyperlink", hyperlink_start, hyperlink_end)

        # Styling the hyperlink (blue color and underline)
        self.tag_configure("hyperlink", foreground="blue", underline=True)

        # Binding the left mouse button click to the hyperlink tag
        self.tag_bind("hyperlink", "<Button-1>", self.open_hyperlink_rollers)

        # Binding enter and leave events for the hyperlink
        self.tag_bind("hyperlink", "<Enter>", self.on_enter)
        self.tag_bind("hyperlink", "<Leave>", self.on_leave)

        self.configure(state="disabled")
        self.pack(expand=True, fill="both")

        self.monitoring = monitoring
        self.rollers_hyperlink_opened: Counter = get_meter("Autoscription").create_counter(
            name="info_message_shown", unit="1", description="Counts Number of Times Info Message is Shown"
        )

    def open_hyperlink_rollers(self, event: tk.Event[tk.Text]) -> None:  # noqa: [U100]
        self.rollers_hyperlink_opened.add(1)
        self.monitoring.logger_adapter.warning("Cleaning Banner Hyperlink opened")
        webbrowser.open_new("https://www.youtube.com/watch?v=VkCBLUouRvA")

    def on_enter(self, event: tk.Event[tk.Text]) -> None:  # noqa: [U100]
        self.config(cursor="hand2")

    def on_leave(self, event: tk.Event[tk.Text]) -> None:  # noqa: [U100]
        self.config(cursor="")
