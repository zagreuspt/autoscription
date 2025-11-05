import datetime
from pathlib import Path
from unittest.mock import Mock

import time_machine
from pytest_mock import MockerFixture

from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.utils import get_barcode_ocr


class TestGetBarcodeOCR:
    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_not_start_by_valid_year(self, mocker: MockerFixture) -> None:
        reader_result = ["9" * 16]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "0000000000000000"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_not_start_by_valid_year_after_2020(self, mocker: MockerFixture) -> None:
        reader_result = ["1" * 16]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "0000000000000000"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_start_by_valid_date_but_has_length_more_than_16(self, mocker: MockerFixture) -> None:
        reader_result = ["230512" + ("1" * 16)]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "0000000000000000"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_start_by_current_year(self, mocker: MockerFixture) -> None:
        reader_result = ["230512" + ("1" * 10)]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "2305121111111111"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_not_start_by_valid_year_has_length_16(self, mocker: MockerFixture) -> None:
        reader_result = ["230512" + ("1" * 10)]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "2305121111111111"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_bc_does_not_start_by_valid_year_length_13_no_following_value(self, mocker: MockerFixture) -> None:
        reader_result = ["230512" + ("1" * 7)]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "0000000000000000"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_barcode_does_not_start_by_valid_length_13_has_following_value(self, mocker: MockerFixture) -> None:
        reader_result = ["230512" + ("1" * 7), "123"]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "2305121111111123"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_bc_does_not_start_by_valid_length_13_has_following_value_with_wrong_length(
        self, mocker: MockerFixture
    ) -> None:
        reader_result = ["230512" + ("1" * 7), "1234"]
        mock_reader = Mock()
        mock_reader.readtext.return_value = reader_result
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert len(result) == 16
        assert result == "0000000000000000"

    @time_machine.travel(datetime.date(2023, 1, 1))
    def test_process_image_output_with_no_barcode(self, mocker: MockerFixture) -> None:
        mock_reader = Mock()
        mock_reader.readtext.return_value = []
        mocker.patch("PIL.Image.open", return_value=Mock())

        result, _ = get_barcode_ocr(file=Path(), reader=mock_reader, monitoring=TestMonitoring())

        assert result == "0000000000000000"
