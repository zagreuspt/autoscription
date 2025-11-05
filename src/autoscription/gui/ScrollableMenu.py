import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from typing import Any, Dict

import ttkthemes


class ScrollableMenu:
    commands: Dict[Any, Any]

    def __init__(self, parent: ttkthemes.ThemedTk) -> None:
        self.top = tk.Toplevel(parent)
        # Adjust size as needed
        self.width = 205
        self.height = 200
        self.top.geometry(f"{self.width}x{self.height}")
        menu_small_font = ("Arial", 8)
        self.scrollbar = ttk.Scrollbar(self.top)
        self.top.overrideredirect(True)
        self.listbox = tk.Listbox(
            self.top,
            yscrollcommand=self.scrollbar.set,
        )

        self.listbox.config(font=menu_small_font, bg="white")
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_columnconfigure(0, weight=9)
        self.top.grid_columnconfigure(1, weight=0)

        self.scrollbar.config(command=self.listbox.yview)
        self.top.bind("<FocusOut>", lambda e: self.top.withdraw())  # noqa: U100
        self.commands = {}
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def on_select(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: U100
        selected = self.listbox.curselection()  # type: ignore[no-untyped-call]
        if selected:
            index = selected[0]
            label = self.listbox.get(index)
            command = self.commands.get(label)
            if command:
                command()

    def add_command(self, label: Any, command: Any, report_file: Path) -> None:
        self.listbox.insert(tk.END, f"    {label}")
        self.commands[f"    {label}"] = lambda: command(report_file)

    def winfo_reqwidth(self) -> int:
        return self.top.winfo_reqwidth()

    def winfo_reqheight(self) -> int:
        return self.top.winfo_reqheight()

    def winfo_rootx(self) -> int:
        return self.top.winfo_rootx()

    def option_clear(self) -> None:
        self.listbox.option_clear()

    def hide(self) -> None:
        self.top.withdraw()

    def post(self, x: int, y: int) -> None:
        target_width = int(x + (self.width / 2) + (0.1 * self.width))
        target_height = int(y - (self.height / 5))
        self.top.geometry(f"+{target_width}+{target_height}")
        self.top.deiconify()
        self.top.focus_force()
