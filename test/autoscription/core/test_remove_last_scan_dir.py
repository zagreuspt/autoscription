import os
import shutil
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.autoscription.core.core import remove_last_scan_dir


class TestRemoveLastScanDir:
    def test_remove_last_scan_dir_removes_directory(self, mocker: MockerFixture):
        temp_dir = "/tmp/test"
        path = Path(temp_dir)

        mocker.patch("src.autoscription.core.core.pathlib.Path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.pathlib.Path.is_dir", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=True)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_last_scan_dir(path)

        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        shutil.rmtree.assert_called_once_with(path)

    def test_remove_temp_scan_dir_does_not_raise_exception_when_directory_not_exists(self, mocker: MockerFixture):
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=False)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_last_scan_dir(Path("/tmp/test"))

        shutil.rmtree.assert_not_called()

    def test_remove_temp_scan_dir_does_not_raise_exception_when_is_not_a_directory(self, mocker: MockerFixture):
        mocker.patch("src.autoscription.core.core.pathlib.Path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=False)
        mocker.patch("src.autoscription.core.core.pathlib.Path.is_dir", return_value=False)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")

        remove_last_scan_dir(Path())

        shutil.rmtree.assert_not_called()

    def test_remove_temp_scan_dir_does_not_remove_non_empty_directory(self, mocker: MockerFixture):
        temp_dir = "/tmp/test"
        path = Path(temp_dir)

        mocker.patch("src.autoscription.core.core.pathlib.Path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.exists", return_value=True)
        mocker.patch("src.autoscription.core.core.pathlib.Path.is_dir", return_value=True)
        mocker.patch("src.autoscription.core.core.os.path.isdir", return_value=True)
        mocker.patch("src.autoscription.core.core.shutil.rmtree")
        mocker.patch(
            "src.autoscription.core.core.shutil.rmtree",
            side_effect=OSError("Mocked OSError"),
        )

        with pytest.raises(OSError):
            remove_last_scan_dir(path)

        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        shutil.rmtree.assert_called_once_with(path)
