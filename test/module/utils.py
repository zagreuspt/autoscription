import datetime

import numpy as np
from pandas import DataFrame
from pandas.io.formats.style import Styler
from schema import Schema

default_pages_dict = {
    "prescription_scanned_pages": {0: "2305161169869_001.jpg"},  #
    "pdf_file_name": {0: "2305161169869_1.pdf"},
    "execution": {0: 1.0},
    "pharmacist_idika_prescription_full": {0: 2305161169869120.0},
    "prescription": {0: 2305161169869.0},
    "scan_last_three_digits": {0: 100.0},
    "type": {0: "pharmacist"},  #
    "page": {0: 1.0},
    "pages": {0: 1.0},
    "first_execution": {0: True},
    "digital": {0: True},
    "unit": {0: "East Mariaside"},
    "category": {0: 8.0},
    "category_name": {0: "South Stevenside"},
    "100%": {0: False},
    "doc_name": {0: "Barbara Payne"},
    "patient_name": {0: "Christopher Smith"},
    "pr_order_timestamp": {0: "2023-11-03 19:04:55"},
    "stack_number": {0: None},
    "sign_found": {0: 0.0},
    "sign_required": {0: 0.0},
    "sign_check": {0: True},
    "stamps_found": {0: 0.0},
    "stamps_required": {0: 0.0},
    "stamps_check": {0: np.nan},
    "dosage_check": {0: np.nan},
    "coupons_found": {0: 0.0},
    "coupons_required": {0: 0.0},
    "coupon_check": {0: np.nan},
    "coupon_precheck": {0: np.nan},
    "hospital_medicine": {0: np.nan},  #
    "document_type": {0: "prescription"},
    "manual_check": {0: np.nan},
    "insurance_amount": {0: np.nan},
    "patient_amount": {0: np.nan},
}

default_dosages_dict = {
    "boxes_required": {0: 3},
    "boxes_provided": {0: 3.0},
    "dosage_category": {0: "ΦΑΚΕΛΑΚΙ"},
    "dosage_description": {0: " 1 ΦΑΚΕΛΑΚΙ x 1 φορά την ημέρα x 30 ημέρες"},
    "description": {0: "B-MAG EFF.GRAN 243MG/SACHET BTX 10 SACHETS"},
    "pills_required": {0: 30.0},
    "description_quantity": {0: 10.0},
    "dosage": {0: 1.0},
    "dosage_qnt": {0: 1.0},
    "dosage_repeat": {0: 30},
    "patient_part": {0: "25%"},
    "unit_price": {0: 8.2},
    "patient_return": {0: 8.2},
    "total": {0: 24.6},
    "diff": {0: 0.0},
    "patient_contrib": {0: 6.15},
    "gov_contrib": {0: 18.45},
    "description_org": {0: "B-MAG EFF.GRAN 243MG/SACHET BTX 10 SACHETS (Γενόσημο)  "},
    "dosage_check": {0: "True"},
    "prescription": {0: 2305161169869},
    "scan_last_three_digits": {0: 120},
    "boxes_provided_multiple_executions": {0: 3.0},
    "hospital_medicine": {0: np.nan},
    "is_past_partial_exec": {0: False},
}

default_partial_prescription_summaries = {
    "prescription": {0: "2305161169869"},  #
    "execution": {0: 1},
    "contains_high_cost_drug_above_limit": {0: False},
}

default_full_prescription_summaries = {
    "prescription": {0: "2305161169869"},  #
    "doctor_specialty_id": {0: "49"},
    "doctor_specialty_name": {0: "ΑΝΕΥ"},
    "medical_report_required": {0: True},
    "contains_desensitization_vaccine": {0: False},
}

report_data_schema = Schema(
    {
        "config_show_overview": bool,
        "config_category_breakdown": bool,
        "config_execution_time_ordering": bool,
        "date": datetime.date,
        "scanned_docs": int,
        "prescriptions_full_idika": int,
        "prescriptions_full_idika_cat1": int,
        "prescriptions_docs": int,
        "digital_prescriptions": int,
        "digital_prescriptions_docs": int,
        "category_1_pres": int,
        "category_1_docs": int,
        "category_2_pres": int,
        "category_2_docs": int,
        "category_3_pres": int,
        "category_3_docs": int,
        "category_4_pres": int,
        "category_4_docs": int,
        "category_8_pres": int,
        "category_8_docs": int,
        "hundred_perc_pres": int,
        "hundred_perc_docs": int,
        "vaccines_pres": int,
        "missing_pharm_prescriptions": DataFrame,
        "missing_pharm_presciptions_existing_doc": DataFrame,
        "missing_doctor_prescriptions": DataFrame,
        "missing_doc_prescriptions_existing_pharm": DataFrame,
        "pharmacist_missing_pages": DataFrame,
        "remove_docs": DataFrame,
        "dosage_check": DataFrame,
        "not_in_idika_scans_df": DataFrame,
        "manual_check": DataFrame,
        "not_detected_barcodes": DataFrame,
        "daily_analytics": DataFrame,
        "total_revenue_value": float,
        "total_revenue": str,
        "total_gov_contribution_value": float,
        "total_gov_contribution": str,
        "total_patient_contribution_value": float,
        "total_patient_contribution": str,
        "total_missing_insurance_amount_value": float,
        "total_missing_insurance_amount": str,
        "total_eopyy_amount_value": float,
        "total_eopyy_amount": str,
        "total_other_funds_amount_value": float,
        "total_other_funds_amount": str,
        "total_missing_other_funds_amount_value": float,
        "total_missing_other_funds_amount": str,
        "total_missing_eopyy_amount_value": float,
        "total_missing_eopyy_amount": str,
        "min_moves": int,
        "execution_time_ordering_df": DataFrame,
        "all_prescriptions_df": Styler,
        "all_prescriptions_df_current_index": Styler,
        "injections_min_moves": int,
        "injections_execution_time_ordering_df": DataFrame,
        "injections_prescriptions_df": Styler,
        "injections_prescriptions_df_current_index": Styler,
        "get_category_2_df": DataFrame,
        "get_100_percent_documents_df": DataFrame,
        "get_other_documents_df": DataFrame,
        "get_digital_doctor_documents_df": DataFrame,
        "missing_pharm_prescriptions_ekaa_check": bool,
        "remove_docs_ekaa_check": bool,
        "fyk_limit": str,
        "above_fyk_limit": DataFrame,
        "prescriptions_amount": DataFrame,
        "no_specialty_doctors": DataFrame,
        "medical_report_prescriptions": DataFrame,
        "desensitization_prescriptions": DataFrame,
    }
)


def extract_part_from_column(df, col_name: str):
    """
    Extracts a part from the specified column in the DataFrame based on the provided pattern.

    Parameters:
    - df: pandas DataFrame
    - col_name: str, the name of the column to be modified

    Returns:
    - None (modifies the DataFrame in place)
    """
    # Match exactly 13 digits
    digits_pattern = r"^(\d{13}|\d{16})$"
    df_digits = df[col_name].str.extract(digits_pattern)

    # Match digits between '>' and '<'
    tags_pattern = r">(\d+)<"
    df_tags = df[col_name].str.extract(tags_pattern)

    # Combine the results
    df[col_name] = df_digits.fillna(df_tags)
