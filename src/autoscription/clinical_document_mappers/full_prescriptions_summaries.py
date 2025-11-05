from dataclasses import asdict, dataclass
from typing import List

from pandas import DataFrame, concat

from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)


@dataclass(frozen=True)
class FullPrescriptionSummary:
    prescription: str
    doctor_specialty_id: str
    doctor_specialty_name: str
    contains_desensitization_vaccine: bool
    medical_report_required: bool
    authenticity_tapes: List[str]


def map_to_full_prescription_summary(clinical_document: ClinicalDocument) -> FullPrescriptionSummary:
    return FullPrescriptionSummary(
        doctor_specialty_id=clinical_document.author.assigned_author.doctor_specialty_id,
        doctor_specialty_name=clinical_document.author.assigned_author.doctor_specialty_name,
        prescription=clinical_document.barcode,
        contains_desensitization_vaccine=clinical_document.section.summary.contains_desensitization_vaccine,
        medical_report_required=clinical_document.section.summary.medical_report_required,
        authenticity_tapes=[
            tape  # type: ignore[union-attr]
            for substance_administration in clinical_document.section.substance_administrations
            if substance_administration.execution_details.authenticity_tape  # type: ignore[union-attr]
            for tape in substance_administration.execution_details.authenticity_tape  # type: ignore[union-attr]
        ],
    )


def map_to_full_summary_dataframe(clinical_document: ClinicalDocument) -> DataFrame:
    return DataFrame.from_records([asdict(map_to_full_prescription_summary(clinical_document))])


def map_to_full_summary_dataframe_from_list(clinical_documents: List[ClinicalDocument]) -> DataFrame:
    summary_dataframes = [map_to_full_summary_dataframe(doc) for doc in clinical_documents]
    if len(summary_dataframes) == 0:
        return DataFrame(
            columns=[
                "prescription",
                "doctor_specialty_id",
                "doctor_specialty_name",
                "contains_desensitization_vaccine",
                "medical_report_required",
                "authenticity_tapes",
            ]
        )
    summaries_dataframe = concat(summary_dataframes, axis=0)
    return summaries_dataframe
