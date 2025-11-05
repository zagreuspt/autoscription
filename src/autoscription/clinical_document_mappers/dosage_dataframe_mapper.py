from dataclasses import asdict, dataclass
from typing import List

from pandas import DataFrame, concat

from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    SubstanceAdministration,
)


@dataclass
class DosageEntry:
    boxes_required: str
    boxes_provided: str
    dosage_category: str
    dosage_description: str
    description: str
    pills_required: str
    description_quantity: str
    description_quantity_rule: str
    dosage: str
    dosage_qnt: str
    dosage_repeat: str
    patient_part: str
    unit_price: str
    patient_return: str
    total: str
    diff: str
    patient_contrib: str
    gov_contrib: str
    description_org: str
    dosage_check: str
    prescription: str
    scan_last_three_digits: str
    boxes_provided_multiple_executions: str
    is_past_partial_exec: str


def __map_to_dosages_entry(substance_administration: SubstanceAdministration, prescription_id: str) -> DosageEntry:
    # todo: calculate boxes_required, pills_required, dosage_check
    # TBC: To Be Calculated
    # TBF: To Be Filled
    return DosageEntry(
        boxes_required="TBC",
        boxes_provided="TBF",
        dosage_category="TBF",
        dosage_description="TBF",
        description=(
            substance_administration.consumable.name
            if substance_administration and substance_administration.consumable
            else "Not Found"
        ),
        pills_required="TBC",
        description_quantity=(
            substance_administration.consumable.container_packaged_medicine.capacity
            if substance_administration
            and substance_administration.consumable
            and substance_administration.consumable.container_packaged_medicine
            and substance_administration.consumable.container_packaged_medicine.capacity
            else "Not Found"
        ),
        description_quantity_rule="TBF",
        dosage=str(
            substance_administration.dose_quantity.high_value
            if substance_administration
            and substance_administration.dose_quantity
            and substance_administration.dose_quantity.high_value
            else "Not Found"
        ),
        dosage_qnt="TBF",
        dosage_repeat=str(
            substance_administration.rate_quantity.value
            if substance_administration
            and substance_administration.rate_quantity
            and substance_administration.rate_quantity.value
            else "Not Found"
        ),
        patient_part="TBF",
        unit_price="TBF",
        patient_return="TBF",
        total="TBF",
        diff="TBF",
        patient_contrib="TBF",
        gov_contrib="TBF",
        description_org="TBF",
        dosage_check="TBC",
        prescription=prescription_id,
        scan_last_three_digits="TBF",
        boxes_provided_multiple_executions="TBF",
        is_past_partial_exec="TBF",
    )


def __map_to_dosage_entries(clinical_document: ClinicalDocument) -> List[DosageEntry]:
    substance_administrations = clinical_document.section.substance_administrations
    return [__map_to_dosages_entry(s, clinical_document.barcode) for s in substance_administrations]


def map_to_dosage_dataframe(clinical_document: ClinicalDocument) -> DataFrame:
    return DataFrame.from_records(asdict(d) for d in __map_to_dosage_entries(clinical_document))


def map_to_dosages_dataframe_from_list(clinical_documents: List[ClinicalDocument]) -> DataFrame:
    dosage_dataframes = [map_to_dosage_dataframe(doc) for doc in clinical_documents]
    dosages_dataframe = concat(dosage_dataframes, axis=0)
    return dosages_dataframe
