from datetime import date, datetime

import pandas as pd
from pandas._testing import assert_frame_equal

from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.report import (
    get_prescriptions_no_specialty_doctor_above_limit,
)


class TestGetPrescriptionsNoSpecialtyDoctorAboveLimit:
    def test_prescriptions_no_specialty_doctor_above_limit_happy_path(self):
        # Mocking the input data
        now = datetime(2023, 11, 3, 18, 14, 17)
        pages = pd.DataFrame(
            {
                "type": ["pharmacist", "pharmacist", "doctor"],
                "prescription": [1, 2, 3],
                "pr_order_timestamp": [now, now + pd.Timedelta("1 minutes"), now + pd.Timedelta("2 minutes")],
                "prescription_scanned_pages": ["file1", "file2", "file3"],
                "pdf_file_name": ["pdf1", "pdf2", "pdf3"],
                "page": [1.0, 1.0, 2.0],
                "pharmacist_idika_prescription_full": ["file12", "file22", "file32"],
                "stack_number": [1, 2, 3],
                "doc_name": ["doc1", "doc2", "doc3"],
                "patient_name": ["patient1", "patient2", "patient3"],
                "execution": [3, 2, 1],
            }
        )

        dosages = pd.DataFrame(
            {
                "prescription": [1, 2],
                "boxes_provided_multiple_executions": [2.0, 1.0],
                "scan_last_three_digits": ["123", "456"],
            }
        )

        full_prescription_summaries = pd.DataFrame(
            {"prescription": [1, 2, 3], "doctor_specialty_id": ["49", "50", "49"]}
        )

        run_date = date.today()

        # Expected output
        expected_output = pd.DataFrame(
            {
                "Αριθμός συνταγής": ["file12"],
                "Θέση στοίβας": [1],
                "Ονομ/νυμο Ασθενούς": ["patient1"],
                "Ονομ/νυμο Ιατρού": ["doc1"],
                "Ώρα Εκτέλεσης": [now.time()],
            }
        )

        # Call the function with the mocked data
        result = get_prescriptions_no_specialty_doctor_above_limit(
            pages, dosages, full_prescription_summaries, run_date, TestMonitoring()
        )

        # Assert that the result is as expected
        assert_frame_equal(result, expected_output)
