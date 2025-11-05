from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    SubstanceAdministration,
)


@dataclass(frozen=True)
class Item:
    id: Optional[str]
    value: str | int  # TODO: investigate further


@dataclass(frozen=True)
class ObservationValue:
    code: Optional[str]
    code_system_name: Optional[str]
    display_name: Optional[str]


@dataclass
class Text:
    soci_info_hndgs: Optional[str]
    list_value: list[Item]


@dataclass(frozen=True)
class Observation:
    text: Optional[str]
    status_code: Optional[str]
    value: Optional[ObservationValue]


@dataclass(frozen=True)
class Summary:
    # prescription_id: str
    # prescription_type_1_typical_2_free: str
    # prescription_repetition_1_simple_3_3_months_4_4_months_5_5_months_6_6_months: str
    # sequence_of_repeated_prescription: str
    # barcode_of_first_initial_prescription_in_case_of_repetition: str
    # start_date_of_validity_for_repeated_prescription: str
    # repetition_period_in_case_of_repeated_prescription_1_30_days_2_28_days_3_60_days: str
    # prescribed_based_on_commercial_name_of_drug: str
    # prescription_reason_id_based_on_commercial_name: str
    # comments_reason_id_based_on_commercial_name: str
    # zero_participation_case_id: str
    medical_report_required: bool
    # AMKA_of_consultation_doctor: str
    # consultation_date: str
    # specialty_id_of_consultation_doctor: str
    # name_of_specialty_of_consultation_doctor: str
    # full_name_of_consultation_doctor: str
    # barcode_of_electronic_consultation: str
    # single_dose_1_yes_0_no: str
    contains_high_cost_drug: bool
    # heparin_drug: str
    # IFET_drug_entry: str
    contains_desensitization_vaccine: bool
    # Performed_only_by_EOPYY_pharmacy: str
    # Execution_of_prescriptions_of_a_specific_category_only_by_special_pharmacies_and_under_conditions: str
    # Contains_narcotic_substance: str
    # Category_of_narcotic_prescription: str
    # Registered_only_by_Hospitals: str
    # Special_Antibiotic: str
    # According_to_Law_3816: str
    # IFET: str
    # Approval_required_by_EOPYY_through_committee: str
    # Outside_EOPYY_Pharmaceutical_Expense: str
    # Execution_case: str
    # Number_of_prescription_executions: str
    # Active_prescriptions: str
    # Patient_insurer_participation_amount_for_zero_participation: str
    # Patient_insurer_participation_amount_with_10_percent_participation: str
    # Patient_insurer_participation_amount_with_25_percent_participation: str
    # Total_patient_participation_amount: str
    # Total_Reference_Price_Amount: str
    # Total_Insurer_Difference_Amount: str
    # Total_Difference_Amount: str
    # Total_Insured_Difference_Amount: str
    # Total_Insurer_Participation_Amount: str
    # Patient_participation_amount_for_zero_participation: str
    # Patient_participation_amount_with_10_percent_participation: str
    # Patient_participation_amount_with_25_percent_participation: str
    # Barcode_of_handwritten_prescription: str
    # Not_covered_by_insurance_fund: str
    # Burden_from_insurance_fund_Burden_1_Euro_Whether_the_prescription_is_burdened_or_not: str
    # Amount_of_Burden_from_insurance_fund_Burden_1_Euro: str
    # # TODO: further investigation is required on the following duplicate value
    # Burden_from_insurance_fund_Burden_1_Euro_Whether_the_prescription_is_burdened_or_not: str  # type: ignore[no-redef]  # noqa: E501
    # Indication_that_the_prescription_contains_vaccines_0_The_prescription_contains_drugs_1_The_prescription_contains_vaccines: str  # noqa: E501
    # Indication_whether_the_prescription_is_reserved_or_not_1_The_prescription_is_reserved_0_The_prescription_is_not_reserved: str  # noqa: E501
    # Indication_of_insured_participation_exemption_1_Yes_0_No: str
    # Reason_for_insured_participation_exemption: str
    # Indication_that_insurer_covers_supplementary_participation_of_insured_1_Yes_0_No: str
    # Total_amount_of_supplementary_coverage_of_insured_participation_by_insurer_TEAPASA: str
    # Total_amount_of_difference_covered_by_KYYAP: str
    # Indication_whether_the_prescription_contains_drugs_from_negative_list: str
    # Contains_antibiotic_drug: str
    # Prescription_with_Consumables_For_extension_0_The_prescription_contains_only_drugs: str
    # Visit_id: str
    # Indication_that_the_prescription_is_virtual: str
    # The_Prescription_contains_drugs_for_home_delivery: str
    # Patient_s_intention_desire_for_home_delivery_of_drugs_1_Yes_0_No: str
    #
    # status_code: Optional[str]
    # effective_time: Optional[EffectiveTime]  # common
    # comments: str
    # observations: list[Observation]


@dataclass(frozen=True)
class Section:
    barcode: Optional[str]
    text: Optional[Text]
    summary: Summary
    substance_administrations: list[SubstanceAdministration]
