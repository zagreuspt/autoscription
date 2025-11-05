from datetime import date
from pathlib import Path

import pytest

from src.autoscription.core.report import map_to_image_link


# Mock the Monitoring class to avoid actual logging during tests
class MockMonitoring:
    def __init__(self):
        self.logger_adapter = MockLoggerAdapter()


class MockLoggerAdapter:
    def __init__(self):
        self.warning_message = None

    def info(self, message):
        self.info = message

    def warning(self, message):
        self.warning_message = message


# # Mock the config.get_scan_dir function to return a known path
def mock_get_scan_dir(run_date):
    return Path("/mock/scan/dir")


def mock_get_download_dir(run_date):
    return Path("/mock/download/dir")


# # Mock the Path.exists method to return True or False based on the file_name
def mock_path_exists(file_name):
    return file_name == Path("/mock/scan/dir/scan.jpg")


# Mock the Path.as_posix method to return a string representation of the path
def mock_path_as_posix(path):
    return str(path)


def mock_pd_isna(file):
    return True


def mock_glob(file):
    return ["pdf_file.pdf"]


# # Patch the functions and classes used in map_to_image_link
@pytest.fixture
def mock_config_existing_scan(monkeypatch):
    monkeypatch.setattr("src.autoscription.core.config.get_scan_dir", mock_get_scan_dir)
    monkeypatch.setattr("pathlib.Path.exists", mock_path_exists)
    monkeypatch.setattr("pathlib.Path.as_posix", mock_path_as_posix)


@pytest.fixture
def mock_config_existing_pdf(monkeypatch):
    monkeypatch.setattr("src.autoscription.core.config.get_download_dir", mock_get_download_dir)
    monkeypatch.setattr("glob.glob", mock_glob)
    monkeypatch.setattr("pandas.isna", mock_pd_isna)


class TestMapImageToLink:
    # Test cases
    def test_map_to_image_link_existing_scan(self, mock_config_existing_scan):
        monitoring = MockMonitoring()
        result = map_to_image_link(
            "scan.jpg",
            "pdf_file.pdf",
            "prescription_123",
            date.today(),
            monitoring,
        ).replace("\\", "/")
        assert result == '<a href="/mock/scan/dir/scan.jpg">prescription_123</a>'

    def test_map_to_image_link_existing_pdf(self, mock_config_existing_pdf):
        monitoring = MockMonitoring()
        result = map_to_image_link(
            "scan.jpg",
            "pdf_file.pdf",
            "prescription_123",
            date.today(),
            monitoring,
        )
        assert result == '<a href="/mock/download/dir/pdf_file.pdf">prescription_123</a>'

    def test_map_to_image_link_nan_file_name(self):
        monitoring = MockMonitoring()
        result = map_to_image_link(None, "pdf_file.pdf", "prescription_123", date.today(), monitoring)
        assert result == "prescription_123"
        assert monitoring.logger_adapter.warning_message == "prescription_123:map_to_image_link: file_name not found"
