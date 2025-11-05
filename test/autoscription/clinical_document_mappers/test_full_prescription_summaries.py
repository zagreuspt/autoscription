from unittest import mock

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from src.autoscription.clinical_document_mappers.full_prescriptions_summaries import (
    FullPrescriptionSummary,
    map_to_full_prescription_summary,
    map_to_full_summary_dataframe,
    map_to_full_summary_dataframe_from_list,
)
from src.autoscription.idika_client.model.mt.clinical_document.author import (
    AssignedAuthor,
    Author,
)
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Section,
    Summary,
)


class TestFullPrescriptionSummaries:
    def test_maps_single_clinical_document_to_full_prescription_summary_correctly(self):
        clinical_document = mock.create_autospec(ClinicalDocument, instance=True)
        clinical_document.author = mock.create_autospec(Author, instance=True)
        clinical_document.author.assigned_author = mock.create_autospec(AssignedAuthor, instance=True)
        clinical_document.section = mock.create_autospec(Section, instance=True)
        clinical_document.section.summary = mock.create_autospec(Summary, instance=True)
        clinical_document.author.assigned_author.doctor_specialty_id = "123"
        clinical_document.author.assigned_author.doctor_specialty_name = "Cardiology"
        clinical_document.barcode = "ABC123"
        clinical_document.section.summary.contains_desensitization_vaccine = True
        clinical_document.section.summary.medical_report_required = False

        expected_summary = FullPrescriptionSummary(
            prescription="ABC123",
            doctor_specialty_id="123",
            doctor_specialty_name="Cardiology",
            contains_desensitization_vaccine=True,
            medical_report_required=False,
        )

        result_summary = map_to_full_prescription_summary(clinical_document)

        assert result_summary == expected_summary

    def test_maps_list_of_clinical_documents_to_dataframe_correctly(self):
        clinical_documents = [
            mock.create_autospec(ClinicalDocument, instance=True),
            mock.create_autospec(ClinicalDocument, instance=True),
        ]
        clinical_documents[0].author = mock.create_autospec(Author, instance=True)
        clinical_documents[0].author.assigned_author = mock.create_autospec(AssignedAuthor, instance=True)
        clinical_documents[0].section = mock.create_autospec(Section, instance=True)
        clinical_documents[0].section.summary = mock.create_autospec(Summary, instance=True)

        clinical_documents[0].author.assigned_author.doctor_specialty_id = "123"
        clinical_documents[0].author.assigned_author.doctor_specialty_name = "Cardiology"
        clinical_documents[0].barcode = "ABC123"
        clinical_documents[0].section.summary.contains_desensitization_vaccine = True
        clinical_documents[0].section.summary.medical_report_required = False

        clinical_documents[1].author = mock.create_autospec(Author, instance=True)
        clinical_documents[1].author.assigned_author = mock.create_autospec(AssignedAuthor, instance=True)
        clinical_documents[1].section = mock.create_autospec(Section, instance=True)
        clinical_documents[1].section.summary = mock.create_autospec(Summary, instance=True)

        clinical_documents[1].author.assigned_author.doctor_specialty_id = "456"
        clinical_documents[1].author.assigned_author.doctor_specialty_name = "Neurology"
        clinical_documents[1].barcode = "DEF456"
        clinical_documents[1].section.summary.contains_desensitization_vaccine = False
        clinical_documents[1].section.summary.medical_report_required = True

        expected_dataframe = pd.DataFrame(
            {
                "prescription": ["ABC123", "DEF456"],
                "doctor_specialty_id": ["123", "456"],
                "doctor_specialty_name": ["Cardiology", "Neurology"],
                "contains_desensitization_vaccine": [True, False],
                "medical_report_required": [False, True],
            }
        )

        result_dataframe = map_to_full_summary_dataframe_from_list(clinical_documents)

        pd.testing.assert_frame_equal(
            result_dataframe.reset_index(drop=True), expected_dataframe.reset_index(drop=True)
        )

    def test_handles_empty_list_of_clinical_documents_without_errors(self):
        clinical_documents = []

        expected_dataframe = pd.DataFrame(
            columns=[
                "prescription",
                "doctor_specialty_id",
                "doctor_specialty_name",
                "contains_desensitization_vaccine",
                "medical_report_required",
            ]
        )

        result_dataframe = map_to_full_summary_dataframe_from_list(clinical_documents)

        pd.testing.assert_frame_equal(result_dataframe, expected_dataframe)

    def test_ensures_dataframe_creation_from_single_clinical_document(self):
        # Given a ClinicalDocument instance
        clinical_document = mock.create_autospec(ClinicalDocument, instance=True)
        clinical_document.author = mock.create_autospec(Author, instance=True)
        clinical_document.author.assigned_author = mock.create_autospec(AssignedAuthor, instance=True)
        clinical_document.section = mock.create_autospec(Section, instance=True)
        clinical_document.section.summary = mock.create_autospec(Summary, instance=True)
        clinical_document.author.assigned_author.doctor_specialty_id = "sp01"
        clinical_document.author.assigned_author.doctor_specialty_name = "Cardiology"
        clinical_document.barcode = "12345"
        clinical_document.section.summary.contains_desensitization_vaccine = True
        clinical_document.section.summary.medical_report_required = False
        # When mapping to a DataFrame
        df = map_to_full_summary_dataframe(clinical_document)
        # Then the DataFrame should have one row with the correct data
        expected_data = {
            "prescription": ["12345"],
            "doctor_specialty_id": ["sp01"],
            "doctor_specialty_name": ["Cardiology"],
            "contains_desensitization_vaccine": [True],
            "medical_report_required": [False],
        }

        expected_dtypes = pd.Series(
            {
                "prescription": "object",
                "doctor_specialty_id": "object",
                "doctor_specialty_name": "object",
                "contains_desensitization_vaccine": "bool",
                "medical_report_required": "bool",
            }
        )

        expected_df = pd.DataFrame(expected_data)
        assert_frame_equal(df.reset_index(drop=True), expected_df.reset_index(drop=True))
        assert_series_equal(df.dtypes, expected_dtypes)
