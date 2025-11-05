import pytest

from src.autoscription.core.extract_metadata import generate_dosage_check


class TestGenerateDosageCheck:
    @pytest.mark.parametrize(
        "boxes_provided, boxes_required, dosage, dosage_qnt, expected_result",
        [
            (10.0, 10, 1, 1, "True"),  # Exact provided boxes
            (8.0, 10, 1, 1, "CHECK"),  # Insufficient provided boxes
            (12.0, 10, 1, 1, "False"),  # Excess provided boxes
            # TODO: make it integer
            (8.5, 10, 1, 1, "CHECK"),  # Provided boxes as a fraction
            ("abc", 10, 1, 1, "False"),  # Invalid input for boxes_provided
            (8.0, 10, 1, 999, "True"),  # Extremely large dosage quantity
            (8.0, 10, 999, 1, "False"),  # Extremely large dosage
            (8.0, 10, 0, 1, "False"),  # Zero dosage
            (10.0, 10, 1, 1, "True"),  # Equal provided and required boxes
            (1000.0, 10, 1, 1, "False"),  # large_provided_boxes
            (8.0, 10000, 1, 1, "CHECK"),  # large_required_boxes,
            (8.0, 0, 1, 1, "False"),  # zero_boxes_required
            (1.0, 0, 1, 1, "True"),  # zero_boxes_required
        ],
    )
    def test_generate_dosage_check(self, boxes_provided, boxes_required, dosage, dosage_qnt, expected_result):
        assert generate_dosage_check(boxes_provided, boxes_required, dosage, dosage_qnt) == expected_result
