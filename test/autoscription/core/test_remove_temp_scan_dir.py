import os
import shutil

import pytest
from pytest_mock import MockerFixture

from src.autoscription.core.core import get_temp_scan_dir, remove_temp_scan_dir


class TestRemoveTempScanDir:
    def test_remove_temp_scan_dir_removes_directory(self, mocker: MockerFixture):
        temp_dir = get_temp_scan_dir()

        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=True)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_temp_scan_dir()

        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        shutil.rmtree.assert_called_once_with(temp_dir)

    def test_remove_temp_scan_dir_does_not_raise_exception_when_directory_not_exists(self, mocker: MockerFixture):
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=False)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_temp_scan_dir()

        shutil.rmtree.assert_not_called()

    def test_remove_temp_scan_dir_does_not_raise_exception_when_is_not_a_directory(self, mocker: MockerFixture):
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=False)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_temp_scan_dir()

        shutil.rmtree.assert_not_called()

    def test_remove_temp_scan_dir_does_not_remove_non_empty_directory(self, mocker: MockerFixture):
        temp_dir = get_temp_scan_dir()

        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=True)
        mocker.patch("src.autoscription.core.core.shutil.rmtree", side_effect=OSError("Mocked OSError"))

        with pytest.raises(OSError):
            remove_temp_scan_dir()

        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        shutil.rmtree.assert_called_once_with(temp_dir)
