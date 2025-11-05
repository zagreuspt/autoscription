from datetime import date, datetime

import pandas as pd
import pytest

from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.report import get_prescriptions_amount


class TestGetPrescriptionsAmount:
    def test_get_prescriptions_amount(self):
        data = {
            "type": ["pharmacist", "doctor", "pharmacist", "pharmacist", "pharmacist"],
            "pr_order_timestamp": [datetime.now(), datetime.now(), datetime.now(), datetime.now(), datetime.now()],
            "stack_number": [1, 2, 3, 4, 5],
            "insurance_amount": [100.0, 200.0, 300.0, 300.0, 400.0],
            "patient_amount": [10.0, 20.0, 30.0, 30.0, 40.0],
            "doc_name": ["doc1", "doc2", "doc3", "doc3", "doc4"],
            "patient_name": ["patient1", "patient2", "patient3", "patient3", "patient4"],
            "page": [1.0, 1.0, 1.0, 2.0, 1.0],
            "prescription_scanned_pages": ["file1", "file2", "file3", "file4", "file5"],
            "pharmacist_idika_prescription_full": ["123", "456", "789", "789", "012"],
            "pdf_file_name": ["pdf1", "pdf2", "pdf3", "pdf3", "pdf4"],
        }
        pages = pd.DataFrame(data)

        monitoring = TestMonitoring()
        result = get_prescriptions_amount(pages, date.today(), monitoring)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "Αριθμός συνταγής" in result.columns
        assert "Ώρα Εκτέλεσης" in result.columns
        assert "Ονομ/νυμο Ιατρού" in result.columns
        assert "Ονομ/νυμο Ασθενούς" in result.columns
        assert "Θέση στοίβας" in result.columns
        assert "Πληρωτέο από Ταμείο" in result.columns

    def test_get_prescriptions_amount_ignore_duplicates(self):
        data = {
            "type": ["pharmacist", "doctor", "pharmacist", "pharmacist", "pharmacist", "pharmacist"],
            "pr_order_timestamp": [
                datetime.now(),
                datetime.now(),
                datetime.now(),
                datetime.now(),
                datetime.now(),
                datetime.now(),
            ],
            "stack_number": [1, 2, 3, 4, 5, 6],
            "insurance_amount": [100.0, 200.0, 300.0, 300.0, 400.0, 400.0],
            "patient_amount": [10.0, 20.0, 30.0, 30.0, 40.0, 40.0],
            "doc_name": ["doc1", "doc2", "doc3", "doc3", "doc4", "doc4"],
            "patient_name": ["patient1", "patient2", "patient3", "patient3", "patient4", "patient4"],
            "page": [1.0, 1.0, 1.0, 2.0, 1.0, 1.0],
            "prescription_scanned_pages": ["file1", "file2", "file3", "file4", "file5", "file6"],
            "pharmacist_idika_prescription_full": ["123", "456", "789", "789", "012", "012"],
            "pdf_file_name": ["pdf1", "pdf2", "pdf3", "pdf3", "pdf4", "pdf4"],
        }
        pages = pd.DataFrame(data)

        monitoring = TestMonitoring()
        result = get_prescriptions_amount(pages, date.today(), monitoring)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "Αριθμός συνταγής" in result.columns
        assert "Ώρα Εκτέλεσης" in result.columns
        assert "Ονομ/νυμο Ιατρού" in result.columns
        assert "Ονομ/νυμο Ασθενούς" in result.columns
        assert "Θέση στοίβας" in result.columns
        assert "Πληρωτέο από Ταμείο" in result.columns

    def test_get_prescriptions_amount_empty_dataframe(self):
        pages = pd.DataFrame()
        monitoring = TestMonitoring()
        with pytest.raises(KeyError):
            get_prescriptions_amount(pages, date.today(), monitoring)

    def test_get_prescriptions_amount_no_pharmacist(self):
        data = {
            "type": ["doctor", "doctor"],
            "pr_order_timestamp": [datetime.now(), datetime.now()],
            "stack_number": [1, 2],
            "insurance_amount": [100.0, 200.0],
            "patient_amount": [10.0, 20.0],
            "doc_name": ["doc1", "doc2"],
            "patient_name": ["patient1", "patient2"],
            "page": [1.0, 1.0],
            "prescription_scanned_pages": ["file1", "file2"],
            "pharmacist_idika_prescription_full": ["123", "456"],
            "pdf_file_name": ["pdf1", "pdf2"],
        }
        pages = pd.DataFrame(data)
        monitoring = TestMonitoring()
        result = get_prescriptions_amount(pages, date.today(), monitoring)
        assert result.empty

    def test_get_prescriptions_amount_null_timestamp(self):
        data = {
            "type": ["pharmacist", "pharmacist"],
            "pr_order_timestamp": [None, None],
            "stack_number": [1, 2],
            "insurance_amount": [100.0, 200.0],
            "patient_amount": [10.0, 20.0],
            "doc_name": ["doc1", "doc2"],
            "page": [1.0, 1.0],
            "prescription_scanned_pages": ["file1", "file2"],
            "pharmacist_idika_prescription_full": ["123", "456"],
            "pdf_file_name": ["pdf1", "pdf2"],
        }
        pages = pd.DataFrame(data)
        monitoring = TestMonitoring()
        with pytest.raises(AttributeError, match="^'NoneType' object has no attribute 'time'$"):
            get_prescriptions_amount(pages, date.today(), monitoring)

    def test_get_prescriptions_amount_null_amounts(self):
        data = {
            "type": ["pharmacist", "pharmacist"],
            "pr_order_timestamp": [datetime.now(), datetime.now()],
            "stack_number": [1, 2],
            "insurance_amount": [None, None],
            "patient_amount": [None, None],
            "doc_name": ["doc1", "doc2"],
            "patient_name": ["patient1", "patient2"],
            "page": [1.0, 1.0],
            "prescription_scanned_pages": ["file1", "file2"],
            "pharmacist_idika_prescription_full": ["123", "456"],
            "pdf_file_name": ["pdf1", "pdf2"],
        }
        pages = pd.DataFrame(data)
        monitoring = TestMonitoring()
        result = get_prescriptions_amount(pages, date.today(), monitoring)
        assert "Πληρωτέο από Ταμείο" in result.columns
        assert all(result["Πληρωτέο από Ταμείο"] == "-")
