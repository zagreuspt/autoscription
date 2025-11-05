from test.autoscription.clinical_document_mappers.fixtures import *
from typing import List

import pandas
from pandas import DataFrame

from src.autoscription.clinical_document_mappers.dosage_dataframe_mapper import (
    DosageEntry,
)
from src.autoscription.clinical_document_mappers.dosage_dataframe_mapper import (
    __map_to_dosage_entries as map_to_dosage_entries,
)
from src.autoscription.clinical_document_mappers.dosage_dataframe_mapper import (
    map_to_dosage_dataframe,
)
from src.autoscription.idika_client.model.mt.clinical_document.author import (
    AssignedAuthor,
    Author,
)
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.clinical_document.common import (
    EffectiveTime,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Section,
    Summary,
)


class TestDosageDataframeMapper:
    def test_mapping_dosages_file_entries(self, substance_administration_1, substance_administration_2):
        substance_administrations = [
            substance_administration_1,
            substance_administration_2,
        ]
        clinical_document = ClinicalDocument(
            barcode="test",
            effective_time=EffectiveTime("a", "b"),
            patient_role=None,
            author=Author(
                assigned_author=AssignedAuthor(
                    doctor_id=None,
                    doctor_amka=None,
                    doctor_specialty_id="15",
                    doctor_specialty_name="test",
                    doctor_etee=None,
                    telecom=None,
                    given_name=None,
                    family_name=None,
                    represented_organization=None,
                ),
                time=None,
            ),
            custodian=None,
            legal_authenticator=None,
            doctor_visit=None,
            section=Section(
                substance_administrations=substance_administrations,
                barcode="",
                text=None,
                summary=Summary(
                    contains_high_cost_drug=False, contains_desensitization_vaccine=True, medical_report_required=False
                ),
            ),
        )
        dosage_entries: List[DosageEntry] = map_to_dosage_entries(clinical_document)
        pandas.DataFrame(dosage_entries)

    def test_map_to_dosage_dataframe(self, clinical_document):
        expected_columns = [
            "boxes_required",
            "boxes_provided",
            "dosage_category",
            "dosage_description",
            "description",
            "pills_required",
            "description_quantity",
            "description_quantity_rule",
            "dosage",
            "dosage_qnt",
            "dosage_repeat",
            "patient_part",
            "unit_price",
            "patient_return",
            "total",
            "diff",
            "patient_contrib",
            "gov_contrib",
            "description_org",
            "dosage_check",
            "prescription",
            "scan_last_three_digits",
            "boxes_provided_multiple_executions",
            "is_past_partial_exec",
        ]
        expected_values = [
            [
                "TBC",
                "TBF",
                "TBF",
                "TBF",
                "Sample Medicine",
                "TBC",
                "10",
                "TBF",
                "20",
                "TBF",
                "5",
                "TBF",
                "TBF",
                "TBF",
                "TBF",
                "TBF",
                "TBF",
                "TBF",
                "TBF",
                "TBC",
                "987654321",
                "TBF",
                "TBF",
                "TBF",
            ]
        ]

        result_df = map_to_dosage_dataframe(clinical_document=clinical_document)

        assert isinstance(result_df, DataFrame)
        assert result_df.columns.tolist() == expected_columns
        assert result_df.values.tolist() == expected_values
