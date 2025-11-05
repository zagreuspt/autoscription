import glob
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pandas import DataFrame
from pandas.io.formats.style import Styler
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

from src.autoscription.core import config
from src.autoscription.core.errors import AboveFykLimitPrescriptionFoundException
from src.autoscription.core.logging import Monitoring

# pd.set_option('display.max_columns', 10)
# pd.set_option('display.width', 10000)
# pd.set_option('display.max_rows', None)

COASTGUARD = "Λιμενικό Σώμα / Ακτοφυλακή"
EU_CITYZEN = "Ευρωπαίων Ασφαλισμένων**"
INJECTIONS = "Εμβόλια"
FULL_PARTICIPATION = "100% Συμμετοχή"
EOPYY_BENEFICIARY = "Δικαιούχοι περίθαλψης του Ε.Ο.Π.Υ.Υ."
INTANGIBLE_PRESCR = "Άυλη Συνταγή"


def generate_report(data: Dict[str, Any], target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    templates_path = config.get_report_templates_path().as_posix()
    font_config = FontConfiguration()
    env = Environment(loader=FileSystemLoader(searchpath=templates_path))  # nosec: B701 - no risc of xss
    # TODO: move to config
    logo_path = config.get_project_root() / "resources" / "report" / "templates" / "logo.png"
    logo_uri = "file:///" + logo_path.resolve().as_posix()
    template = env.get_template("template.j2")
    html = template.render(data, logo_src=logo_uri)
    html_object = HTML(string=html)
    # TODO: Move to file
    css = CSS(
        string="""
/*
  Moonstone: #17B4CE (23, 180, 206)
  Moonstone: #2A9DB0 (42, 157, 176)
  Prussian blue: #002537 (0, 37, 55)
  Blue Green: #139CB6 (19, 156, 182)
  Azure (web): #E1F3F4 (225, 243, 244)
  Baby powder: #FEFEFC (254, 254, 252)
*/

@page { size: A4;
        margin-top: 16mm;
        margin-bottom: 12mm;
        margin-left: 12mm;
        margin-right: 12mm;
}

.header {
    display: flex;
    position: relative;
    top: -4mm;
    right:0mm;
    text-align: center;
    color: #9a9494;
    font-size: 14px;
    width: 100%;
    justify-content: center;
}

.footer {
    position: absolute;
    bottom: -8mm;
    left: 0mm;
    text-align: center;
    color: #9a9494;
    font-size: 12px;
    width: 100%;
}

.fixed-logo {
    position: fixed;
    top: -9mm; /* Adjust this value as needed */
    right: -5mm; /* Adjust this value as needed */
    width: 60px; /* Adjust this value to control the logo size */
    z-index: 999;
}

.fixed-logo img {
    max-width: 100%;
    height: auto;
}

body {
    margin: 0mm 0mm;
    background-color: #FFFFFF;
    padding: 0px;
    box-sizing: border-box;
}

.three-segments {
    display: flex; /* use Flexbox for layout */
    margin: 10px 10px; /* center the container horizontally */
}

.segment {
    flex: 1; /* distribute the available space equally among the segments */
    margin: 2.5px; /* add some margin between segments */
    padding: 4px; /* add padding inside each segment */
    box-sizing: border-box; /* include padding in total width */
    background-color: #E1F3F4; /* set background color for segments */
    border-radius: 30px; /* add border-radius to segments */
}

.segment1 {
    flex: 1; /* distribute the available space equally among the segments */
    margin: 2.5px; /* add some margin between segments */
    padding: 4px; /* add padding inside each segment */
    box-sizing: border-box; /* include padding in total width */
    background-color: #d1e6e8 ; /* set background color for segments */
    border-radius: 30px; /* add border-radius to segments */
}

h1 {
    position: relative;
    top: 0mm;
    color: #139CB6;
    text-align: center;
    margin-top: 0mm;
    font-size: 36px;
}

h2 {
    color: #17B4CE;
    text-align: left;
    margin-top: 4mm;
    font-size: 32px;
}

h3 {
    color: #2A9DB0;
    text-align: left;
    margin-top: 4mm;
    font-size: 22px;
}

h4 {
    color: #2A9DB0;
    text-align: left;
    margin-top: 4mm;
    margin-bottom: 3mm;
    font-size: 16px;
}

h5 {
    color: #17B4CE;
    text-align: center;
    margin-top: 1px;
    margin-bottom: 3mm;
    font-size: 24px;
}

h6 {
    color: #2A9DB0;
    text-align: left;
    margin-top: 1mm;
    margin-bottom: 3mm;
    font-size: 13px;
}

h7 {
    margin-top: 0mm;
    margin-bottom: 0mm;
    margin: 10px 0;
    text-align: center;
    font-size: 13px;
    color: #3a759c;
    font-weight: bold;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background-color: #FEFEFC;
  border-radius: 15px;
}

th,
td {
  padding: 8px;
  text-align: center;
  border-bottom: 1px solid #eee;
  font-size: 10px;
  color: #002537;
}

th {
  background-color: #139CB6;
  text-align: center;
  color: #FEFEFC;
  font-weight: bold;
  font-size: 12px;
  border-radius: 15px 15px 0 0;
}

tr:last-child td {
  border-bottom: none;
}

tr:nth-child(odd) {
  background-color: #FEFEFC;
}

tr:nth-child(even) {
  background-color: #E1F3F4;
}

tr:last-child td:first-child {
  border-bottom-left-radius: 15px;
}

tr:last-child td:last-child {
  border-bottom-right-radius: 15px;
}


.alt-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background-color: #FEFEFC;
  border-radius: 0px;
  border-bottom: 0 !important;
  border-bottom-left-radius:0
}

.alt-table td:first-child,
.alt-table th:first-child {
    width: 1%; /* Adjust the width to your liking */
}

.alt-table th,
.alt-table td {
  padding: 7px;
  text-align: center;
  border-bottom: 0px solid #eee;
  font-size: 7px;
  color: #002537; /* changed */
}

.alt-table th {
  background-color: #139CB6;  /* changed */
  text-align: center;
  color: #FEFEFC;
  font-weight: bold;
  font-size: 10px;
  border-radius: 0px 0px 0 0;
}

.alt-table tr:last-child td {
  border-bottom: none;
}

.alt-table tr:nth-child(odd) {
  background-color: #FEFEFC;  /* changed */
}

.alt-table tr:nth-child(even) {
  background-color: #E1F3F4;  /* changed */
}

.alt-table tr:last-child td:first-child {
  border-bottom-left-radius: 0px;
}

.alt-table tr:last-child td:last-child {
  border-bottom-right-radius: 0px;
}


.value {
    margin: 10px 0;
    text-align: center;
    font-size: 15px;
    color: #3a759c;
    font-weight: bold;
}

.value1 {
    margin: 10px 0;
    text-align: center;
    font-size: 13px;
    font-weight: bold;
    color: #17B4CE;
}

.avoid-page-break {
    page-break-inside: avoid;
}

.group-together {
    orphans: 10;  /* at least 3 lines at the bottom of a page */
    widows: 10;   /* at least 3 lines at the top of a new page */
}

h3, h6 {
  page-break-after: avoid;
  orphans: 3;
  widows: 3;
}
.section-divider {
    border: none; /* Remove default border */
    background-image: linear-gradient(to right, #E1F3F4, #17B4CE),
                      linear-gradient(to right, #17B4CE, #E1F3F4),
                      linear-gradient(to right, #E1F3F4, #17B4CE),
                      linear-gradient(to right, #17B4CE, #E1F3F4);
    background-size: 50% 2px, 50% 2px, 50% 2px, 50% 2px;
    background-position: 0 25%, 100% 25%, 0 75%, 100% 75%;
    background-repeat: no-repeat;
    height: 12px; /* Adjust the height to fit both lines */
    margin: 8px auto; /* Add some margin above and below the lines */
    width: 100%; /* Set the line width to 100% */
}

.page-break-before {
    page-break-before: always;
}


.prescriptions-amount-table td {
    padding: 3px;
}


        """,
        font_config=font_config,
    )
    html_object.write_pdf(target=target_path.as_posix(), stylesheets=[css], font_config=font_config)


def contains_eu_citizen(df: pd.DataFrame) -> bool:
    return len(df[df["Κατηγορία"] == EU_CITYZEN]) > 0


def get_report_data(
    pages: pd.DataFrame,
    dosages: pd.DataFrame,
    partial_prescription_summaries: pd.DataFrame,
    full_prescription_summaries: pd.DataFrame,
    run_date: date,
    report_config: Dict[str, Any],
    business_rules_config: Dict[str, Any],
    monitoring: Monitoring,
) -> Dict[str, Any]:
    # pages.to_csv("10.report_input_pages.csv")
    if not has_dataframe_attribute(pages, "manual_check"):
        pages = pages.assign(manual_check=np.nan)
    # Data Transformation pages
    pages["prescription"] = pages["prescription"].apply(lambda x: str(int(x)) if pd.notna(x) else np.nan)
    pages["scan_prescription_full"] = (
        pages["prescription_scanned_pages"].astype(str).apply(lambda x: x.split("_")[1] if ("_" in x) else np.nan)
    )
    pages["pharmacist_idika_prescription_full"] = pages["pharmacist_idika_prescription_full"].apply(
        lambda x: str(int(x)) if pd.notna(x) else np.nan
    )
    pages["execution"] = pages["pharmacist_idika_prescription_full"].str[-1].replace("", np.nan)
    pages["execution"] = pages["execution"].astype(pd.Int64Dtype())
    pages["stack_number"] = pages["stack_number"] + 1  # change the stack number so that it does not start with "0"
    pages["stack_number"] = pages["stack_number"].astype(pd.Int64Dtype())
    pages["page"] = pages["page"].astype(pd.Int64Dtype())
    pages["pages"] = pages["pages"].astype(pd.Int64Dtype())
    pages["category"] = pages["category"].astype(pd.Int64Dtype())
    pages["scan_last_three_digits"] = pages["scan_last_three_digits"].astype(pd.Int64Dtype())
    pages["scan_last_three_digits"] = pages["scan_last_three_digits"].apply(
        lambda x: f"{x:03d}" if len(str(x)) < 3 else str(x)
    )
    pages["pr_order_timestamp"] = (
        pd.to_datetime(pages["pr_order_timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%z")
        + pd.Timedelta(hours=2)
    )
    # pages.loc[pages.document_type == "injection", "category"] = 2
    # Data Transformation dosages
    dosages["prescription"] = dosages["prescription"].astype(pd.Int64Dtype()).astype(pd.StringDtype())
    dosages["boxes_provided"] = dosages["boxes_provided"].astype(pd.Int64Dtype())
    dosages["boxes_provided_multiple_executions"] = dosages["boxes_provided_multiple_executions"].astype(
        pd.Int64Dtype()
    )
    dosages["boxes_required"] = dosages["boxes_required"].astype(pd.Int64Dtype())
    dosages["total"] = dosages["total"]  # .str.replace(".", "").str.replace(",", ".").astype(float)
    dosages["patient_contrib"] = dosages["patient_contrib"]  # .str.replace(".", "").str.replace(",", ".").astype(float)
    dosages["gov_contrib"] = dosages["gov_contrib"]  # .str.replace(".", "").str.replace(",", ".").astype(float)

    # Data Transformation partial_prescription_summaries
    partial_prescription_summaries["prescription"] = partial_prescription_summaries["prescription"].apply(
        lambda x: str(int(x)) if pd.notna(x) else np.nan
    )
    partial_prescription_summaries["execution"] = partial_prescription_summaries["execution"].astype(pd.Int64Dtype())
    # the following will level the data so that the first execution is 0
    partial_prescription_summaries["execution"] = partial_prescription_summaries["execution"] - 1

    # Overall Metrics
    scanned_docs = pages.shape[0]
    prescriptions = pages.prescription.nunique()

    pharmacist_idika_prescription_full = pages[pages["100%"] == False][
        "pharmacist_idika_prescription_full"
    ].drop_duplicates()

    pages = pages[(pages["prescription_scanned_pages"].notna()) | (pages["prescription"].notna())]
    pages['prescription_scanned_pages'] = pages['prescription_scanned_pages'].replace(["", "nan", "NaN", "None", " "], pd.NA)
    dosages = dosages[(dosages["prescription"].notna())]

    pharmacist_idika_prescription_full_list = pharmacist_idika_prescription_full.nunique()
    barcode_not_found_filtered_docs = pages[pages["scan_prescription_full"] == "0000000000000000"]
    barcode_not_found_docs = barcode_not_found_filtered_docs.shape[0]

    filtered_prescription_full = pages[pages["scan_prescription_full"] != "0000000000000000"]
    prescriptions_docs = filtered_prescription_full.shape[0]

    digital_prescriptions = pages[pages.digital == True].prescription.nunique()
    digital_prescriptions_docs = pages[pages.digital == True].scan_prescription_full.nunique()

    category_1_pres = pages[pages["category"] == 1].prescription.nunique()
    category_1_docs = pages[pages["category"] == 1].scan_prescription_full.nunique()

    pharmacist_idika_prescription_full_categ_1_list = pages[(pages["category"] == 1) & (pages["100%"] == False)][
        "pharmacist_idika_prescription_full"
    ]
    pharmacist_idika_prescription_full_categ_1_list = pharmacist_idika_prescription_full_categ_1_list.nunique()

    category_2_pres = pages[pages["category"] == 2].prescription.nunique()
    category_2_docs = pages[pages["category"] == 2].scan_prescription_full.nunique()

    category_3_pres = pages[pages["category"] == 3].prescription.nunique()
    category_3_docs = pages[pages["category"] == 3].scan_prescription_full.nunique()

    category_4_pres = pages[pages["category"] == 4].prescription.nunique()
    category_4_docs = pages[pages["category"] == 4].scan_prescription_full.nunique()

    category_8_pres = pages[pages["category"] == 8].prescription.nunique()
    category_8_docs = pages[pages["category"] == 8].scan_prescription_full.nunique()

    hundred_perc_pres = pages[pages["100%"] == True].prescription.nunique()
    hundred_perc_docs = pages[pages["100%"] == True].scan_prescription_full.nunique()

    vaccines_pres = pages[pages["document_type"] == "injection"].prescription.nunique()

    # ----------------------------------------------------------------
    log_data(
        barcode_not_found_docs=barcode_not_found_docs,
        category_1_docs=category_1_docs,
        category_1_pres=category_1_pres,
        category_2_docs=category_2_docs,
        category_2_pres=category_2_pres,
        category_3_docs=category_3_docs,
        category_3_pres=category_3_pres,
        category_4_docs=category_4_docs,
        category_4_pres=category_4_pres,
        category_8_docs=category_8_docs,
        category_8_pres=category_8_pres,
        digital_prescriptions=digital_prescriptions,
        digital_prescriptions_docs=digital_prescriptions_docs,
        hundred_perc_docs=hundred_perc_docs,
        hundred_perc_pres=hundred_perc_pres,
        prescriptions=prescriptions,
        prescriptions_docs=prescriptions_docs,
        scanned_docs=scanned_docs,
        monitoring=monitoring,
    )

    dosages_issues = get_dosage_issues(dosages=dosages, pages=pages, run_date=run_date, monitoring=monitoring)
    manual_check_df = get_negative_manual_check(pages=pages, run_date=run_date, monitoring=monitoring)

    # DO NOT DELETE, we would probably need it to assess what happens if
    # the manual check is blank because everything was ok?
    # if has_dataframe_attribute(pages, 'manual_check'):
    #   manual_check_df = get_negative_manual_check(pages, run_date=run_date)
    # else:
    #   monitoring.logger_adapter.warning("Skipping manual_check since it doesn't exist in
    #   the DataFrame.")
    #   # Handle the case when 'manual_check' doesn't exist, e.g., set
    #   manual_check_df to an empty DataFrame or None
    #   manual_check_df = None

    not_in_idika_scans_df = get_not_in_idika_scans(pages=pages, run_date=run_date, monitoring=monitoring)
    missing_pharm_prescriptions_df = get_missing_pharmacist_prescriptions(
        pages=pages, run_date=run_date, monitoring=monitoring
    )
    missing_pharm_presciptions_existing_doc_df = get_missing_pharmacist_no_digital_doctor_detected(
        pages=pages, run_date=run_date, monitoring=monitoring
    )
    missing_doctor_prescriptions_df = get_missing_doctor_prescriptions(
        pages=pages, run_date=run_date, monitoring=monitoring
    )
    missing_doc_prescriptions_existing_pharm_df = get_missing_doctor_no_digital_pharmacist_detected(
        pages=pages, run_date=run_date, monitoring=monitoring
    )
    pharmacist_missing_pages_df = get_pharmacist_missing_pages(pages=pages, run_date=run_date, monitoring=monitoring)
    remove_docs_df = get_documents_to_be_removed(pages=pages, run_date=run_date, monitoring=monitoring)
    not_detected_barcodes_df = not_detected_barcodes(pages=pages, run_date=run_date, monitoring=monitoring)
    daily_analytics = calculate_daily_analytics(pages=pages)

    get_category_2_df = get_category_2_documents(pages=pages, run_date=run_date, monitoring=monitoring).drop(
        "Κατηγορία", axis=1
    )
    get_100_percent_documents_df = get_100_percent_documents(pages=pages, run_date=run_date, monitoring=monitoring)
    get_other_documents_df = get_other_documents(pages=pages, run_date=run_date, monitoring=monitoring).drop(
        "Ασφαλιστικός Φορέας", axis=1
    )
    get_digital_doctor_documents_df = get_digital_doctor_documents(
        pages=pages, run_date=run_date, monitoring=monitoring
    )

    (
        min_moves,
        execution_time_ordering_df,
        all_prescriptions_df,
        all_prescriptions_df_current_index,
    ) = execution_time_ordering(pages=pages, injections=False, run_date=run_date, monitoring=monitoring)
    (
        injections_min_moves,
        injections_execution_time_ordering_df,
        injections_prescriptions_df,
        injections_prescriptions_df_current_index,
    ) = execution_time_ordering(pages=pages, injections=True, run_date=run_date, monitoring=monitoring)
    
    # missing_pharm_prescriptions_df.to_csv("11.missing_pharm_prescriptions_df.csv")
    # TODO: add type checking (mypy), currently covered by TestGetReportData:test_get_report_data_schema
    return {
        "config_show_overview": report_config["show_overview"],
        "config_category_breakdown": report_config["category_breakdown"],
        "config_execution_time_ordering": report_config["execution_time_ordering"],
        "date": run_date,
        "scanned_docs": scanned_docs,
        "prescriptions_full_idika": pharmacist_idika_prescription_full_list,
        "prescriptions_full_idika_cat1": pharmacist_idika_prescription_full_categ_1_list,
        "prescriptions_docs": prescriptions_docs,
        "digital_prescriptions": digital_prescriptions,
        "digital_prescriptions_docs": digital_prescriptions_docs,
        "category_1_pres": category_1_pres,
        "category_1_docs": category_1_docs,
        "category_2_pres": category_2_pres,
        "category_2_docs": category_2_docs,
        "category_3_pres": category_3_pres,
        "category_3_docs": category_3_docs,
        "category_4_pres": category_4_pres,
        "category_4_docs": category_4_docs,
        "category_8_pres": category_8_pres,
        "category_8_docs": category_8_docs,
        "hundred_perc_pres": hundred_perc_pres,
        "hundred_perc_docs": hundred_perc_docs,
        "vaccines_pres": vaccines_pres,
        "missing_pharm_prescriptions": missing_pharm_prescriptions_df.sort_values(by="Ώρα Εκτέλεσης"),
        "missing_pharm_prescriptions_ekaa_check": contains_eu_citizen(missing_pharm_prescriptions_df),
        "missing_pharm_presciptions_existing_doc": missing_pharm_presciptions_existing_doc_df.sort_values(
            by="Θέση Στοίβας"
        ),
        "missing_doctor_prescriptions": missing_doctor_prescriptions_df.sort_values(by="Ώρα Εκτέλεσης"),
        "missing_doc_prescriptions_existing_pharm": missing_doc_prescriptions_existing_pharm_df.sort_values(
            by="Θέση Στοίβας"
        ),
        "pharmacist_missing_pages": pharmacist_missing_pages_df.sort_values(by="Θέση Στοίβας"),
        "remove_docs": remove_docs_df.sort_values(by="Θέση Στοίβας"),
        "remove_docs_ekaa_check": contains_eu_citizen(remove_docs_df),
        "dosage_check": dosages_issues.sort_values(by="Θέση Στοίβας"),
        "not_in_idika_scans_df": not_in_idika_scans_df.sort_values(by="Θέση Στοίβας"),
        "manual_check": manual_check_df.sort_values(by="Θέση Στοίβας"),
        "not_detected_barcodes": not_detected_barcodes_df.sort_values(by="Θέση Στοίβας"),
        "daily_analytics": daily_analytics.top_5_doctors,
        "total_revenue_value": daily_analytics.total_amount,
        "total_revenue": format_currency(daily_analytics.total_amount),
        "total_patient_contribution_value": daily_analytics.total_patient_amount,  # Is uploaded to backend
        "total_patient_contribution": format_currency(daily_analytics.total_patient_amount),
        "total_gov_contribution_value": daily_analytics.total_insurance_amount,
        "total_gov_contribution": format_currency(daily_analytics.total_insurance_amount),
        "total_missing_insurance_amount_value": daily_analytics.total_missing_insurance_amount,
        "total_missing_insurance_amount": format_currency(daily_analytics.total_missing_insurance_amount),
        "total_eopyy_amount_value": daily_analytics.total_eopyy_amount,
        "total_eopyy_amount": format_currency(daily_analytics.total_eopyy_amount),
        "total_other_funds_amount_value": daily_analytics.total_other_funds_amount,
        "total_other_funds_amount": format_currency(daily_analytics.total_other_funds_amount),
        "total_missing_other_funds_amount_value": daily_analytics.total_missing_other_funds_amount,
        "total_missing_other_funds_amount": format_currency(daily_analytics.total_missing_other_funds_amount),
        "total_missing_eopyy_amount_value": daily_analytics.total_missing_eopyy_amount,
        "total_missing_eopyy_amount": format_currency(daily_analytics.total_missing_eopyy_amount),
        "min_moves": min_moves,
        "execution_time_ordering_df": execution_time_ordering_df,
        "all_prescriptions_df": all_prescriptions_df,
        "all_prescriptions_df_current_index": all_prescriptions_df_current_index,
        "injections_min_moves": injections_min_moves,
        "injections_execution_time_ordering_df": injections_execution_time_ordering_df,
        "injections_prescriptions_df": injections_prescriptions_df,
        "injections_prescriptions_df_current_index": injections_prescriptions_df_current_index,
        "get_category_2_df": get_category_2_df,
        "get_100_percent_documents_df": get_100_percent_documents_df,
        "get_other_documents_df": get_other_documents_df,
        "get_digital_doctor_documents_df": get_digital_doctor_documents_df,
        "fyk_limit": format_currency(business_rules_config["fyk_limit"]),
        "above_fyk_limit": get_above_fyk_limit(
            pages, partial_prescription_summaries, run_date=run_date, monitoring=monitoring
        ),
        "prescriptions_amount": get_prescriptions_amount(pages, run_date=run_date, monitoring=monitoring),
        "no_specialty_doctors": get_prescriptions_no_specialty_doctor_above_limit(
            pages=pages,
            dosages=dosages,
            full_prescription_summaries=full_prescription_summaries,
            run_date=run_date,
            monitoring=monitoring,
        ),
        "medical_report_prescriptions": get_prescriptions_requiring_medical_report(
            pages=pages,
            full_prescription_summaries=full_prescription_summaries,
            run_date=run_date,
            monitoring=monitoring,
        ),
        "desensitization_prescriptions": get_desensitization_prescriptions(
            pages=pages,
            full_prescription_summaries=full_prescription_summaries,
            run_date=run_date,
            monitoring=monitoring,
        ),
    }


def has_dataframe_attribute(dataframe: pd.DataFrame, attribute: str) -> bool:
    try:
        _ = dataframe[attribute]
        return True
    except KeyError:
        return False


def format_currency(value: float, currency_symbol: str = "€", precision: int = 2) -> str:
    return f"{value:,.{precision}f} {currency_symbol}"


def get_category_2_documents(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Define the columns to be used
    remove_docs_cols = [
        "scan_prescription_full",
        "type",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "category_name",
        "justification",
        "prescription_scanned_pages",
    ]
    # Apply the condition for category == 2 and set justification
    category_2_df = pages[(pages["category"] == 2) | (pages["document_type"] == "injection")].copy()
    category_2_df["justification"] = INJECTIONS

    # Filter and process the DataFrame as needed
    category_2_df = process_remove_documents(category_2_df, remove_docs_cols, run_date, monitoring)

    # category_2_df = category_2_df.drop("Ασφαλιστικός Φορέας", axis=1)

    return category_2_df


def get_100_percent_documents(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Apply the condition for 100% == True and set justification
    hundred_percent_df = pages[pages["100%"] == True].copy()
    hundred_percent_df["justification"] = FULL_PARTICIPATION

    # Define the columns to be used and process the DataFrame as before
    remove_docs_cols = [
        "scan_prescription_full",
        "type",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "category_name",
        "justification",
        "prescription_scanned_pages",
    ]
    hundred_percent_df = process_remove_documents(hundred_percent_df, remove_docs_cols, run_date, monitoring)

    # Drop the 'prescription_scanned_pages' column since it's no longer needed
    hundred_percent_df = hundred_percent_df.drop("Κατηγορία", axis=1)

    return hundred_percent_df


def get_other_documents(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Apply the negation of all other conditions
    others_df = pages[pages.category.isin([3, 4, 8])].copy()
    others_df["justification"] = None  # This might need to be set based on other conditions
    # Assign 'justification' based on 'category'
    others_df.loc[others_df.category == 3, "justification"] = COASTGUARD
    others_df.loc[others_df.category == 4, "justification"] = EU_CITYZEN
    # For category 8, assign the corresponding 'category_name'
    others_df.loc[others_df.category == 8, "justification"] = others_df.loc[others_df.category == 8, "category_name"]

    # Define the columns to be used and process the DataFrame as before
    remove_docs_cols = [
        "scan_prescription_full",
        "type",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "category_name",
        "justification",
        "prescription_scanned_pages",
    ]
    others_df = process_remove_documents(others_df, remove_docs_cols, run_date, monitoring)
    return others_df


def get_digital_doctor_documents(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Apply the condition for digital == True and type == "doctor" and set justification
    digital_doctor_df = pages[(pages.digital == True) & (pages.type == "doctor")].copy()
    digital_doctor_df["justification"] = INTANGIBLE_PRESCR

    # Define the columns to be used and process the DataFrame as before
    remove_docs_cols = [
        "scan_prescription_full",
        "type",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "category_name",
        "justification",
        "prescription_scanned_pages",
    ]
    digital_doctor_df = process_remove_documents(digital_doctor_df, remove_docs_cols, run_date, monitoring)

    return digital_doctor_df


# Remove Docs
def get_documents_to_be_removed(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Apply the negation of all other conditions
    remove_docs_df = pages[
        (pages.category.isin([2, 3, 4, 8])) | (pages["document_type"] == "injection") | (pages["100%"] == True)
    ].copy()
    remove_docs_df["justification"] = None  # This might need to be set based on other conditions
    # Assign 'justification' based on 'category'
    remove_docs_df.loc[
        (remove_docs_df["category"] == 2) | (remove_docs_df["document_type"] == "injection"), "justification"
    ] = INJECTIONS
    remove_docs_df.loc[remove_docs_df.category == 3, "justification"] = COASTGUARD
    remove_docs_df.loc[remove_docs_df.category == 4, "justification"] = EU_CITYZEN
    # For category 8, assign the corresponding 'category_name'
    remove_docs_df.loc[remove_docs_df.category == 8, "justification"] = remove_docs_df.loc[
        remove_docs_df.category == 8, "category_name"
    ]
    remove_docs_df.loc[pages["100%"] == True, "justification"] = FULL_PARTICIPATION
    # Define the columns to be used and process the DataFrame as before
    remove_docs_cols = [
        "scan_prescription_full",
        "type",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "category_name",
        "justification",
        "prescription_scanned_pages",
    ]
    remove_docs_df = process_remove_documents(remove_docs_df, remove_docs_cols, run_date, monitoring)

    return remove_docs_df


def process_remove_documents(
    process_remove_documents_df: pd.DataFrame, cols: List[str], run_date: date, monitoring: Monitoring
) -> DataFrame:
    # Assuming map_to_image_link is a function defined elsewhere that maps file names to image links
    if not process_remove_documents_df.empty:
        process_remove_documents_df["scan_prescription_full"] = process_remove_documents_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )

    # Convert the timestamp to time
    process_remove_documents_df["pr_order_timestamp"] = process_remove_documents_df["pr_order_timestamp"].dt.time

    # Replace "type" values with Greek text equivalents
    process_remove_documents_df["type"] = process_remove_documents_df["type"].replace("doctor", "Πρωτότυπο")
    process_remove_documents_df["type"] = process_remove_documents_df["type"].str.replace("pharmacist", "Εκτέλεση")

    # Filter the DataFrame based on the columns specified
    process_remove_documents_df = process_remove_documents_df[
        process_remove_documents_df.justification.notna()
        & process_remove_documents_df.prescription_scanned_pages.notna()
    ][cols].drop_duplicates(subset="scan_prescription_full")

    # Drop the 'prescription_scanned_pages' column since it's no longer needed
    process_remove_documents_df = process_remove_documents_df.drop("prescription_scanned_pages", axis=1)

    process_remove_documents_df = process_remove_documents_df.sort_values(by="stack_number", ascending=True)

    process_remove_documents_df["doc_name"] = process_remove_documents_df["doc_name"].fillna("-")
    # Rename the columns to the desired names in Greek
    process_remove_documents_df.columns = [
        "Αριθμός συνταγής",
        "Τύπος συνταγής",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
        "Ασφαλιστικός Φορέας",
        "Κατηγορία",
    ]
    return process_remove_documents_df


def get_pharmacist_missing_pages(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    pharmacist_missing_pages_cols = [
        "scan_prescription_full",
        "pages",
        "page",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "group",
        "prescription_scanned_pages",
        "pdf_file_name",
    ]
    pages["group"] = None
    pages.loc[pages.category == 1, "group"] = pages.loc[pages.category == 1, "category_name"]
    pages.loc[pages.category == 2, "group"] = INJECTIONS
    pages.loc[pages.category == 3, "group"] = COASTGUARD
    pages.loc[pages.category == 4, "group"] = EU_CITYZEN
    pages.loc[pages.category == 8, "group"] = pages.loc[pages.category == 8, "category_name"]
    pages.loc[pages["100%"] == True, "group"] = FULL_PARTICIPATION
    pages.loc[(pages.digital == True) & (pages.type == "doctor"), "group"] = INTANGIBLE_PRESCR

    pharmacist_missing_pages_df = pages[(pages.type == "pharmacist") & (pages["scan_prescription_full"].notna())][
        pharmacist_missing_pages_cols
    ]
    grouped = pharmacist_missing_pages_df.groupby("scan_prescription_full")
    grouped_agg = grouped.agg({"scan_prescription_full": "count", "pages": "max"})
    grouped_agg_df = grouped_agg[grouped_agg["scan_prescription_full"] < grouped_agg["pages"]]
    index = grouped_agg_df.index
    pharmacist_missing_pages_df = pharmacist_missing_pages_df[
        pharmacist_missing_pages_df["scan_prescription_full"].isin(index)
        & pharmacist_missing_pages_df["scan_prescription_full"].notna()
    ]
    if not pharmacist_missing_pages_df.empty:
        pharmacist_missing_pages_df["scan_prescription_full"] = pharmacist_missing_pages_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    pharmacist_missing_pages_df["pr_order_timestamp"] = pharmacist_missing_pages_df["pr_order_timestamp"].dt.time
    pharmacist_missing_pages_df = pharmacist_missing_pages_df.drop(
        ["pages", "prescription_scanned_pages", "pdf_file_name"], axis=1
    )
    pharmacist_missing_pages_df.columns = [
        "Αριθμός συνταγής",
        "Αναγνωρισμένη σελίδα",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
        "Κατηγορία",
    ]
    return pharmacist_missing_pages_df


# TODO: Duplicate pages based on the code above?


def get_dosage_issues(dosages: pd.DataFrame, pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    dosage_columns = [
        "prescription",
        "scan_last_three_digits",
        "dosage_description",
        "description",
        "boxes_provided",
        "boxes_provided_multiple_executions",
    ]
    dosage_check_df = dosages[(dosages.dosage_check == "False") & (dosages.dosage_description.notna())][dosage_columns]

    dosage_check_df["scan_prescription_full"] = dosage_check_df["prescription"].astype(str) + dosage_check_df[
        "scan_last_three_digits"
    ].astype(str)
    dosage_check_df = (
        dosage_check_df.drop("scan_last_three_digits", axis=1)
        .drop("prescription", axis=1)
        .reindex(
            columns=[
                "scan_prescription_full",
                "dosage_description",
                "description",
                "boxes_provided",
                "boxes_provided_multiple_executions",
            ]
        )
    )

    pharmacist_only_pages_columns = [
        "scan_prescription_full",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "100%",
        "stack_number",
        "prescription_scanned_pages",
        "pdf_file_name",
    ]
    pharmacist_only_pages_df = pages[(pages.type == "pharmacist")][pharmacist_only_pages_columns]
    pharmacist_only_pages_df["scan_prescription_full"] = pages["prescription"].astype(str) + pages[
        "scan_last_three_digits"
    ].astype(str)

    merged_df = dosage_check_df.merge(
        pharmacist_only_pages_df[
            [
                "scan_prescription_full",
                "patient_name",
                "stack_number",
                "prescription_scanned_pages",
                "pdf_file_name",
                "100%",
            ]
        ],
        on="scan_prescription_full",
        how="left",
    )

    merged_df = merged_df[merged_df["100%"] == False]
    merged_df = merged_df.drop("100%", axis=1)

    if not merged_df.empty:
        merged_df["prescription"] = merged_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    merged_df = merged_df.drop("pdf_file_name", axis=1)
    merged_df = (
        merged_df.drop("prescription_scanned_pages", axis=1)
        .drop("scan_prescription_full", axis=1)
        .drop_duplicates()
        .reindex(
            columns=[
                "prescription",
                "dosage_description",
                "description",
                "boxes_provided",
                "boxes_provided_multiple_executions",
                "patient_name",
                "stack_number",
            ]
        )
    )

    merged_df.columns = [
        "Αριθμός συνταγής",
        "Δοσολογία",
        "Περιγραφή φαρμάκου",
        "Ποσότητα Εκτέλεσης",
        "Συνολική Εκτελεσμένη Ποσότητα",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
    ]
    return merged_df


def get_missing_pharmacist_prescriptions(pages: DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    missing_pharm_presciptions_cols = [
        "prescription",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "pdf_file_name",
        "pharmacist_idika_prescription_full",
        "category_name",
        "group",
    ]

    pages["group"] = None
    pages.loc[pages.category == 1, "group"] = EOPYY_BENEFICIARY
    pages.loc[pages.category == 2, "group"] = INJECTIONS
    pages.loc[pages.category == 3, "group"] = COASTGUARD
    pages.loc[pages.category == 4, "group"] = EU_CITYZEN
    pages.loc[pages.category == 8, "group"] = pages.loc[pages.category == 8, "category_name"]
    pages.loc[pages["100%"] == True, "group"] = FULL_PARTICIPATION
    pages.loc[pages["document_type"] == "injection", "group"] = "Διενέργεια Εμβολίου"
    pages.loc[(pages.digital == True) & (pages.type == "doctor"), "group"] = INTANGIBLE_PRESCR

    missing_pharm_prescriptions_df = pages[
        (pages.type == "pharmacist")
        & (pages["100%"] == False)
        & (pages.prescription.notna())
        & (pages.prescription_scanned_pages.isna())
    ][missing_pharm_presciptions_cols]

    if not missing_pharm_prescriptions_df.empty:
        missing_pharm_prescriptions_df["prescription"] = missing_pharm_prescriptions_df.apply(
            lambda row: map_to_pdf_file_name(
                pdf_file_name=row["pdf_file_name"],
                prescription=row["pharmacist_idika_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    missing_pharm_prescriptions_df["pr_order_timestamp"] = missing_pharm_prescriptions_df["pr_order_timestamp"].dt.time
    missing_pharm_prescriptions_df["doc_name"] = missing_pharm_prescriptions_df["doc_name"].fillna("-")

    missing_pharm_prescriptions_df = missing_pharm_prescriptions_df.drop("pdf_file_name", axis=1).drop(
        "pharmacist_idika_prescription_full", axis=1
    )
    missing_pharm_prescriptions_df.columns = [
        "Αριθμός συνταγής",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Ασφαλιστικός Φορέας",
        "Κατηγορία",
    ]
    return missing_pharm_prescriptions_df


def get_missing_pharmacist_no_digital_doctor_detected(
    pages: DataFrame, run_date: date, monitoring: Monitoring
) -> DataFrame:
    missing_pharm_presciptions_existing_doc_cols = [
        "prescription",
        "scan_prescription_full",
        "page",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "prescription_scanned_pages",
        "pdf_file_name",
    ]

    # Filter DataFrame to get unique pharmacist-handled physical
    # prescriptions with execution status 0 or 1
    pharm_no_digital_prescriptions = list(
        pages[
            (pages.type == "pharmacist")
            & (pages.digital == False)
            & (pages["100%"] == False)
            & (pages.scan_prescription_full.isna())
        ].prescription.unique()
    )
    # Filter DataFrame to get unique doctor-handled physical prescriptions
    doctor_no_digital_prescriptions = list(
        pages[
            (pages.type == "doctor")
            & (pages["100%"] == False)
            & (pages.scan_prescription_full.notna())
            & (pages.digital == False)
        ].prescription.unique()
    )
    # Find missing doctor prescriptions
    missing_pharm_prescriptions_existing_doc = set(pharm_no_digital_prescriptions).intersection(
        set(doctor_no_digital_prescriptions)
    )
    # Create a new DataFrame with missing doctor prescriptions and
    # specific columns
    missing_pharm_prescriptions_existing_doc_df = pages[
        (pages.prescription.isin(missing_pharm_prescriptions_existing_doc)) & (pages.type == "doctor")
    ][missing_pharm_presciptions_existing_doc_cols]
    missing_pharm_prescriptions_existing_doc_df = missing_pharm_prescriptions_existing_doc_df[
        missing_pharm_prescriptions_existing_doc_df["prescription_scanned_pages"].notna()
    ]
    if not missing_pharm_prescriptions_existing_doc_df.empty:
        missing_pharm_prescriptions_existing_doc_df[
            "scan_prescription_full"
        ] = missing_pharm_prescriptions_existing_doc_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    missing_pharm_prescriptions_existing_doc_df["pr_order_timestamp"] = missing_pharm_prescriptions_existing_doc_df[
        "pr_order_timestamp"
    ].dt.time
    missing_pharm_prescriptions_existing_doc_df = (
        missing_pharm_prescriptions_existing_doc_df.drop("prescription_scanned_pages", axis=1)
        .drop("prescription", axis=1)
        .drop("pdf_file_name", axis=1)
    )
    missing_pharm_prescriptions_existing_doc_df.columns = [
        "Αριθμός συνταγής",
        "Σελίδα",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
    ]

    return missing_pharm_prescriptions_existing_doc_df


def get_missing_doctor_prescriptions(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    missing_doctor_presciptions_cols = [
        "prescription",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "pdf_file_name",
        "pharmacist_idika_prescription_full",
        "category_name",
        "group",
    ]

    pages["group"] = None
    pages.loc[pages.category == 1, "group"] = EOPYY_BENEFICIARY
    pages.loc[pages.category == 2, "group"] = INJECTIONS
    pages.loc[pages.category == 3, "group"] = COASTGUARD
    pages.loc[pages.category == 4, "group"] = EU_CITYZEN
    pages.loc[pages.category == 8, "group"] = pages.loc[pages.category == 8, "category_name"]
    pages.loc[pages["100%"] == True, "group"] = FULL_PARTICIPATION
    pages.loc[(pages.digital == True) & (pages.type == "doctor"), "group"] = INTANGIBLE_PRESCR

    missing_doctor_prescriptions_df = pages[
        (pages.type == "doctor")
        & (pages["100%"] == False)
        & (pages.prescription.notna())
        & (pages.prescription_scanned_pages.isna())
    ]
    missing_doctor_prescriptions_df = missing_doctor_prescriptions_df.merge(
        pages[(pages.first_execution == True) & (pages.type == "pharmacist")],
        on="prescription",
        how="inner",
        suffixes=("", "_right"),
    )[missing_doctor_presciptions_cols]
    if not missing_doctor_prescriptions_df.empty:
        missing_doctor_prescriptions_df["prescription"] = missing_doctor_prescriptions_df.apply(
            lambda row: map_to_pdf_file_name(
                pdf_file_name=row["pdf_file_name"],
                prescription=row["pharmacist_idika_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    missing_doctor_prescriptions_df = missing_doctor_prescriptions_df.drop("pdf_file_name", axis=1).drop(
        "pharmacist_idika_prescription_full", axis=1
    )
    missing_doctor_prescriptions_df.columns = [
        "Αριθμός συνταγής",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Ασφαλιστικός Φορέας",
        "Κατηγορία",
    ]
    return missing_doctor_prescriptions_df


def get_missing_doctor_no_digital_pharmacist_detected(
    pages: DataFrame, run_date: date, monitoring: Monitoring
) -> DataFrame:
    # Missing NonDigital Doctor Prescriptions whilst there is
    # a pharmacist prescription id detected.

    # Define the list of columns to be used later
    missing_doc_presciptions_existing_pharm_cols = [
        "prescription",
        "scan_prescription_full",
        "page",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "prescription_scanned_pages",
        "pdf_file_name",
    ]

    # Filter DataFrame to get unique pharmacist-handled physical prescriptions
    # with execution status 0 or 1
    pharm_no_digital_prescriptions = list(
        pages[
            (pages.type == "pharmacist")
            & (pages.digital == False)
            & (pages["100%"] == False)
            & (pages.prescription_scanned_pages.notna())
            & (pages.execution.isin([0, 1]))
        ].prescription.unique()
    )
    # Filter DataFrame to get unique doctor-handled physical prescriptions
    doctor_no_digital_prescriptions = list(
        pages[
            (pages.type == "doctor")
            & (pages["100%"] == False)
            & (pages.prescription_scanned_pages.isna())
            & (pages.digital == False)
        ].prescription.unique()
    )
    # Find missing doctor prescriptions
    missing_doc_prescriptions_existing_pharm = set(pharm_no_digital_prescriptions).intersection(
        set(doctor_no_digital_prescriptions)
    )

    # Create a new DataFrame with missing doctor prescriptions
    # and specific columns
    missing_doc_prescriptions_existing_pharm_df = pages[
        (pages.prescription.isin(missing_doc_prescriptions_existing_pharm))
    ][missing_doc_presciptions_existing_pharm_cols]
    missing_doc_prescriptions_existing_pharm_df = missing_doc_prescriptions_existing_pharm_df[
        missing_doc_prescriptions_existing_pharm_df["prescription_scanned_pages"].notna()
    ]
    if not missing_doc_prescriptions_existing_pharm_df.empty:
        missing_doc_prescriptions_existing_pharm_df[
            "scan_prescription_full"
        ] = missing_doc_prescriptions_existing_pharm_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    missing_doc_prescriptions_existing_pharm_df["pr_order_timestamp"] = missing_doc_prescriptions_existing_pharm_df[
        "pr_order_timestamp"
    ].dt.time
    missing_doc_prescriptions_existing_pharm_df = (
        missing_doc_prescriptions_existing_pharm_df.drop("prescription_scanned_pages", axis=1)
        .drop("prescription", axis=1)
        .drop("pdf_file_name", axis=1)
    )
    missing_doc_prescriptions_existing_pharm_df.columns = [
        "Αριθμός συνταγής",
        "Σελίδα",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
    ]
    return missing_doc_prescriptions_existing_pharm_df


def get_negative_manual_check(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    manual_check_columns = [
        "scan_prescription_full",
        "pr_order_timestamp",
        "doc_name",
        "patient_name",
        "stack_number",
        "prescription_scanned_pages",
        "pdf_file_name",
    ]
    manual_check_df = pages[(pages.manual_check == False) & (pages.prescription_scanned_pages.notna())][
        manual_check_columns
    ]
    if not manual_check_df.empty:
        manual_check_df["scan_prescription_full"] = manual_check_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    manual_check_df = manual_check_df.drop("pdf_file_name", axis=1)
    manual_check_df["pr_order_timestamp"] = manual_check_df["pr_order_timestamp"].dt.time
    manual_check_df["doc_name"] = manual_check_df["doc_name"].fillna("-")
    manual_check_df = manual_check_df.drop("prescription_scanned_pages", axis=1)
    manual_check_df.columns = [
        "Αριθμός συνταγής",
        "Ώρα Εκτέλεσης",
        "Ονομ/νυμο Ιατρού",
        "Ονομ/νυμο Ασθενούς",
        "Θέση Στοίβας",
    ]
    return manual_check_df


def get_not_in_idika_scans(pages: DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    not_in_idika_scans_cols = ["scan_prescription_full", "stack_number", "prescription_scanned_pages", "pdf_file_name"]
    not_in_idika_scans_df = pages[(pages.prescription.isna()) & (pages.scan_prescription_full != "0000000000000000")][
        not_in_idika_scans_cols
    ]
    if not not_in_idika_scans_df.empty:
        not_in_idika_scans_df["scan_prescription_full"] = not_in_idika_scans_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    not_in_idika_scans_df = not_in_idika_scans_df.drop("prescription_scanned_pages", axis=1)
    not_in_idika_scans_df = not_in_idika_scans_df.drop("pdf_file_name", axis=1)
    not_in_idika_scans_df.columns = ["Αριθμός συνταγής", "Θέση Στοίβας"]
    return not_in_idika_scans_df


def not_detected_barcodes(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    not_detected_barcodes_cols = [
        "prescription_scanned_pages",
        "scan_prescription_full",
        "stack_number",
        "pdf_file_name",
    ]
    not_detected_barcodes_df = pages[(pages.scan_prescription_full == "0000000000000000")][not_detected_barcodes_cols]
    # not_detected_barcodes_df['column_name'] = \
    # not_detected_barcodes_df['prescription_scanned_pages']
    if not not_detected_barcodes_df.empty:
        not_detected_barcodes_df["prescription_scanned_pages"] = not_detected_barcodes_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["prescription_scanned_pages"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    not_detected_barcodes_df = not_detected_barcodes_df.drop("pdf_file_name", axis=1)
    # not_detected_barcodes_df.drop('prescription_scanned_pages',
    # axis=1, inplace=True)
    not_detected_barcodes_df = not_detected_barcodes_df.drop("scan_prescription_full", axis=1)
    not_detected_barcodes_df.columns = ["Όνομα αρχείου", "Θέση Στοίβας"]
    return not_detected_barcodes_df


def float_precision(number: float, precision: int = 2) -> float:
    return float(f"{number:.{precision}f}")


@dataclass
class DailyAnalytics:
    top_5_doctors: DataFrame
    total_amount: float
    total_insurance_amount: float
    total_patient_amount: float
    total_missing_insurance_amount: float
    total_eopyy_amount: float
    total_missing_eopyy_amount: float
    total_other_funds_amount: float
    total_missing_other_funds_amount: float


def calculate_daily_analytics(pages: DataFrame) -> DailyAnalytics:
    pharmacist_pages = pages[pages["type"] == "pharmacist"].copy()

    pharmacist_pages["doc_name"] = pharmacist_pages["doc_name"].fillna("-")
    # ignore duplicates in the scanned package
    pharmacist_pages = pharmacist_pages.drop_duplicates(subset="pharmacist_idika_prescription_full")
    pharmacist_pages["patient_amount"] = pharmacist_pages["patient_amount"].astype(float)
    pharmacist_pages["insurance_amount"] = pharmacist_pages["insurance_amount"].astype(float)
    pharmacist_pages["total_amount"] = pharmacist_pages["insurance_amount"] + pharmacist_pages["patient_amount"]

    # calculate totals start
    total_insurance_amount = pharmacist_pages["insurance_amount"].sum()
    total_patient_amount = pharmacist_pages["patient_amount"].sum()
    total_amount = total_insurance_amount + total_patient_amount
    # calculate totals end

    # calculate missing amounts start

    missing_pharmacist_prescription_pages = pharmacist_pages[
        (pharmacist_pages.prescription.notna()) & (pharmacist_pages.prescription_scanned_pages.isna())
    ]
    total_missing_insurance_amount = missing_pharmacist_prescription_pages["insurance_amount"].sum()

    # calculate missing amounts end

    # calculate eopyy and other funds amounts start

    eopyy = pharmacist_pages[
        (pharmacist_pages["category"] == 1.0)
        | (pharmacist_pages["category"] == 2.0)
        | (pharmacist_pages["category"] == 3.0)
        | (pharmacist_pages["category"] == 4.0)
        | (pharmacist_pages["category"] == 5.0)
    ]

    other_funds = pharmacist_pages[pharmacist_pages["category"] == 8.0]

    missing_eopyy = eopyy[(eopyy.prescription.notna()) & (eopyy.prescription_scanned_pages.isna())]

    missing_other_funds = other_funds[
        (other_funds.prescription.notna()) & (other_funds.prescription_scanned_pages.isna())
    ]

    total_eopyy_amount = eopyy["insurance_amount"].sum()
    total_other_funds_amount = other_funds["insurance_amount"].sum()
    total_missing_other_funds_amount = missing_other_funds["insurance_amount"].sum()
    total_missing_eopyy_amount = missing_eopyy["insurance_amount"].sum()

    # calculate eopyy and other funds amounts end

    # top_5_doctors start
    by_doc = (
        pharmacist_pages.groupby("doc_name")
        .agg(
            {
                "pharmacist_idika_prescription_full": "nunique",
                "insurance_amount": "sum",
                "total_amount": "sum",
            }
        )
        .reset_index()
        .sort_values("pharmacist_idika_prescription_full", ascending=False)
    )

    by_doc["insurance_amount"] = by_doc["insurance_amount"].apply(format_currency)
    by_doc["total_amount"] = by_doc["total_amount"].apply(format_currency)
    by_doc = by_doc[by_doc["doc_name"] != "-"]

    top_5_doctors = (
        by_doc[["doc_name", "pharmacist_idika_prescription_full", "total_amount", "insurance_amount"]]
        .head(5)
        .rename(
            columns={
                "doc_name": "Ονομ/νυμο Ιατρού",
                "pharmacist_idika_prescription_full": "Αριθμός συνταγών",
                "total_amount": "Συνολικό Ποσό",
                "insurance_amount": "Πληρωτέο ποσό (ταμείο)",
            }
        )
    )
    # top_5_doctors end

    return DailyAnalytics(
        top_5_doctors=top_5_doctors,
        total_amount=float_precision(total_amount),
        total_patient_amount=float_precision(total_patient_amount),
        total_insurance_amount=float_precision(total_insurance_amount),
        total_missing_insurance_amount=float_precision(total_missing_insurance_amount),
        total_eopyy_amount=float_precision(total_eopyy_amount),
        total_other_funds_amount=float_precision(total_other_funds_amount),
        total_missing_other_funds_amount=float_precision(total_missing_other_funds_amount),
        total_missing_eopyy_amount=float_precision(total_missing_eopyy_amount),
    )


def log_data(
    barcode_not_found_docs: int,
    category_1_docs: int,
    category_1_pres: int,
    category_2_docs: int,
    category_2_pres: int,
    category_3_docs: int,
    category_3_pres: int,
    category_4_docs: int,
    category_4_pres: int,
    category_8_docs: int,
    category_8_pres: int,
    digital_prescriptions: int,
    digital_prescriptions_docs: int,
    hundred_perc_docs: int,
    hundred_perc_pres: int,
    prescriptions: int,
    prescriptions_docs: int,
    scanned_docs: int,
    monitoring: Monitoring,
) -> None:
    monitoring.logger_adapter.warning(f"Σαρωμένα έγγραφα {scanned_docs}")
    monitoring.logger_adapter.info(f"Αναγνωρισμένα Έγγραφα συνταγών {prescriptions_docs}")
    monitoring.logger_adapter.info(f"Μη αναγνωρισμένα έγγραφα συνταγών {barcode_not_found_docs}")
    monitoring.logger_adapter.info(f"Άυλα Έγγραφα συνταγών {digital_prescriptions_docs}")
    monitoring.logger_adapter.warning(f"Συνταγές {prescriptions}")
    monitoring.logger_adapter.info(f"Άυλες συνταγές {digital_prescriptions}")
    monitoring.logger_adapter.info(f"category 1 συνταγές {category_1_pres}")
    monitoring.logger_adapter.info(f"category 1 έγγραφα {category_1_docs}")
    monitoring.logger_adapter.info(f"category 2 συνταγές {category_2_pres}")
    monitoring.logger_adapter.info(f"category 2 έγγραφα {category_2_docs}")
    monitoring.logger_adapter.info(f"category 3 συνταγές {category_3_pres}")
    monitoring.logger_adapter.info(f"category 3 έγγραφα {category_3_docs}")
    monitoring.logger_adapter.info(f"category 4 συνταγές {category_4_pres}")
    monitoring.logger_adapter.info(f"category 4 έγγραφα {category_4_docs}")
    monitoring.logger_adapter.info(f"category 8 συνταγές {category_8_pres}")
    monitoring.logger_adapter.info(f"category 8 έγγραφα {category_8_docs}")
    monitoring.logger_adapter.info(f"100% συνταγές {hundred_perc_pres}")
    monitoring.logger_adapter.info(f"100% έγγραφα {hundred_perc_docs}")


# Note: for prescription arguments, use the following order of preference:
# Use scan_prescription_full for documents in the scanned documents, initialized at the beginning of get_report_data
# Use pharmacist_idika_prescription_full in case the document is not scanned, part of pages
def map_to_image_link(
    file_name: str, pdf_file_name: str, prescription: str, run_date: date, monitoring: Monitoring
) -> str:
    # initialize with prescription text
    image_link = prescription
    if not pd.isna(file_name):
        file: Path = config.get_scan_dir(run_date) / file_name
        monitoring.logger_adapter.info(f"map_to_image | , filename:, {file_name}, file:, {file}")
        if file.exists():
            file_path: str = (config.get_scan_dir(run_date) / file_name).as_posix()
            image_link = f'<a href="{file_path}">{prescription}</a>'
    else:
        # set pdf link
        image_link = map_to_pdf_file_name(pdf_file_name, prescription, run_date, monitoring)
        monitoring.logger_adapter.warning(f"{prescription}:map_to_image_link: file_name not found")
    return image_link


def map_to_pdf_file_name(pdf_file_name: str, prescription: str, run_date: date, monitoring: Monitoring) -> str:
    download_dir = config.get_download_dir(run_date)
    pattern = f"{download_dir}/*/{pdf_file_name}"
    matches = glob.glob(pattern)
    if not matches:
        monitoring.logger_adapter.warning(f"{prescription}:map_to_pdf_file_name: No matching files found.")
        return prescription
    matches.sort()
    first_match = matches[0]
    file_path: str = (config.get_download_dir(run_date) / first_match).as_posix()
    pdf_file_link: str = f'<a href="{file_path}">{prescription}</a>'
    return pdf_file_link


def get_succesiveness_issues(pages: pd.DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    # Keep necessary rows
    suc_df = pages[
        ~((pages["100%"]) | (pages.prescription.isna()) | (pages.stack_number.isna()) | (pages.type.isna()))
    ].copy()
    # Exclude partial executions
    suc_df = suc_df[~(suc_df.scan_last_three_digits.str[-1].astype(int) > 1)]
    # Start stack number from 1
    if suc_df.stack_number.min() == 0:
        suc_df.stack_number = suc_df.stack_number + 1
    # Keep similar sorting while ordering within each prediction
    unique_pres = list(suc_df.prescription.unique())
    suc_df["custom_sort"] = suc_df.prescription.apply(lambda x: unique_pres.index(x))
    suc_df = suc_df.sort_values(by=["custom_sort", "type", "page"], ascending=[True, False, True])
    suc_df.loc[suc_df.prescription == 0, "prescription"] = np.nan
    suc_df = suc_df.drop("custom_sort", axis=1)
    # Get the correct internal (within prescription) position
    suc_df["correct_internal_pos"] = suc_df.groupby("prescription").cumcount()
    # Get the stack number of the first page per prescription
    first_page_stack_number = suc_df[suc_df.correct_internal_pos == 0][
        ["prescription", "stack_number"]
    ].drop_duplicates()
    first_page_stack_number = first_page_stack_number.rename(columns={"stack_number": "first_page_stack_number"})
    suc_df = suc_df.merge(first_page_stack_number, how="left", on="prescription")
    # Get the correct stack number per page
    suc_df.loc[~suc_df.prescription.isna(), "correct_stack_number"] = (
        suc_df.first_page_stack_number + suc_df.correct_internal_pos
    )
    # Exclude doctor pages
    suc_df = suc_df[suc_df.type == "pharmacist"]
    # Get pages whose stack number does not match with the correct one
    # cols = ['prescription', 'scan_prescription_full', 'type', 'page', 'stack_number', 'correct_stack_number']
    cols = ["scan_prescription_full", "pr_order_timestamp", "doc_name", "patient_name", "stack_number", "pdf_file_name"]
    incorrect_ordering_pres = suc_df[suc_df.stack_number != suc_df.correct_stack_number].prescription.unique()
    suc_df[suc_df.prescription.isin(incorrect_ordering_pres)][cols].drop_duplicates(subset="prescription")
    if not suc_df.empty:
        suc_df["scan_prescription_full"] = suc_df.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                pdf_file_name=row["pdf_file_name"],
                prescription=row["scan_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    # suc_issues_df = suc_issues_df.drop(["prescription_scanned_pages", "type", "page"], axis=1)
    suc_df = suc_df.drop(["pdf_file_name"], axis=1)
    rename_cols = {
        "scan_prescription_full": "Αριθμός συνταγής",
        "pr_order_timestamp": "Ώρα Εκτέλεσης",
        "type": "Κατηγορία",
        "page": "Αριθμός σελίδας",
        "doc_name": "Ονομ/νυμο Ιατρού",
        "patient_name": "Ονομ/νυμο Ασθενούς",
        "stack_number": "Θέση στοίβας",
        "correct_stack_number": "Διορθωμένη θέση στοίβας",
    }
    display_cols = [rename_cols[col] for col in cols]
    return suc_df.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]


def find_min_moves_for_sorting(
    df: pd.DataFrame, desired_order: List[int], current_order: List[int]
) -> Tuple[int, pd.DataFrame]:
    total_moves = 0
    move_instructions = []
    working_order = current_order.copy()
    # TODO:
    #  check that both lists have the same length
    #  or pass dataframe (with specified schema) and extract lists internally

    for desired_pos, doc_id in enumerate(desired_order, start=1):
        if doc_id in working_order:
            current_pos = working_order.index(doc_id) + 1
            if current_pos != desired_pos:
                working_order.pop(current_pos - 1)  # Remove from current position
                working_order.insert(desired_pos - 1, doc_id)  # Insert to desired position
                total_moves += 1

                move_before = "End" if desired_pos >= len(desired_order) else desired_order[desired_pos]
                move_instructions.append(
                    {
                        "prescription_to_move": doc_id,
                        "current_index": df.index[df["pharmacist_idika_prescription_full"] == doc_id].tolist()[0] + 1,
                        "prescription_to_move_before": move_before,
                        "desired_index": desired_pos,
                    }
                )

    instructions_df = pd.DataFrame(
        move_instructions,
        columns=["prescription_to_move", "current_index", "prescription_to_move_before", "desired_index"],
    )
    return total_moves, instructions_df


def execution_time_ordering(
    pages: DataFrame, injections: bool, run_date: date, monitoring: Monitoring
) -> Tuple[int, DataFrame, Styler, Styler]:
    if injections:
        unique_idika_pages_df = pages[
            (pages.type == "pharmacist")
            & (pages["100%"] == False)
            & ((pages["category"] == 2) | (pages["document_type"] == "injection"))
        ]
        unique_scan_pages_df = pages[
            (pages.type == "pharmacist")
            & (pages["100%"] == False)
            & ((pages["category"] == 2) | (pages["document_type"] == "injection"))
        ]
    else:
        unique_idika_pages_df = pages[
            (pages.type == "pharmacist")
            & (pages["100%"] == False)
            & (pages["category"] == 1)
            & (pages["document_type"] != "injection")
        ]
        unique_scan_pages_df = pages[
            (pages.type == "pharmacist")
            & (pages["100%"] == False)
            & (pages["category"] == 1)
            & (pages["document_type"] != "injection")
        ]

    unique_idika_pages_df = (
        unique_idika_pages_df[["pharmacist_idika_prescription_full", "scan_prescription_full", "pr_order_timestamp"]]
        .drop_duplicates(subset="pharmacist_idika_prescription_full")
        .sort_values(by=["pr_order_timestamp", "pharmacist_idika_prescription_full"], ascending=[True, True])
    )
    unique_idika_pages_df = unique_idika_pages_df.reset_index(drop=True)
    unique_idika_pages_df["desired_index"] = unique_idika_pages_df.index

    unique_scan_pages_df = (
        unique_scan_pages_df[
            ["pharmacist_idika_prescription_full", "scan_prescription_full", "pr_order_timestamp", "stack_number"]
        ]
        .dropna(subset=["scan_prescription_full"])
        .drop_duplicates(subset="scan_prescription_full")
        .sort_values("stack_number")
    )
    unique_scan_pages_df = unique_scan_pages_df.reset_index(drop=True)
    unique_scan_pages_df["current_index"] = unique_scan_pages_df.index

    df = unique_idika_pages_df.merge(
        unique_scan_pages_df[["pharmacist_idika_prescription_full", "current_index", "stack_number"]],
        on="pharmacist_idika_prescription_full",
        how="left",
    ).sort_values("current_index")

    # Sort the dataframes by the desired and current indices
    df_desired = df.sort_values("desired_index")
    df_current = df.sort_values("current_index")

    # Prepare the orders as before
    # Extract the 'prescription_id' column as a list to get the order lists
    desired_order = df_desired["pharmacist_idika_prescription_full"].tolist()
    current_order = df_current["pharmacist_idika_prescription_full"].tolist()

    # TODO: move function outside the function

    # Find minimum moves and the sequence
    # min_moves, moves_df = find_list_with_positions(df, desired_order, current_order)

    min_moves, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

    moves_df1 = moves_df.merge(
        pages[["pharmacist_idika_prescription_full", "pdf_file_name", "patient_name"]],
        how="left",
        left_on="prescription_to_move",
        right_on="pharmacist_idika_prescription_full",
    )
    moves_df1 = moves_df1.merge(
        pages[["pharmacist_idika_prescription_full", "pdf_file_name", "patient_name"]],
        how="left",
        left_on="prescription_to_move_before",
        right_on="pharmacist_idika_prescription_full",
    )
    moves_df1 = moves_df1.drop(columns=["pharmacist_idika_prescription_full_x", "pharmacist_idika_prescription_full_y"])
    moves_df1["current_index"] = moves_df1["current_index"] + 1
    moves_df1["desired_index"] = moves_df1["desired_index"] + 1

    moves_df1["current_index"] = moves_df1["current_index"].astype(pd.Int64Dtype())
    moves_df1["desired_index"] = moves_df1["desired_index"].astype(pd.Int64Dtype())

    moves_column_reindex_df = moves_df1.reindex(
        columns=[
            "prescription_to_move",
            "patient_name_x",
            "current_index",
            "prescription_to_move_before",
            "patient_name_y",
            "desired_index",
            "pdf_file_name_x",
            "pdf_file_name_y",
        ]
    )
    moves_column_reindex_df = moves_column_reindex_df.rename(
        columns={
            "patient_name_x": "patient_name_to_move",
            "patient_name_y": "patient_name_to_move_before",
            "pdf_file_name_x": "pdf_file_name_to_move",
            "pdf_file_name_y": "pdf_file_name_to_move_before",
        }
    )

    if not moves_column_reindex_df.empty:
        moves_column_reindex_df["prescription_to_move"] = moves_column_reindex_df.apply(
            lambda row: map_to_pdf_file_name(
                pdf_file_name=row["pdf_file_name_to_move"],
                prescription=row["prescription_to_move"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )

    if not moves_column_reindex_df.empty:
        moves_column_reindex_df["prescription_to_move_before"] = moves_column_reindex_df.apply(
            lambda row: map_to_pdf_file_name(
                pdf_file_name=row["pdf_file_name_to_move_before"],
                prescription=row["prescription_to_move_before"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )

    moves_column_reindex_df = moves_column_reindex_df.drop(
        columns=["pdf_file_name_to_move", "pdf_file_name_to_move_before"]
    ).drop_duplicates(subset="prescription_to_move")
    moves_column_reindex_df["patient_name_to_move_before"] = moves_column_reindex_df[
        "patient_name_to_move_before"
    ].fillna("-")
    moves_column_reindex_df = moves_column_reindex_df.rename(
        columns={
            "prescription_to_move": "Ανακατάταξη συνταγής",
            "current_index": "Τρέχουσα θέση",
            "patient_name_to_move": "Όνομ/νυμο ασθενούς συνταγής προς ανακατάταξη",
            "prescription_to_move_before": "Συνταγή αναφοράς (τοποθέτηση πριν απο συνταγή)",
            "desired_index": "Επιθυμητή θέση",
            "patient_name_to_move_before": "Όνομ/νυμο ασθενούς συνταγής αναφοράς",
        }
    )
    # Create a new dataframe similar to moves_column_reindex_df for all prescriptions
    all_prescriptions_df = df_desired.copy()
    all_prescriptions_df = all_prescriptions_df.merge(
        pages[["pharmacist_idika_prescription_full", "pdf_file_name", "patient_name"]],
        how="left",
        left_on="pharmacist_idika_prescription_full",
        right_on="pharmacist_idika_prescription_full",
    )
    all_prescriptions_df["desired_index"] += 1
    all_prescriptions_df["current_index"] += 1

    # Add 'move' column to indicate whether each prescription needs to be moved
    all_prescriptions_df["move"] = all_prescriptions_df["pharmacist_idika_prescription_full"].isin(
        moves_df["prescription_to_move"]
    )
    # all_prescriptions_df['move'] = all_prescriptions_df['move'].map({True: True, False: False})
    #   # Convert Boolean to Yes/No
    all_prescriptions_df = all_prescriptions_df.drop_duplicates(subset="pharmacist_idika_prescription_full")

    all_prescriptions_df = all_prescriptions_df[
        [
            "desired_index",
            "current_index",
            "pharmacist_idika_prescription_full",
            "pdf_file_name",
            "patient_name",
            "pr_order_timestamp",
            "move",
        ]
    ]
    all_prescriptions_df["desired_index"] = all_prescriptions_df["desired_index"].astype(pd.Int64Dtype())
    all_prescriptions_df["current_index"] = all_prescriptions_df["current_index"].astype(pd.Int64Dtype())

    if not all_prescriptions_df.empty:
        all_prescriptions_df["pharmacist_idika_prescription_full"] = all_prescriptions_df.apply(
            lambda row: map_to_pdf_file_name(
                pdf_file_name=row["pdf_file_name"],
                prescription=row["pharmacist_idika_prescription_full"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
    all_prescriptions_df["pr_order_timestamp"] = all_prescriptions_df["pr_order_timestamp"].dt.time
    all_prescriptions_df_current_index = all_prescriptions_df.copy()
    all_prescriptions_df_current_index.set_index("current_index")
    all_prescriptions_df_current_index = all_prescriptions_df_current_index.sort_values("current_index")

    all_prescriptions_df = all_prescriptions_df.drop(columns=["pdf_file_name", "current_index"]).rename(
        columns={
            "desired_index": "Σειρά",
            "pharmacist_idika_prescription_full": "Συνταγή",
            "pdf_file_name": "html_link_to_file",
            "patient_name": "Όνομ/νυμο ασθενούς",
            "pr_order_timestamp": "Ώρα εκτέλεσης",
            "move": "move",
        }
    )
    all_prescriptions_df_current_index["current_index"] = all_prescriptions_df_current_index["current_index"].astype(
        str
    )
    all_prescriptions_df_current_index["current_index"] = all_prescriptions_df_current_index["current_index"].replace(
        "<NA>", "-"
    )
    all_prescriptions_df_current_index = all_prescriptions_df_current_index.drop(
        columns=["pdf_file_name", "desired_index", "pr_order_timestamp"]
    ).rename(
        columns={
            "current_index": "Θέση",
            "pharmacist_idika_prescription_full": "Συνταγή",
            "pdf_file_name": "html_link_to_file",
            "patient_name": "Όνομ/νυμο ασθενούς",
            "move": "move",
        }
    )

    def highlight_rows_based_on_boolean_green(data: DataFrame) -> List[str]:
        color = "#8fce00" if data["move"] else ""
        attr = f"background-color: {color}"
        return [attr] * len(data)

    def highlight_rows_based_on_boolean_red(data: DataFrame) -> List[str]:
        color = "#EA9999" if data["move"] else ""
        attr = f"background-color: {color}"
        return [attr] * len(data)

    styles_1 = [
        dict(selector="th", props=[("font-size", "7pt")]),
        dict(selector="td", props=[("font-size", "7pt")]),
        dict(selector="tr", props=[("height", "20px")]),
        dict(selector="th.col_heading.level0.col4", props=[("display", "none")]),  # hiding the move column
        dict(selector="td.col4", props=[("display", "none")]),  # hiding the move column
    ]
    styles_2 = [
        dict(selector="th", props=[("font-size", "7pt")]),
        dict(selector="td", props=[("font-size", "7pt")]),
        dict(selector="tr", props=[("height", "20px")]),
        dict(selector="th.col_heading.level0.col3", props=[("display", "none")]),  # hiding the move column
        dict(selector="td.col3", props=[("display", "none")]),  # hiding the move column
    ]
    all_prescriptions_df = (
        all_prescriptions_df.style.apply(highlight_rows_based_on_boolean_green, axis=1)
        .set_table_styles(styles_1)
        .hide(axis="index")
    )
    all_prescriptions_df_current_index = (
        all_prescriptions_df_current_index.style.apply(highlight_rows_based_on_boolean_red, axis=1)
        .set_table_styles(styles_2)
        .hide(axis="index")
    )

    return min_moves, moves_column_reindex_df, all_prescriptions_df, all_prescriptions_df_current_index


def get_above_fyk_limit(
    pages: pd.DataFrame, partial_prescription_summaries: pd.DataFrame, run_date: date, monitoring: Monitoring
) -> pd.DataFrame:
    try:
        above_fyk_limit = partial_prescription_summaries[
            partial_prescription_summaries["contains_high_cost_drug_above_limit"] == True
        ]

        pharmacist_pages = pages[pages["type"] == "pharmacist"].copy()
        pharmacist_pages["pr_order_timestamp"] = pharmacist_pages["pr_order_timestamp"].apply(lambda x: x.time())
        pharmacist_pages["stack_number"] = pharmacist_pages["stack_number"].apply(
            lambda x: str(x) if not pd.isna(x) else "-"
        )
        df_merged = pharmacist_pages.merge(above_fyk_limit, on=["prescription", "execution"], how="inner")
        df_merged["pharmacist_idika_prescription_full"] = df_merged.apply(
            lambda row: map_to_image_link(
                file_name=row["prescription_scanned_pages"],
                prescription=row["pharmacist_idika_prescription_full"],
                pdf_file_name=row["pdf_file_name"],
                run_date=run_date,
                monitoring=monitoring,
            ),
            axis=1,
        )
        columns = [
            "pharmacist_idika_prescription_full",
            "stack_number",
            "patient_name",
            "doc_name",
            "pr_order_timestamp",
        ]

        rename_cols = {
            "pharmacist_idika_prescription_full": "Αριθμός συνταγής",
            "pr_order_timestamp": "Ώρα Εκτέλεσης",
            "doc_name": "Ονομ/νυμο Ιατρού",
            "patient_name": "Ονομ/νυμο Ασθενούς",
            "stack_number": "Θέση στοίβας",
        }
        display_cols = [rename_cols[col] for col in columns]

        above_fyk_limit = df_merged.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]
        if above_fyk_limit.shape[0] > 0:
            monitoring.logger_adapter.info("Prescription containing drug above fyk limit found")
            monitoring.logger_adapter.exception(
                AboveFykLimitPrescriptionFoundException("Informative Exception: This does not stop the process")
            )
        return df_merged.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]
    except Exception as e:
        monitoring.logger_adapter.error("failed to get above fyk limit prescriptions")
        monitoring.logger_adapter.exception(e)
        return DataFrame(
            columns=["Αριθμός συνταγής", "Ώρα Εκτέλεσης", "Ονομ/νυμο Ιατρού", "Ονομ/νυμο Ασθενούς", "Θέση στοίβας"]
        )


def get_prescriptions_amount(pages: DataFrame, run_date: date, monitoring: Monitoring) -> DataFrame:
    pharmacist_pages = pages[pages["type"] == "pharmacist"].copy()
    pharmacist_pages["pr_order_timestamp"] = pharmacist_pages["pr_order_timestamp"].apply(lambda x: x.time())
    pharmacist_pages["stack_number"] = pharmacist_pages["stack_number"].apply(
        lambda x: str(x) if not pd.isna(x) else "-"
    )
    pharmacist_pages["insurance_amount"] = pharmacist_pages["insurance_amount"].astype(float)
    pharmacist_pages["patient_amount"] = pharmacist_pages["patient_amount"].astype(float)
    pharmacist_pages["insurance_amount"] = pharmacist_pages["insurance_amount"].apply(
        lambda x: format_currency(x) if pd.notna(x) else "-"
    )
    pharmacist_pages["patient_amount"] = pharmacist_pages["patient_amount"].apply(
        lambda x: format_currency(x) if pd.notna(x) else "-"
    )
    pharmacist_pages["doc_name"] = pharmacist_pages["doc_name"].fillna("-")

    # ignore duplicates in the scanned package
    pharmacist_pages = pharmacist_pages.drop_duplicates(subset="pharmacist_idika_prescription_full")

    pharmacist_pages["pharmacist_idika_prescription_full"] = pharmacist_pages.apply(
        lambda row: map_to_image_link(
            file_name=row["prescription_scanned_pages"],
            prescription=row["pharmacist_idika_prescription_full"],
            pdf_file_name=row["pdf_file_name"],
            run_date=run_date,
            monitoring=monitoring,
        ),
        axis=1,
    )

    columns = [
        "pharmacist_idika_prescription_full",
        "stack_number",
        "patient_name",
        "doc_name",
        "pr_order_timestamp",
        "insurance_amount",
    ]

    rename_cols = {
        "pharmacist_idika_prescription_full": "Αριθμός συνταγής",
        "pr_order_timestamp": "Ώρα Εκτέλεσης",
        "doc_name": "Ονομ/νυμο Ιατρού",
        "patient_name": "Ονομ/νυμο Ασθενούς",
        "stack_number": "Θέση στοίβας",
        "insurance_amount": "Πληρωτέο από Ταμείο",
    }

    display_cols = [rename_cols[col] for col in columns]
    return pharmacist_pages.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]


def get_prescriptions_no_specialty_doctor_above_limit(
    pages: DataFrame,
    dosages: DataFrame,
    full_prescription_summaries: DataFrame,
    run_date: date,
    monitoring: Monitoring,
) -> DataFrame:
    full_prescription_summaries_df = full_prescription_summaries.copy()
    dosages_df = dosages.copy()
    pages_df = pages.copy()
    pages_df["execution"] = pages_df["execution"].astype(pd.Int64Dtype())
    presc_doctors_without_specialty = full_prescription_summaries_df[
        full_prescription_summaries_df["doctor_specialty_id"] == "49"
    ]
    dosages_df["execution"] = dosages_df["scan_last_three_digits"].apply(lambda x: int(str(x)[-1]))
    dosages_df["execution"] = dosages_df["execution"].astype(pd.Int64Dtype())
    merged = presc_doctors_without_specialty.merge(dosages_df, on="prescription", how="inner")
    prescriptions_with_issue = merged[merged["boxes_provided_multiple_executions"] > 1.0]
    prescriptions_with_issue_prescriptions = prescriptions_with_issue.drop_duplicates(
        subset=["prescription", "execution"]
    )
    combined = pages_df.merge(prescriptions_with_issue_prescriptions, on=["prescription", "execution"], how="inner")
    combined = combined[combined["type"] == "pharmacist"]
    combined = combined[combined["page"] == 1.0]
    combined["pr_order_timestamp"] = combined["pr_order_timestamp"].apply(lambda x: x.time())

    combined["pharmacist_idika_prescription_full"] = combined.apply(
        lambda row: map_to_image_link(
            file_name=row["prescription_scanned_pages"],
            prescription=row["pharmacist_idika_prescription_full"],
            pdf_file_name=row["pdf_file_name"],
            run_date=run_date,
            monitoring=monitoring,
        ),
        axis=1,
    )

    columns = [
        "pharmacist_idika_prescription_full",
        "stack_number",
        "patient_name",
        "doc_name",
        "pr_order_timestamp",
    ]

    rename_cols = {
        "pharmacist_idika_prescription_full": "Αριθμός συνταγής",
        "pr_order_timestamp": "Ώρα Εκτέλεσης",
        "doc_name": "Ονομ/νυμο Ιατρού",
        "patient_name": "Ονομ/νυμο Ασθενούς",
        "stack_number": "Θέση στοίβας",
    }

    display_cols = [rename_cols[col] for col in columns]
    return combined.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]


def get_prescriptions_requiring_medical_report(
    pages: DataFrame,
    full_prescription_summaries: DataFrame,
    run_date: date,
    monitoring: Monitoring,
) -> DataFrame:
    full_prescription_summaries_df = full_prescription_summaries.copy()
    pages_df = pages.copy()
    pages_df["execution"] = pages_df["execution"].astype(pd.Int64Dtype())
    medical_report_required = full_prescription_summaries_df[
        full_prescription_summaries_df["medical_report_required"] == True
    ]
    combined = pages.merge(medical_report_required, on=["prescription"], how="inner")

    combined = combined.drop_duplicates(subset=["prescription", "execution"])
    combined = combined[combined["type"] == "pharmacist"]
    combined = combined[combined["page"] == 1.0]
    combined["pr_order_timestamp"] = combined["pr_order_timestamp"].apply(lambda x: x.time())

    combined["pharmacist_idika_prescription_full"] = combined.apply(
        lambda row: map_to_image_link(
            file_name=row["prescription_scanned_pages"],
            prescription=row["pharmacist_idika_prescription_full"],
            pdf_file_name=row["pdf_file_name"],
            run_date=run_date,
            monitoring=monitoring,
        ),
        axis=1,
    )

    columns = [
        "pharmacist_idika_prescription_full",
        "stack_number",
        "patient_name",
        "doc_name",
        "pr_order_timestamp",
    ]

    rename_cols = {
        "pharmacist_idika_prescription_full": "Αριθμός συνταγής",
        "pr_order_timestamp": "Ώρα Εκτέλεσης",
        "doc_name": "Ονομ/νυμο Ιατρού",
        "patient_name": "Ονομ/νυμο Ασθενούς",
        "stack_number": "Θέση στοίβας",
    }

    display_cols = [rename_cols[col] for col in columns]
    return combined.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]


def get_desensitization_prescriptions(
    pages: DataFrame,
    full_prescription_summaries: DataFrame,
    run_date: date,
    monitoring: Monitoring,
) -> DataFrame:
    full_prescription_summaries_df = full_prescription_summaries.copy()
    pages_df = pages.copy()
    pages_df["execution"] = pages_df["execution"].astype(pd.Int64Dtype())
    medical_report_required = full_prescription_summaries_df[
        full_prescription_summaries_df["contains_desensitization_vaccine"] == True
    ]
    combined = pages.merge(medical_report_required, on=["prescription"], how="inner")

    combined = combined.drop_duplicates(subset=["prescription", "execution"])
    combined = combined[combined["type"] == "pharmacist"]
    combined = combined[combined["page"] == 1.0]
    combined["pr_order_timestamp"] = combined["pr_order_timestamp"].apply(lambda x: x.time())

    combined["pharmacist_idika_prescription_full"] = combined.apply(
        lambda row: map_to_image_link(
            file_name=row["prescription_scanned_pages"],
            prescription=row["pharmacist_idika_prescription_full"],
            pdf_file_name=row["pdf_file_name"],
            run_date=run_date,
            monitoring=monitoring,
        ),
        axis=1,
    )

    columns = [
        "pharmacist_idika_prescription_full",
        "stack_number",
        "patient_name",
        "doc_name",
        "pr_order_timestamp",
    ]

    rename_cols = {
        "pharmacist_idika_prescription_full": "Αριθμός συνταγής",
        "pr_order_timestamp": "Ώρα Εκτέλεσης",
        "doc_name": "Ονομ/νυμο Ιατρού",
        "patient_name": "Ονομ/νυμο Ασθενούς",
        "stack_number": "Θέση στοίβας",
    }

    display_cols = [rename_cols[col] for col in columns]
    return combined.sort_values(by="pr_order_timestamp").rename(columns=rename_cols)[display_cols]
