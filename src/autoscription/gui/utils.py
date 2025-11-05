from pathlib import Path
from tkinter import Event, Label, Toplevel, Widget
from typing import Any, Dict, List, TypeVar

from pandas import DataFrame

OPERATION_FAILED_MESSAGE = "Η διαδικασία απέτυχε."


# TODO: find out return type for pandas filter
def __page_needs_check_filter(pages: DataFrame) -> Any:
    return (pages["coupon_check"] == "False") | (pages["sign_check"] == "False") | (pages["stamps_check"] == "False")


def get_prescriptions_for_manual_check(pages_df: DataFrame, scan_directory: Path) -> List[Dict[str, Any]]:
    # TODO: change Dict to dataclass
    prescriptions = pages_df[__page_needs_check_filter(pages_df)][  # noqa: PD011
        [
            "prescription_scanned_pages",
            "stack_number",
            "coupon_check",
            "sign_check",
            "stamps_check",
            "missing_tapes",
            "surplus_tapes",
        ]
    ].values.tolist()
    return [
        {
            "image_path": (scan_directory / prescription[0]).as_posix(),
            "stack_number": prescription[1],
            "check_coupons": prescription[2],
            "check_signatures": prescription[3],
            "check_stamps": prescription[4],
            "missing_tapes": str(prescription[5]),
            "surplus_tapes": str(prescription[6]),
        }
        for prescription in prescriptions
        if isinstance(prescription[0], str)
    ]


T = TypeVar("T", bound=Widget)  # Define a type variable that is bound to Widget


def create_tooltip(widget: T, text: str) -> None:
    def enter(event: Event) -> None:  # type: ignore[type-arg] # noqa: U100
        x = y = 0
        x, y, _, _ = widget.bbox("insert")  # type: ignore[call-overload]
        x += widget.winfo_rootx() + 60
        y += widget.winfo_rooty() + 20

        # Dynamically add the tooltip attribute using setattr
        setattr(widget, "tooltip", Toplevel(widget))  # noqa: B010
        tooltip_widget = getattr(widget, "tooltip")  # noqa: B009
        tooltip_widget.wm_overrideredirect(True)
        tooltip_widget.wm_geometry(f"+{x}+{y}")

        label = Label(tooltip_widget, text=text, justify="left", background="#ffffff", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def leave(event: Event) -> None:  # type: ignore[type-arg] # noqa: U100
        if hasattr(widget, "tooltip"):
            tooltip_widget = getattr(widget, "tooltip")  # noqa: B009
            tooltip_widget.destroy()
            delattr(widget, "tooltip")  # Safely remove the dynamically added attribute

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
