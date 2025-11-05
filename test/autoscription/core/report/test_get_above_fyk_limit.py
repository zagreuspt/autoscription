import datetime

import pandas as pd

from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.report import get_above_fyk_limit


class TestGetAboveFykLimit:
    def test_should_return_dataframe_when_high_cost_drug_above_limit_is_true(self):
        pages = pd.DataFrame(
            {
                "prescription": ["123", "456", "789"],
                "execution": ["1", "2", "3"],
                "other_columns": ["data1", "data2", "data3"],
                "stack_number": ["12", "15", "28"],
                "patient_name": ["John Doe", "Jane Doe", "John Smith"],
                "prescription_scanned_pages": ["file1", "file2", "file3"],
                "pdf_file_name": ["file1.pdf", "file2.pdf", "file3.pdf"],
                "type": ["doctor", "pharmacist", "doctor"],
                "pharmacist_idika_prescription_full": ["123452", "456522", "789532"],
                "doc_name": ["doc1", "doc2", "doc3"],
                "pr_order_timestamp": ["2024-03-27 12:09:56", "2024-03-27 12:10:56", "2024-03-27 12:11:56"],
            }
        )
        pages["pr_order_timestamp"] = pd.to_datetime(pages["pr_order_timestamp"])

        partial_prescription_summaries = pd.DataFrame(
            {
                "prescription": ["123", "456"],
                "execution": ["1", "2"],
                "contains_high_cost_drug_above_limit": [False, True],
            }
        )

        result = get_above_fyk_limit(pages, partial_prescription_summaries, datetime.date.today(), TestMonitoring())

        assert len(result) == 1
        assert result.columns.tolist() == [
            "Αριθμός συνταγής",
            "Θέση στοίβας",
            "Ονομ/νυμο Ασθενούς",
            "Ονομ/νυμο Ιατρού",
            "Ώρα Εκτέλεσης",
        ]
        assert result["Αριθμός συνταγής"][0] == "456522"
        assert result["Θέση στοίβας"][0] == "15"
        assert result["Ονομ/νυμο Ασθενούς"][0] == "Jane Doe"
        assert result["Ονομ/νυμο Ιατρού"][0] == "doc2"
        assert result["Ώρα Εκτέλεσης"][0] == datetime.time(12, 10, 56)

    def test_should_return_empty_dataframe_when_no_high_cost_drug_above_limit(self):
        pages = pd.DataFrame(
            {
                "prescription": ["123", "456", "789"],
                "execution": ["1", "2", "3"],
                "other_columns": ["data1", "data2", "data3"],
                "stack_number": ["12", "15", "28"],
                "patient_name": ["John Doe", "Jane Doe", "John Smith"],
                "prescription_scanned_pages": ["file1", "file2", "file3"],
                "pharmacist_idika_prescription_full": ["123452", "456522", "789532"],
                "doc_name": ["doc1", "doc2", "doc3"],
                "pr_order_timestamp": ["2024-03-27 12:09:56", "2024-03-27 12:10:56", "2024-03-27 12:11:56"],
            }
        )
        pages["pr_order_timestamp"] = pd.to_datetime(pages["pr_order_timestamp"])

        partial_prescription_summaries = pd.DataFrame(
            {
                "prescription": ["123", "456"],
                "execution": ["1", "2"],
                "contains_high_cost_drug_above_limit": [False, False],
            }
        )

        result = get_above_fyk_limit(pages, partial_prescription_summaries, datetime.date.today(), TestMonitoring())

        assert len(result) == 0
