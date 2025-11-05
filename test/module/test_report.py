import datetime
from test.module.utils import (
    default_dosages_dict,
    default_full_prescription_summaries,
    default_pages_dict,
    default_partial_prescription_summaries,
    extract_part_from_column,
)

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pytest_mock import MockerFixture

from src.autoscription.core.config import config
from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.report import get_report_data


class TestReport:
    def test_get_report_data_231103(self):
        data_path = "test/module/data/231103"
        pages: pd.DataFrame = pd.read_csv(f"{data_path}/generate_report_data_pages_0.csv", header=0, sep="|")
        dosages: pd.DataFrame = pd.read_csv(f"{data_path}/generate_report_data_dosages_0.csv", header=0, sep="|")
        partial_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/generate_report_data_partial_prescription_summaries_0.csv", header=0, sep="|"
        )

        full_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/generate_full_prescriptions_summaries.csv",
            header=0,
            sep="|",
            dtype={
                "prescription": "object",
                "doctor_specialty_id": "object",
                "doctor_specialty_name": "object",
                "contains_desensitization_vaccine": "bool",
                "medical_report_required": "bool",
            },
        )

        result = get_report_data(
            pages=pages,
            dosages=dosages,
            partial_prescription_summaries=partial_prescription_summaries,
            full_prescription_summaries=full_prescription_summaries,
            run_date=datetime.date(2023, 11, 3),
            report_config=config["reporting"],
            business_rules_config=config["business_rules"],
            monitoring=TestMonitoring(),
        )
        # If you want to view the report uncomment this function
        # generate_report(result, Path("test_report.pdf"))

        extract_part_from_column(result["manual_check"], "Αριθμός συνταγής")
        extract_part_from_column(result["not_detected_barcodes"], "Όνομα αρχείου")
        extract_part_from_column(result["get_category_2_df"], "Αριθμός συνταγής")

        missing_pharm_prescriptions = pd.read_parquet(f"{data_path}/missing_pharm_prescriptions.parquet")
        missing_doctor_prescriptions = pd.read_parquet(f"{data_path}/missing_doctor_prescriptions.parquet")
        manual_check = pd.read_parquet(f"{data_path}/manual_check.parquet")
        not_detected_barcodes = pd.read_parquet(f"{data_path}/not_detected_barcodes.parquet")
        get_category_2_df = pd.read_parquet(f"{data_path}/get_category_2_df.parquet")

        extract_part_from_column(manual_check, "Αριθμός συνταγής")
        extract_part_from_column(not_detected_barcodes, "Όνομα αρχείου")
        extract_part_from_column(get_category_2_df, "Αριθμός συνταγής")

        assert result["config_show_overview"] == True
        assert result["config_category_breakdown"] == False
        assert result["config_execution_time_ordering"] == False
        assert result["date"] == datetime.date(2023, 11, 3)
        assert result["scanned_docs"] == 222
        assert result["prescriptions_full_idika"] == 170
        assert result["prescriptions_full_idika_cat1"] == 158
        assert result["prescriptions_docs"] == 221
        assert result["digital_prescriptions"] == 102
        assert result["digital_prescriptions_docs"] == 13
        assert result["category_1_pres"] == 137
        assert result["category_1_docs"] == 17
        assert result["category_2_pres"] == 11
        assert result["category_2_docs"] == 0
        assert result["category_3_pres"] == 0
        assert result["category_3_docs"] == 0
        assert result["category_4_pres"] == 0
        assert result["category_4_docs"] == 0
        assert result["category_8_pres"] == 1
        assert result["category_8_docs"] == 0
        assert result["hundred_perc_pres"] == 2
        assert result["hundred_perc_docs"] == 0
        assert result["vaccines_pres"] == 8
        assert_frame_equal(result["missing_pharm_prescriptions"], missing_pharm_prescriptions)
        assert result["missing_pharm_presciptions_existing_doc"].empty
        assert_frame_equal(result["missing_doctor_prescriptions"], missing_doctor_prescriptions)
        assert result["missing_doc_prescriptions_existing_pharm"].empty
        assert result["pharmacist_missing_pages"].empty
        assert_frame_equal(result["remove_docs"], pd.read_parquet(f"{data_path}/remove_docs.parquet"))
        assert result["dosage_check"].empty
        assert result["not_in_idika_scans_df"].empty
        assert_frame_equal(result["manual_check"], manual_check)
        assert_frame_equal(result["not_detected_barcodes"], not_detected_barcodes)
        assert_frame_equal(result["daily_analytics"], pd.read_parquet(f"{data_path}/daily_analytics.parquet"))
        assert result["total_revenue"] == "1,026.84 €"
        assert result["total_revenue_value"] == 1026.84
        assert result["total_gov_contribution"] == "555.56 €"
        assert result["total_gov_contribution_value"] == 555.56
        assert result["total_patient_contribution_value"] == 471.28
        assert result["total_patient_contribution"] == "471.28 €"
        assert result["total_missing_insurance_amount_value"] == 507.11
        assert result["total_missing_insurance_amount"] == "507.11 €"
        assert result["total_eopyy_amount_value"] == 552.33
        assert result["total_eopyy_amount"] == "552.33 €"
        assert result["total_other_funds_amount_value"] == 3.23
        assert result["total_other_funds_amount"] == "3.23 €"
        assert result["total_missing_other_funds_amount_value"] == 3.23
        assert result["total_missing_other_funds_amount"] == "3.23 €"
        assert result["total_missing_eopyy_amount_value"] == 503.88
        assert result["total_missing_eopyy_amount"] == "503.88 €"
        assert result["min_moves"] == 116

        assert_frame_equal(
            result["execution_time_ordering_df"], pd.read_parquet(f"{data_path}/execution_time_ordering_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df"].data, pd.read_parquet(f"{data_path}/all_prescriptions_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df_current_index"].data,
            pd.read_parquet(f"{data_path}/all_prescriptions_df_current_index.parquet"),
        )
        assert_frame_equal(result["get_category_2_df"], get_category_2_df)
        assert result["get_100_percent_documents_df"].empty
        assert result["get_other_documents_df"].empty
        assert result["get_digital_doctor_documents_df"].empty
        assert not result["above_fyk_limit"].empty
        assert result["above_fyk_limit"].shape[0] == 1
        assert result["above_fyk_limit"]["Αριθμός συνταγής"][0] == "2310104283854120"
        assert result["above_fyk_limit"]["Ώρα Εκτέλεσης"][0] == datetime.time(17, 12, 2)
        assert result["above_fyk_limit"]["Ονομ/νυμο Ιατρού"][0] == "Deborah Butler"
        assert result["above_fyk_limit"]["Ονομ/νυμο Ασθενούς"][0] == "Dana Peters"
        assert result["above_fyk_limit"]["Θέση στοίβας"][0] == "-"
        assert not result["prescriptions_amount"].empty
        assert result["prescriptions_amount"].shape[0] == 172
        assert_frame_equal(result["prescriptions_amount"], pd.read_parquet(f"{data_path}/prescriptions_amount.parquet"))
        assert_frame_equal(result["no_specialty_doctors"], pd.read_parquet(f"{data_path}/no_specialty_doctors.parquet"))
        assert_frame_equal(
            result["medical_report_prescriptions"], pd.read_parquet(f"{data_path}/medical_report_prescriptions.parquet")
        )
        assert_frame_equal(
            result["desensitization_prescriptions"],
            pd.read_parquet(f"{data_path}/desensitization_prescriptions.parquet"),
        )

    def test_get_report_data_231213(self):
        data_path = "test/module/data/231213"
        pages: pd.DataFrame = pd.read_csv(f"{data_path}/pages_20231213-20240106_204250.csv", header=0, sep="|")
        dosages: pd.DataFrame = pd.read_csv(f"{data_path}/dosages_20231213-20240106_204250.csv", header=0, sep="|")
        partial_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/generate_report_data_partial_prescription_summaries_0.csv", header=0, sep="|"
        )
        full_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/generate_full_prescriptions_summaries.csv",
            header=0,
            sep="|",
            dtype={
                "prescription": "object",
                "doctor_specialty_id": "object",
                "doctor_specialty_name": "object",
                "contains_desensitization_vaccine": "bool",
                "medical_report_required": "bool",
            },
        )
        result = get_report_data(
            pages=pages,
            dosages=dosages,
            partial_prescription_summaries=partial_prescription_summaries,
            full_prescription_summaries=full_prescription_summaries,
            run_date=datetime.date(2023, 12, 13),
            report_config=config["reporting"],
            business_rules_config=config["business_rules"],
            monitoring=TestMonitoring(),
        )
        # If you want to view the report uncomment this function
        # generate_report(result, Path("test_report.pdf"))

        extract_part_from_column(result["manual_check"], "Αριθμός συνταγής")
        extract_part_from_column(result["not_detected_barcodes"], "Όνομα αρχείου")
        extract_part_from_column(result["get_category_2_df"], "Αριθμός συνταγής")

        missing_pharm_prescriptions = pd.read_parquet(f"{data_path}/missing_pharm_prescriptions.parquet")
        missing_doctor_prescriptions = pd.read_parquet(f"{data_path}/missing_doctor_prescriptions.parquet")
        manual_check = pd.read_parquet(f"{data_path}/manual_check.parquet")
        not_detected_barcodes = pd.read_parquet(f"{data_path}/not_detected_barcodes.parquet")
        get_category_2_df = pd.read_parquet(f"{data_path}/get_category_2_df.parquet")
        dosage_check = pd.read_parquet(f"{data_path}/dosage_check.parquet")
        get_other_documents_df = pd.read_parquet(f"{data_path}/get_other_documents_df.parquet")
        extract_part_from_column(manual_check, "Αριθμός συνταγής")
        extract_part_from_column(not_detected_barcodes, "Όνομα αρχείου")
        extract_part_from_column(get_category_2_df, "Αριθμός συνταγής")

        assert result["config_show_overview"] == True
        assert result["config_category_breakdown"] == False
        assert result["config_execution_time_ordering"] == False
        assert result["date"] == datetime.date(2023, 12, 13)
        assert result["scanned_docs"] == 182
        assert result["prescriptions_full_idika"] == 129
        assert result["prescriptions_full_idika_cat1"] == 120
        assert result["prescriptions_docs"] == 181
        assert result["digital_prescriptions"] == 84
        assert result["digital_prescriptions_docs"] == 84
        assert result["category_1_pres"] == 120
        assert result["category_1_docs"] == 162
        assert result["category_2_pres"] == 5
        assert result["category_2_docs"] == 6
        assert result["category_3_pres"] == 0
        assert result["category_3_docs"] == 0
        assert result["category_4_pres"] == 0
        assert result["category_4_docs"] == 0
        assert result["category_8_pres"] == 4
        assert result["category_8_docs"] == 2
        assert result["hundred_perc_pres"] == 0
        assert result["hundred_perc_docs"] == 0
        assert result["vaccines_pres"] == 3
        assert_frame_equal(result["missing_pharm_prescriptions"], missing_pharm_prescriptions)
        assert result["missing_pharm_presciptions_existing_doc"].empty
        assert_frame_equal(result["missing_doctor_prescriptions"], missing_doctor_prescriptions)
        assert result["missing_doc_prescriptions_existing_pharm"].empty
        assert result["pharmacist_missing_pages"].empty
        assert_frame_equal(result["remove_docs"], pd.read_parquet(f"{data_path}/remove_docs.parquet"))
        assert_frame_equal(result["dosage_check"], dosage_check)
        assert result["not_in_idika_scans_df"].empty
        assert_frame_equal(result["manual_check"], manual_check)
        assert_frame_equal(result["not_detected_barcodes"], not_detected_barcodes)
        assert_frame_equal(result["daily_analytics"], pd.read_parquet(f"{data_path}/daily_analytics.parquet"))
        assert result["total_revenue"] == "710.79 €"
        assert result["total_revenue_value"] == 710.79
        assert result["total_gov_contribution"] == "537.93 €"
        assert result["total_gov_contribution_value"] == 537.93
        assert result["total_patient_contribution_value"] == 172.86
        assert result["total_patient_contribution"] == "172.86 €"
        assert result["total_missing_insurance_amount_value"] == 8.34
        assert result["total_missing_insurance_amount"] == "8.34 €"
        assert result["total_eopyy_amount_value"] == 521.25
        assert result["total_eopyy_amount"] == "521.25 €"
        assert result["total_other_funds_amount_value"] == 16.68
        assert result["total_other_funds_amount"] == "16.68 €"
        assert result["total_missing_other_funds_amount_value"] == 8.34
        assert result["total_missing_other_funds_amount"] == "8.34 €"
        assert result["total_missing_eopyy_amount_value"] == 0.0
        assert result["total_missing_eopyy_amount"] == "0.00 €"
        assert result["min_moves"] == 115
        assert_frame_equal(
            result["execution_time_ordering_df"], pd.read_parquet(f"{data_path}/execution_time_ordering_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df"].data, pd.read_parquet(f"{data_path}/all_prescriptions_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df_current_index"].data,
            pd.read_parquet(f"{data_path}/all_prescriptions_df_current_index.parquet"),
        )
        assert_frame_equal(result["get_category_2_df"], get_category_2_df)
        assert result["get_100_percent_documents_df"].empty
        assert_frame_equal(result["get_other_documents_df"], get_other_documents_df)
        assert result["get_digital_doctor_documents_df"].empty
        assert not result["above_fyk_limit"].empty
        assert result["above_fyk_limit"].shape[0] == 1
        assert result["above_fyk_limit"]["Αριθμός συνταγής"][0] == "2312125917015110"
        assert result["above_fyk_limit"]["Ώρα Εκτέλεσης"][0] == datetime.time(11, 47, 34)
        assert result["above_fyk_limit"]["Ονομ/νυμο Ιατρού"][0] == "Sarah Fisher"
        assert result["above_fyk_limit"]["Ονομ/νυμο Ασθενούς"][0] == "Matthew Fletcher"
        assert result["above_fyk_limit"]["Θέση στοίβας"][0] == "109"
        assert not result["prescriptions_amount"].empty
        assert result["prescriptions_amount"].shape[0] == 129
        assert_frame_equal(result["prescriptions_amount"], pd.read_parquet(f"{data_path}/prescriptions_amount.parquet"))
        assert_frame_equal(result["no_specialty_doctors"], pd.read_parquet(f"{data_path}/no_specialty_doctors.parquet"))
        assert_frame_equal(
            result["medical_report_prescriptions"], pd.read_parquet(f"{data_path}/medical_report_prescriptions.parquet")
        )
        assert_frame_equal(
            result["desensitization_prescriptions"],
            pd.read_parquet(f"{data_path}/desensitization_prescriptions.parquet"),
        )

    def test_get_report_data_240108(self):
        # TODO: improve test
        data_path = "test/module/data/240108"
        pages: pd.DataFrame = pd.read_csv(f"{data_path}/pages_20240108-20240604_124053_anon.csv", header=0, sep="|")
        dosages: pd.DataFrame = pd.read_csv(f"{data_path}/dosages_20240108-20240604_124053.csv", header=0, sep="|")
        partial_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/api_partial_prescriptions_summaries_20240108-20240604_124053.csv", header=0, sep="|"
        )
        full_prescription_summaries: pd.DataFrame = pd.read_csv(
            f"{data_path}/api_full_prescriptions_summaries_20240108-20240702_134941.csv",
            header=0,
            sep="|",
            dtype={
                "prescription": "object",
                "doctor_specialty_id": "object",
                "doctor_specialty_name": "object",
                "contains_desensitization_vaccine": "bool",
                "medical_report_required": "bool",
            },
        )
        result = get_report_data(
            pages=pages,
            dosages=dosages,
            partial_prescription_summaries=partial_prescription_summaries,
            full_prescription_summaries=full_prescription_summaries,
            run_date=datetime.date(2024, 1, 8),
            report_config=config["reporting"],
            business_rules_config=config["business_rules"],
            monitoring=TestMonitoring(),
        )

        extract_part_from_column(result["manual_check"], "Αριθμός συνταγής")
        extract_part_from_column(result["not_detected_barcodes"], "Όνομα αρχείου")
        extract_part_from_column(result["get_category_2_df"], "Αριθμός συνταγής")
        extract_part_from_column(result["missing_pharm_prescriptions"], "Αριθμός συνταγής")
        extract_part_from_column(result["missing_doctor_prescriptions"], "Αριθμός συνταγής")
        extract_part_from_column(result["execution_time_ordering_df"], "Ανακατάταξη συνταγής")
        extract_part_from_column(result["execution_time_ordering_df"], "Συνταγή αναφοράς (τοποθέτηση πριν απο συνταγή)")
        extract_part_from_column(result["all_prescriptions_df"].data, "Συνταγή")
        extract_part_from_column(result["all_prescriptions_df_current_index"].data, "Συνταγή")
        extract_part_from_column(result["prescriptions_amount"], "Αριθμός συνταγής")

        missing_pharm_prescriptions = pd.read_parquet(f"{data_path}/missing_pharm_prescriptions.parquet")
        missing_doctor_prescriptions = pd.read_parquet(f"{data_path}/missing_doctor_prescriptions.parquet")
        manual_check = pd.read_parquet(f"{data_path}/manual_check.parquet")
        not_detected_barcodes = pd.read_parquet(f"{data_path}/not_detected_barcodes.parquet")
        get_category_2_df = pd.read_parquet(f"{data_path}/get_category_2_df.parquet")
        get_other_documents_df = pd.read_parquet(f"{data_path}/get_other_documents_df.parquet")

        assert result["config_show_overview"] == True
        assert result["config_category_breakdown"] == False
        assert result["config_execution_time_ordering"] == False
        assert result["date"] == datetime.date(2024, 1, 8)
        assert result["scanned_docs"] == 245
        assert result["prescriptions_full_idika"] == 167
        assert result["prescriptions_full_idika_cat1"] == 163
        assert result["prescriptions_docs"] == 240
        assert result["digital_prescriptions"] == 101
        assert result["digital_prescriptions_docs"] == 102
        assert result["category_1_pres"] == 161
        assert result["category_1_docs"] == 219
        assert result["category_2_pres"] == 3
        assert result["category_2_docs"] == 3
        assert result["category_3_pres"] == 0
        assert result["category_3_docs"] == 0
        assert result["category_4_pres"] == 1
        assert result["category_4_docs"] == 2
        assert result["category_8_pres"] == 0
        assert result["category_8_docs"] == 0
        assert result["hundred_perc_pres"] == 1
        assert result["hundred_perc_docs"] == 0
        assert result["vaccines_pres"] == 5

        assert_frame_equal(result["missing_pharm_prescriptions"], missing_pharm_prescriptions)
        assert result["missing_pharm_presciptions_existing_doc"].empty
        assert_frame_equal(result["missing_doctor_prescriptions"], missing_doctor_prescriptions)
        assert_frame_equal(
            result["missing_doc_prescriptions_existing_pharm"],
            pd.read_parquet(f"{data_path}/missing_doc_prescriptions_existing_pharm.parquet"),
        )
        assert result["pharmacist_missing_pages"].empty
        assert_frame_equal(result["remove_docs"], pd.read_parquet(f"{data_path}/remove_docs.parquet"))
        assert result["dosage_check"].empty
        assert_frame_equal(
            result["not_in_idika_scans_df"], pd.read_parquet(f"{data_path}/not_in_idika_scans_df.parquet")
        )
        assert_frame_equal(result["manual_check"], manual_check)
        assert_frame_equal(result["not_detected_barcodes"], not_detected_barcodes)
        assert_frame_equal(result["daily_analytics"], pd.read_parquet(f"{data_path}/daily_analytics.parquet"))
        assert result["total_revenue"] == "1,943.76 €"
        assert result["total_revenue_value"] == 1943.76
        assert result["total_gov_contribution"] == "1,218.00 €"
        assert result["total_gov_contribution_value"] == 1218.0
        assert result["total_patient_contribution_value"] == 725.76
        assert result["total_patient_contribution"] == "725.76 €"
        assert result["total_missing_insurance_amount_value"] == 14.5
        assert result["total_missing_insurance_amount"] == "14.50 €"
        assert result["total_eopyy_amount_value"] == 1218.0
        assert result["total_eopyy_amount"] == "1,218.00 €"
        assert result["total_other_funds_amount_value"] == 0.0
        assert result["total_other_funds_amount"] == "0.00 €"
        assert result["total_missing_other_funds_amount_value"] == 0.0
        assert result["total_missing_other_funds_amount"] == "0.00 €"
        assert result["total_missing_eopyy_amount_value"] == 14.5
        assert result["total_missing_eopyy_amount"] == "14.50 €"
        assert result["min_moves"] == 153
        assert_frame_equal(
            result["execution_time_ordering_df"], pd.read_parquet(f"{data_path}/execution_time_ordering_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df"].data, pd.read_parquet(f"{data_path}/all_prescriptions_df.parquet")
        )
        assert_frame_equal(
            result["all_prescriptions_df_current_index"].data,
            pd.read_parquet(f"{data_path}/all_prescriptions_df_current_index.parquet"),
        )

        assert_frame_equal(result["get_category_2_df"], get_category_2_df)
        assert result["get_100_percent_documents_df"].empty
        result["get_other_documents_df"].to_parquet(f"{data_path}/get_other_documents_df.parquet")
        assert_frame_equal(result["get_other_documents_df"], get_other_documents_df)
        assert result["get_digital_doctor_documents_df"].empty
        assert result["above_fyk_limit"].empty
        assert not result["prescriptions_amount"].empty
        assert result["prescriptions_amount"].shape[0] == 168
        assert_frame_equal(result["prescriptions_amount"], pd.read_parquet(f"{data_path}/prescriptions_amount.parquet"))
        assert_frame_equal(result["no_specialty_doctors"], pd.read_parquet(f"{data_path}/no_specialty_doctors.parquet"))
        assert_frame_equal(
            result["medical_report_prescriptions"], pd.read_parquet(f"{data_path}/medical_report_prescriptions.parquet")
        )
        assert_frame_equal(
            result["desensitization_prescriptions"],
            pd.read_parquet(f"{data_path}/desensitization_prescriptions.parquet"),
        )
