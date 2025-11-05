import pandas
from pandas import DataFrame
from pandas._testing import assert_frame_equal

from src.autoscription.core.report import calculate_daily_analytics


class TestDailyAnalytics:
    def test_daily_analytics_with_pharmacist_pages(self):
        # Setup
        pages_data = {
            "type": ["pharmacist", "pharmacist", "doctor"],
            "doc_name": ["Dr. Smith", "Dr. Mike", "Dr. Doe"],
            "category": [1.0, 8.0, 1.0],
            "pharmacist_idika_prescription_full": ["123", "456", "789"],
            "patient_amount": [100.0, 200.0, 300.0],
            "insurance_amount": [50.0, 150.0, 250.0],
            "prescription": ["123", "456", "789"],
            "prescription_scanned_pages": ["123", "456", "789"],
        }
        pages_df = DataFrame(pages_data)
        expected_top_5_doctors = DataFrame(
            {
                "Ονομ/νυμο Ιατρού": ["Dr. Mike", "Dr. Smith"],
                "Αριθμός συνταγών": [1, 1],
                "Συνολικό Ποσό": ["350.00 €", "150.00 €"],
                "Πληρωτέο ποσό (ταμείο)": ["150.00 €", "50.00 €"],
            }
        )

        # Act
        daily_analytics = calculate_daily_analytics(pages_df)

        # Assert
        assert_frame_equal(daily_analytics.top_5_doctors, expected_top_5_doctors)
        assert daily_analytics.total_amount == 500.0
        assert daily_analytics.total_insurance_amount == 200.0
        assert daily_analytics.total_patient_amount == 300.0
        assert daily_analytics.total_missing_insurance_amount == 0.0
        assert daily_analytics.total_eopyy_amount == 50.0
        assert daily_analytics.total_missing_eopyy_amount == 0.0
        assert daily_analytics.total_other_funds_amount == 150.0
        assert daily_analytics.total_missing_other_funds_amount == 0.0

    def test_daily_analytics_with_pharmacist_pages_exclude_non_doctor_prescriptions(self):
        # Setup
        pages_data = {
            "type": ["pharmacist", "pharmacist", "doctor"],
            "doc_name": ["Dr. Smith", None, "Dr. Doe"],
            "category": [2.0, 8.0, 1.0],
            "pharmacist_idika_prescription_full": ["123", "456", "789"],
            "patient_amount": [100.0, 200.0, 300.0],
            "insurance_amount": [50.0, 150.0, 250.0],
            "prescription": ["123", "456", "789"],
            "prescription_scanned_pages": ["123", "456", "789"],
        }
        pages_df = DataFrame(pages_data)
        expected_top_5_doctors = DataFrame(
            {
                "Ονομ/νυμο Ιατρού": ["Dr. Smith"],
                "Αριθμός συνταγών": [1],
                "Συνολικό Ποσό": ["150.00 €"],
                "Πληρωτέο ποσό (ταμείο)": ["50.00 €"],
            },
            index=[1],
        )
        # Act
        daily_analytics = calculate_daily_analytics(pages_df)

        # Assert
        assert_frame_equal(daily_analytics.top_5_doctors, expected_top_5_doctors)
        assert daily_analytics.total_amount == 500.0
        assert daily_analytics.total_insurance_amount == 200.0
        assert daily_analytics.total_patient_amount == 300.0
        assert daily_analytics.total_missing_insurance_amount == 0.0
        assert daily_analytics.total_eopyy_amount == 50.0
        assert daily_analytics.total_missing_eopyy_amount == 0.0
        assert daily_analytics.total_other_funds_amount == 150.0
        assert daily_analytics.total_missing_other_funds_amount == 0.0

    def test_daily_analytics_empty_dataframe(self):
        # Setup
        pages_df = DataFrame(
            columns=[
                "type",
                "doc_name",
                "category",
                "pharmacist_idika_prescription_full",
                "patient_amount",
                "insurance_amount",
                "prescription",
                "prescription_scanned_pages",
            ]
        )
        expected_top_5_doctors = DataFrame(
            columns=[
                "Ονομ/νυμο Ιατρού",
                "Αριθμός συνταγών",
                "Συνολικό Ποσό",
                "Πληρωτέο ποσό (ταμείο)",
            ],
            index=pandas.Int64Index([]),
        ).astype(
            {
                "Αριθμός συνταγών": "int64",
                "Συνολικό Ποσό": "float",
                "Πληρωτέο ποσό (ταμείο)": "float",
            }
        )

        # Act
        daily_analytics = calculate_daily_analytics(pages_df)

        # Assert
        assert_frame_equal(daily_analytics.top_5_doctors, expected_top_5_doctors)
        assert daily_analytics.total_amount == 0.0
        assert daily_analytics.total_insurance_amount == 0.0
        assert daily_analytics.total_patient_amount == 0.0
        assert daily_analytics.total_missing_insurance_amount == 0.0
        assert daily_analytics.total_eopyy_amount == 0.0
        assert daily_analytics.total_missing_eopyy_amount == 0.0
        assert daily_analytics.total_other_funds_amount == 0.0
        assert daily_analytics.total_missing_other_funds_amount == 0.0

    def test_daily_analytics_with_duplicate_pharmacist_idika_prescription_full(self):
        # Setup
        pages_data = {
            "type": ["pharmacist", "pharmacist", "doctor", "pharmacist"],
            "doc_name": ["Dr. Smith", "Dr. Smith", "Dr. Doe", "Dr. Smith"],
            "category": [1.0, 8.0, 1.0, 1.0],
            "pharmacist_idika_prescription_full": ["123", "123", "789", "123"],
            "patient_amount": [100.0, 100.0, 300.0, 100.0],
            "insurance_amount": [50.0, 50.0, 250.0, 50.0],
            "prescription": ["123", "456", "789", "123"],
            "prescription_scanned_pages": ["123", "456", "789", "123"],
        }
        pages_df = DataFrame(pages_data)
        expected_top_5_doctors = DataFrame(
            {
                "Ονομ/νυμο Ιατρού": ["Dr. Smith"],
                "Αριθμός συνταγών": [1],  # Assuming duplicates are counted as one
                "Συνολικό Ποσό": ["150.00 €"],
                "Πληρωτέο ποσό (ταμείο)": ["50.00 €"],
            }
        )

        # Act
        daily_analytics = calculate_daily_analytics(pages_df)

        # Assert
        assert_frame_equal(daily_analytics.top_5_doctors, expected_top_5_doctors)
        assert daily_analytics.total_amount == 150.0  # Adjusted for duplicates
        assert daily_analytics.total_insurance_amount == 50.0
        assert daily_analytics.total_patient_amount == 100.0
        assert daily_analytics.total_missing_insurance_amount == 0.0
        assert daily_analytics.total_eopyy_amount == 50.0
        assert daily_analytics.total_missing_eopyy_amount == 0.0
        assert daily_analytics.total_other_funds_amount == 0.0
        assert daily_analytics.total_missing_other_funds_amount == 0.0

    def test_daily_analytics_missing_amounts(self):
        # Setup
        pages_data = {
            "type": ["pharmacist", "pharmacist", "doctor", "pharmacist"],
            "doc_name": ["Dr. Smith", "Dr. Mike", "Dr. Doe", "Dr. Daniels"],
            "category": [1.0, 4.0, 5.0, 8.0],
            "pharmacist_idika_prescription_full": ["123", "456", "789", "012"],
            "patient_amount": [100.0, 200.0, 300.0, 400.0],
            "insurance_amount": [50.0, 150.0, 250.0, 350.0],
            "prescription": ["123", "456", "789", "012"],
            "prescription_scanned_pages": ["123", None, "789", None],
        }
        pages_df = DataFrame(pages_data)
        expected_top_5_doctors = DataFrame(
            {
                "Ονομ/νυμο Ιατρού": ["Dr. Daniels", "Dr. Mike", "Dr. Smith"],
                "Αριθμός συνταγών": [1, 1, 1],
                "Συνολικό Ποσό": ["750.00 €", "350.00 €", "150.00 €"],
                "Πληρωτέο ποσό (ταμείο)": ["350.00 €", "150.00 €", "50.00 €"],
            }
        )

        # Act
        daily_analytics = calculate_daily_analytics(pages_df)

        # Assert
        assert_frame_equal(daily_analytics.top_5_doctors, expected_top_5_doctors)
        assert daily_analytics.total_amount == 1250.0
        assert daily_analytics.total_insurance_amount == 550.0
        assert daily_analytics.total_patient_amount == 700.0
        assert daily_analytics.total_missing_insurance_amount == 500.0
        assert daily_analytics.total_eopyy_amount == 200.0
        assert daily_analytics.total_missing_eopyy_amount == 150.0
        assert daily_analytics.total_other_funds_amount == 350.0
        assert daily_analytics.total_missing_other_funds_amount == 350.0
