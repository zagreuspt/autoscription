import pathlib
from typing import List

from pandas import DataFrame

from src.autoscription.gui.utils import get_prescriptions_for_manual_check


class TestApp:
    def test_get_prescriptions_to_check(self) -> None:
        # GIVEN
        columns: List[str] = [
            "prescription_scanned_pages",
            "stack_number",
            "coupon_check",
            "sign_check",
            "stamps_check",
        ]

        prescriptions: List[List[str]] = [
            ["abc", "2", "True", "False", "False"],
            ["bcd", "8", "False", "True", "False"],
            ["def", "12", "False", "False", "True"],
            ["efg", "21", "False", "False", "False"],
            ["efg", "21", "True", "True", "True"],
        ]

        pages_df = DataFrame(prescriptions, columns=columns)
        # WHEN
        manual_check = get_prescriptions_for_manual_check(pages_df=pages_df, scan_directory=pathlib.Path.cwd())
        # THEN
        assert len(prescriptions) <= len(pages_df)
        assert len(manual_check) == 4
        # TODO: check for dictionary key values
