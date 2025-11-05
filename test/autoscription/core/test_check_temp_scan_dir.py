from unittest.mock import Mock

import pytest

from src.autoscription.core.core import Core
from src.autoscription.core.errors import FewScansException, WrongDayException
from src.autoscription.core.logging import TestMonitoring


class TestCheckTempScanDir:
    def test_check_temp_scan_dir_correct_day(self):
        # list similarity <0.5
        prescription_values = ["a", "b", "c", "d", "e"]
        scan_pres_ids = ["c", "d", "e", "f", "g", "h"]

        with pytest.raises(WrongDayException):
            core = Core(monitoring=TestMonitoring())
            core.check_temp_scan_dir(Mock(), prescription_values, scan_pres_ids, username="test_user")

    def test_check_temp_scan_dir_few_scans(self):
        # list similarity <0.6
        prescription_values = ["a", "b", "c", "d", "e"]
        scan_pres_ids = ["a", "b"]

        with pytest.raises(FewScansException):
            core = Core(monitoring=TestMonitoring())
            core.check_temp_scan_dir(Mock(), prescription_values, scan_pres_ids, username="test_user")

    def test_check_temp_scan_dir_all_correct(self):
        prescription_values = ["a", "b", "c", "d", "e"]
        scan_pres_ids = ["a", "b", "c", "d", "e"]

        core = Core(monitoring=TestMonitoring())
        core.check_temp_scan_dir(Mock(), prescription_values, scan_pres_ids, username="test_user")
