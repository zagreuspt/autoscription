from dataclasses import asdict, dataclass
from typing import List

from pandas import DataFrame, concat

from src.autoscription.idika_client.model.mt.partial_clinical_document import (
    PartialClinicalDocument,
)


@dataclass(frozen=True)
class PartialPrescriptionSummary:
    prescription: str
    execution: int
    contains_high_cost_drug_above_limit: bool
    retail_prices: str
    authenticity_tapes: List[str]


def contains_high_cost_drug_above_limit(
    partial_clinical_document: PartialClinicalDocument, high_cost_drug_limit: float
) -> bool:
    for ps in partial_clinical_document.product_supplies:
        if ps.execution_details.retail_price is None:
            return False
        if ps.execution_details.retail_price > high_cost_drug_limit:
            return True
    return False


def __map_to_partial_prescription_summary(
    partial_clinical_document: PartialClinicalDocument, high_cost_drug_limit: float
) -> PartialPrescriptionSummary:
    return PartialPrescriptionSummary(
        prescription=partial_clinical_document.barcode,
        execution=partial_clinical_document.execution,
        contains_high_cost_drug_above_limit=contains_high_cost_drug_above_limit(
            partial_clinical_document=partial_clinical_document, high_cost_drug_limit=high_cost_drug_limit
        ),
        retail_prices=" ".join(
            [
                str(ps.execution_details.retail_price)
                for ps in partial_clinical_document.product_supplies
                if ps.execution_details.retail_price
            ]
        ),
        authenticity_tapes=[
            tape  # Extract individual strings
            for product_supply in partial_clinical_document.product_supplies
            if product_supply.execution_details.authenticity_tape  # Ensure it's not empty
            for tape in product_supply.execution_details.authenticity_tape  # Flatten the list
        ],
    )


def map_to_partial_prescription_summary_dataframe(
    partial_clinical_document: PartialClinicalDocument, high_cost_drug_limit: float
) -> DataFrame:
    return DataFrame.from_records(
        [
            asdict(
                __map_to_partial_prescription_summary(
                    partial_clinical_document, high_cost_drug_limit=high_cost_drug_limit
                )
            )
        ]
    )


def map_to_partial_prescription_summaries_dataframe_from_list(
    partial_clinical_documents: List[PartialClinicalDocument], high_cost_drug_limit: float
) -> DataFrame:
    if not partial_clinical_documents:
        return DataFrame([])
    prescription_details_dataframes = [
        map_to_partial_prescription_summary_dataframe(
            partial_clinical_document, high_cost_drug_limit=high_cost_drug_limit
        )
        for partial_clinical_document in partial_clinical_documents
    ]

    prescription_details_dataframe = concat(prescription_details_dataframes, axis=0)
    return prescription_details_dataframe
