from __future__ import annotations

import csv
import datetime
import gc
import glob
import os
import pathlib
import shutil
import time
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from multiprocessing import Manager, Pool, Queue
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional  # noqa: PEA001

import cv2
import easyocr
import pandas as pd
from numpy.typing import NDArray
from opentelemetry.metrics import get_meter
from opentelemetry.metrics._internal.instrument import Counter
from opentelemetry.trace import Tracer, get_current_span, get_tracer
from pandas import DataFrame
from pyzbar.pyzbar import Decoded, decode

import src.autoscription.core.logging
from src.autoscription import clinical_document_mappers
from src.autoscription.core.config import (
    get_api_dosages_file_name,
    get_api_full_prescriptions_summaries_file_name,
    get_api_partial_prescriptions_summaries_file_name,
    get_dosages_file_name,
    get_download_dir,
    get_pages_file_name,
    get_past_partial_exec_dir,
    get_results_dir,
    get_scan_dir,
    get_temp_scan_dir,
    get_weights_dir,
)
from src.autoscription.core.data_types import index_dtype
from src.autoscription.core.errors import (
    ApiFullPrescriptionsSummariesParsingException,
    ApiPartialPrescriptionsSummariesParsingException,
    FewScansException,
    RetriedException,
    ScanDirNotFoundException,
    SkippedException,
    WrongDayException,
)
from src.autoscription.core.extract_metadata import (
    create_pages_df,
    extract_metadata,
    generate_dosage_check,
)
from src.autoscription.core.logging import Monitoring, setup_logging
from src.autoscription.core.retriever import ClinicalDocumentRetriever
from src.autoscription.core.utils import (
    blank_page_removal,
    generate_past_partial_executions,
    get_barcode_ocr,
)
from src.autoscription.idika_client.api_client import IdikaAPIClient
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit

if TYPE_CHECKING:
    from src.autoscription.gui.Application import Application

    # TODO: remove circular dependency with Application

from src.autoscription.selenium_components.utils import (
    _get_daily_pres_list,
    _get_daily_pres_list_df,
    download_prescriptions,
    get_injections,
    list_similarity,
    retrieve_prescription_ids,
)

DAY_IS_CORRECT_RATIO_THRESHOLD = 0.60
SUFFICIENT_SCANS_RATIO_THRESHOLD = 0.5
TIMES_TO_RETRY = 4

warnings.filterwarnings("ignore")


def pages_columns_for_excel() -> list[str]:
    return [
        "prescription_scanned_pages",
        "pdf_file_name",
        "execution",
        "pharmacist_idika_prescription_full",
        "prescription",
        "scan_last_three_digits",
        "type",
        "page",
        "pages",
        "first_execution",
        "digital",
        "unit",
        "category",
        "category_name",
        "100%",
        "doc_name",
        "patient_name",
        "pr_order_timestamp",
        "stack_number",
        "sign_found",
        "sign_required",
        "sign_check",
        "stamps_found",
        "stamps_required",
        "stamps_check",
        "dosage_check",
        "coupons_found",
        "coupons_required",
        "coupon_check",
        "coupon_precheck",
        "document_type",
        "insurance_amount",
        "patient_amount",
        "missing_tapes",
        "surplus_tapes",
    ]


def remove_temp_scan_dir() -> None:
    temp_scan_dir = get_temp_scan_dir()
    if os.path.exists(temp_scan_dir) and os.path.isdir(temp_scan_dir):
        shutil.rmtree(temp_scan_dir)


def remove_last_scan_dir(last_scan_dir: Path) -> None:
    if last_scan_dir.exists() and last_scan_dir.is_dir():
        for item in os.listdir(last_scan_dir):
            item_path = os.path.join(last_scan_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)


def select_doctor_scans(scans: list[str]) -> DataFrame:
    return pd.DataFrame(
        [doc.split("_")[-2][:-3] for doc in scans if doc.split("_")[-2] and doc.split("_")[-2][-3] == "0"],
        columns=["id"],
    )


def select_pharmacist_scans(scans: list[str]) -> DataFrame:
    return DataFrame(
        [doc.split("_")[-2][:-3] for doc in scans if doc.split("_")[-2] and doc.split("_")[-2][-3] == "1"],
        columns=["id"],
    )


class ModifiedDict(object):  # noqa: N801
    def __init__(self, d: dict[str, int]) -> None:
        self.__dict__ = d


def get_unique_recognized_barcodes_l13(scan_pres_ids: list[str]) -> list[str]:
    recognized_barcode_l13 = [s for s in scan_pres_ids if s != "0" * 13]
    unique_recognized_barcodes_l13 = list(set(recognized_barcode_l13))
    return unique_recognized_barcodes_l13


def select_pharmacy_id(
    idika_api_client: IdikaAPIClient,
    scanned_prescription_ids_sample: list[str],
    guessing_pharmacy_id_config: dict[str, Any],
    monitoring: Monitoring,
) -> int:
    authentication_pharmacy_id = idika_api_client.authenticate()
    active_pharmacist_units = idika_api_client.get_active_pharmacist_units()
    active_pharmacist_units_as_dicts = [asdict(u) for u in active_pharmacist_units]
    monitoring.logger_adapter.warning(f"Active pharmacist Units: {active_pharmacist_units_as_dicts}")

    if guessing_pharmacy_id_config["is_enabled"]:
        guessed_pharmacy_id = guess_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=scanned_prescription_ids_sample,
            guessing_pharmacy_id_config=guessing_pharmacy_id_config,
            active_pharmacist_units=active_pharmacist_units,
            monitoring=monitoring,
        )
        return guessed_pharmacy_id if guessed_pharmacy_id else authentication_pharmacy_id

    monitoring.logger_adapter.warning(f"Authentication Pharmacy Id used: {authentication_pharmacy_id}")
    return authentication_pharmacy_id


def guess_pharmacy_id(
    idika_api_client: IdikaAPIClient,
    scanned_prescription_ids_sample: list[str],
    guessing_pharmacy_id_config: dict[str, Any],
    active_pharmacist_units: list[PharmacistUnit],
    monitoring: Monitoring,
) -> Optional[int]:
    pharmacy_ids = [p.pharmacy_id for p in active_pharmacist_units]
    success_rates: dict[int, float] = defaultdict(int)
    for pharmacy_id in pharmacy_ids:
        successful_requests = sum(
            1
            for pres_id in scanned_prescription_ids_sample
            if idika_api_client.idika_http_client.get_clinical_document(pharmacy_id, pres_id).status_code == 200
        )
        total_requests = len(scanned_prescription_ids_sample)
        success_rates[pharmacy_id] = successful_requests / total_requests if total_requests > 0 else 0
    guessed_pharmacy_id = None
    best_pharmacy_id = max(success_rates, key=success_rates.get)  # type: ignore[arg-type]
    if success_rates[best_pharmacy_id] > guessing_pharmacy_id_config["success_rate_threshold"]:
        monitoring.logger_adapter.warning(f"Guessed Pharmacy Id used: {best_pharmacy_id}")
        guessed_pharmacy_id = best_pharmacy_id
    return guessed_pharmacy_id


def find_missing_tapes(row):  # type: ignore[no-untyped-def]
    # Convert to sets for efficient comparison
    required_tapes = set(row["authenticity_tapes"])
    found_tapes = set(row["coupons_found"].split(","))
    found_tapes = {x.strip() for x in found_tapes if x.strip() and x.strip().lower() != "nan"}

    # Find the difference (elements in required_tapes that are not in found_tapes)
    missing_tapes = list(required_tapes - found_tapes)
    surplus_tapes = list(found_tapes - required_tapes)
    # Return empty list if all tapes are found
    return pd.Series(
        {
            "missing_tapes": ",".join(missing_tapes) if missing_tapes else "",
            "surplus_tapes": ",".join(surplus_tapes) if surplus_tapes else "",
            "execution": row["execution"],
        }
    )


def safe_missing_tapes(row: pd.Series, column_name: str) -> str:
    # Check if 'column_name' exists in the row
    if column_name not in row:
        return ""
    # Check if the value in 'column_name' is missing
    if pd.isna(row[column_name]) or row[column_name] is None:
        return ""
    # Check if 'type' exists and is not missing
    if "type" in row and pd.notna(row["type"]):
        # Normalize 'type' to lowercase for case-insensitive comparison
        if str(row["type"]).lower() == "pharmacist":
            return str(row[column_name])
    # For all other cases, return an empty string
    return ""


def process_missing_tapes(pages_df: pd.DataFrame, tapes_summary_df: pd.DataFrame) -> pd.DataFrame:
    grouped_pages_tapes_df = (
        pages_df.loc[pages_df["type"] == "pharmacist"]
        .groupby(["prescription", "execution"])["coupons_found"]
        .agg(",".join)
        .reset_index()
    )

    grouped_pages_tapes_df = grouped_pages_tapes_df.merge(
        tapes_summary_df[["prescription", "execution", "authenticity_tapes"]],
        on=["prescription", "execution"],
        how="left",
    )
    #TODO: if is_test_user: 
    # grouped_pages_tapes_df.to_csv("8.grouped_pages_tapes_df.csv")
    grouped_pages_tapes_df[["missing_tapes", "surplus_tapes","execution"]] = grouped_pages_tapes_df.apply(
        find_missing_tapes, axis=1
    )
    # grouped_pages_tapes_df.to_csv("9.grouped_pages_tapes_df.csv")
    pages_df = pages_df.drop(columns=["missing_tapes", "surplus_tapes"])
    pages_df = grouped_pages_tapes_df[["prescription", "missing_tapes", "surplus_tapes","execution"]].merge(
        pages_df, on=["prescription", "execution"], how="right"
    )

    pages_df["missing_tapes"] = pages_df.apply(safe_missing_tapes, args=("missing_tapes",), axis=1)
    pages_df["surplus_tapes"] = pages_df.apply(safe_missing_tapes, args=("surplus_tapes",), axis=1)

    pages_df["coupon_check"] = pages_df["missing_tapes"].apply(lambda x: x == "")
    pages_df = pages_df.drop_duplicates()
    return pages_df


@dataclass
class Output:
    dosages: Optional[DataFrame]
    pages: Optional[DataFrame]
    api_dosages: Optional[DataFrame]
    api_partial_prescriptions_summaries: Optional[DataFrame]
    api_full_prescriptions_summaries: Optional[DataFrame]


class Core:
    multiprocessing_controls: list[tuple[Manager, Pool, Queue]] = []  # type: ignore[valid-type, type-arg]
    monitoring: Monitoring
    runs_counter: Counter
    wrong_day_counter: Counter
    output: Output

    def __init__(self, monitoring: Monitoring) -> None:
        self.monitoring = monitoring
        self.runs_counter = get_meter("Autoscription").create_counter(
            name="runs", unit="1", description="Counts runs per user"
        )
        self.wrong_day_counter = get_meter("Autoscription").create_counter(
            name="wrong_day", unit="1", description="Counts wrong day errors"
        )
        self.few_scans_found_counter = get_meter("Autoscription").create_counter(
            name="few_scans_found", unit="1", description="Counts few scans found errors"
        )
        self.scan_dir_not_found_counter = get_meter("Autoscription").create_counter(
            name="scan_dir_not_found", unit="1", description="Counts scan dir not found errors"
        )
        self.probable_barcode_match_counter = get_meter("Autoscription").create_counter(
            name="probable_barcode_match", unit="1", description="Counts Probable Barcode Matched"
        )
        self.idika_over_scan_ratio = get_meter("Autoscription").create_histogram(
            name="idika_over_scan_ratio", description="Idika Over Scan totals ratio"
        )
        self.scan_over_idika_ratio = get_meter("Autoscription").create_histogram(
            name="scan_over_idika_ratio", description="Scan Over Idika totals ratio"
        )

    # TODO: move specific_prescriptions to config
    def run(
        self,
        username: str,
        scanner_output_directory: str,
        scan_date: datetime.datetime,
        progress_bar: dict[str, Any],
        config: dict[str, Any],
        application: Application,
        idika_api_client: IdikaAPIClient,
        output: Output,
        specific_prescriptions: Optional[list[str]] = None,
    ) -> None:
        self.monitoring.set_logger_adapter_extra({"username": username})
        self.output = output
        setup_logging(monitoring=self.monitoring, scan_date=scan_date)  # TODO: make it method of Monitoring
        tracer: Tracer = get_tracer(__name__)
        with tracer.start_as_current_span("run"):
            self.monitoring.run_context = get_current_span().get_span_context()
            self.monitoring.logger_adapter.warning(f"Software Started by {username} for {scan_date}.")
            self.runs_counter.add(1, {"username": username})
            self.__run(
                username=username,
                scanner_output_directory=scanner_output_directory,
                scan_date=scan_date,
                progress_bar=progress_bar,
                config=config,
                specific_prescriptions=specific_prescriptions,
                application=application,
                idika_api_client=idika_api_client,
            )

    # TODO: pass api token through method attributed instead of config
    def __run( 
        self,
        username: str,
        scanner_output_directory: str,
        scan_date: datetime.datetime,
        progress_bar: dict[str, Any],
        config: dict[str, Any],
        application: Application,
        idika_api_client: IdikaAPIClient,
        specific_prescriptions: Optional[list[str]] = None,
    ) -> None:
        # Run Preparation starts here

        clinical_document_retriever = ClinicalDocumentRetriever(
            idika_api_client=idika_api_client, monitoring=self.monitoring
        )
        is_test_user: bool = bool(config["backend"]["file_uploader"]["test_user"] == True)
        scanner_output_dir = Path(scanner_output_directory)
        scan_dir = get_scan_dir(scan_date)
        download_dir = get_download_dir(scan_date)
        past_partial_exec_dir = get_past_partial_exec_dir(scan_date)
        if not is_test_user:
            if download_dir.exists():
                shutil.rmtree(download_dir)
            if past_partial_exec_dir.exists():
                shutil.rmtree(past_partial_exec_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        past_partial_exec_dir.mkdir(parents=True, exist_ok=True)
        results_dir = get_results_dir(scan_date)
        results_dir.mkdir(parents=True, exist_ok=True)

        self.monitoring.logger_adapter.warning(f"Scanner_output_dir:, {scanner_output_dir}")
        self.monitoring.logger_adapter.warning(f"Scan directory:, {scan_dir}")
        self.monitoring.logger_adapter.warning(f"Download directory:, {download_dir}")
        self.monitoring.logger_adapter.warning(f"Results directory:, {results_dir}")
        temp_scan_dir = get_temp_scan_dir()
        
        if scanner_output_dir.exists():
            scan_prep_start = time.time()
            scan_prep_start_time = time.localtime(scan_prep_start)
            if progress_bar:
                progress_bar["text"] = "Προετοιμασία εγγράφων: "

            blank_page_removal(scanner_output_dir, monitoring=self.monitoring)
            remove_temp_scan_dir()
            temp_scan_dir.mkdir(parents=True, exist_ok=True)
            self.prepare_scan_files(scanner_output_dir, temp_scan_dir, progress_bar=progress_bar)

            scan_prep_end = time.time()
            scan_prep_end_time = time.localtime(scan_prep_end)
            scan_prep_runtime = scan_prep_end - scan_prep_start
            scan_prep_formatted_elapsed_time = str(datetime.timedelta(seconds=int(scan_prep_runtime)))
            formatted_start_time: str = time.strftime("%Y-%m-%d %H:%M:%S", scan_prep_start_time)
            formatted_end_time: str = time.strftime("%Y-%m-%d %H:%M:%S", scan_prep_end_time)

            self.monitoring.logger_adapter.warning(
                f"Scan_prep Runtime: {scan_prep_formatted_elapsed_time} | Start: {formatted_start_time}"
                f", End: {formatted_end_time}."
            )

            self.delete_last_scan_folder(scanner_output_directory, is_debug_enabled=config["is_debug_enabled"])

        # Run Preparation ends here

        # Get Scans pres ids starts here
        if temp_scan_dir.exists():
            scans = glob.glob(str(temp_scan_dir / "*.jpg"))
        else:
            scan_dir.mkdir(parents=True, exist_ok=True)
            idex_file_exists = any(scan_dir.glob("index.csv"))
            if not scanner_output_dir.exists() and not idex_file_exists:
                self.monitoring.logger_adapter.error(
                    "Last scan directory not found and scan directory in executions not found"
                )
                self.scan_dir_not_found_counter.add(1, {"username": username})
                raise ScanDirNotFoundException()
            scans = glob.glob(str(scan_dir / "*.jpg"))
        scan_pres_ids = [file.split("_")[-2][:-3] for file in scans if len(file.split("_")[-2]) == 16]
        # Get Scans pres ids ends here

        prescription_values: Optional[list[str]] = None
        ps_ids: list[dict[str, str]] = []
        if config["idika_integration"]["is_enabled"]:
            self.update_pharmacy_id(
                config=config,
                idika_api_client=idika_api_client,
                unique_recognized_scanned_barcodes=get_unique_recognized_barcodes_l13(scan_pres_ids),
                guessing_pharmacy_id_config=config["idika_integration"]["guessing_pharmacy_id"],
            )
            # Get pdfs starts here

            if progress_bar:
                progress_bar["counter"] = None
            selenium_start = time.time()
            selenium_start_time = time.localtime(selenium_start)
            if progress_bar:
                progress_bar["text"] = "Συγχρονισμός συνταγών με την ΗΔΙΚΑ: "
            ps_ids = _get_daily_pres_list(download_dir, date=scan_date.strftime("%Y-%m-%d"), config=config["api"])
            prescription_values = [item["prescription"] for item in ps_ids]

            if temp_scan_dir.exists():
                # Check for the correctness of the day
                self.check_temp_scan_dir(application, prescription_values, scan_pres_ids, username)

                # If both checks pass, handle the directories
                if scan_dir.exists():
                    shutil.rmtree(scan_dir)
                shutil.move(temp_scan_dir.as_posix(), scan_dir)

            for _ in range(TIMES_TO_RETRY):
                pdfs = [
                    file.split("/")[-1].split("\\")[-1].split(".")[0]
                    for file in glob.glob(str(download_dir / "*" / "*.pdf"))
                ]

                remaining_scans = [d for d in ps_ids if f"{d['prescription']}_{d['execution']}" not in pdfs]
                self.monitoring.logger_adapter.warning(
                    f" Remaining scans not downloaded:{[d['prescription'] for d in remaining_scans]}"
                )
                if remaining_scans:
                    retrieve_prescription_ids(
                        ps_ids=remaining_scans,
                        download_dir=download_dir,
                        config=config["api"],
                        multiprocessing_controls=self.multiprocessing_controls,
                        progress_bar=progress_bar,
                        monitoring=self.monitoring,
                    )

            past_partial_executions = generate_past_partial_executions(pd.DataFrame(ps_ids))
            for _ in range(TIMES_TO_RETRY):
                pdfs = [
                    file.split("/")[-1].split("\\")[-1].split(".")[0]
                    for file in glob.glob(str(past_partial_exec_dir / "*" / "*.pdf"))
                ]
                remaining_scans = [
                    d for d in past_partial_executions if f"{d['prescription']}_{d['execution']}" not in pdfs
                ]
                if remaining_scans:
                    download_prescriptions(
                        ps_ids=remaining_scans,
                        download_dir=past_partial_exec_dir,
                        download_counter=0,
                        lock=None,
                        shared_counter=None,
                        log_queue=None,
                        config=config["api"],
                        monitoring=self.monitoring,
                    )
            selenium_end = time.time()
            selenium_end_time = time.localtime(selenium_end)
            selenium_runtime = selenium_end - selenium_start
            selenium_formatted_elapsed_time = str(datetime.timedelta(seconds=int(selenium_runtime)))
            selenium_start_time_formatted: str = time.strftime("%Y-%m-%d %H:%M:%S", selenium_start_time)
            selenium_end_time_formatted: str = time.strftime("%Y-%m-%d %H:%M:%S", selenium_end_time)

            self.monitoring.logger_adapter.warning(
                f"Selenium process Runtime: {selenium_formatted_elapsed_time} | Start: {selenium_start_time_formatted}"
                f", End: {selenium_end_time_formatted}."
            )

            if progress_bar:
                progress_bar["counter"] = None

        # Get pdfs ends here
        self.monitoring.logger_adapter.warning(f"Number of scanned documents (jpg): {len(scans)}")
        pdfs = glob.glob(str(download_dir / "*" / "*.pdf"))
        idika_barcodes = [pdf.rsplit("\\")[-1].rsplit("_")[-1] for pdf in pdfs]
        # Add doctor barcodes
        total_barcodes = [f"{barcode[:-3]}0{barcode[-2:-1]}0" for barcode in idika_barcodes] + idika_barcodes
        self.validate_and_rename_scanned_filenames(
            target_dir=scan_dir, idika_barcodes=total_barcodes, username=username
        )
        self.monitoring.logger_adapter.warning(f"Number of downloaded documents (pdf): {len(pdfs)}")
        if progress_bar:
            progress_bar["total_prescriptions"] = len(pdfs)

        # Extract metadata starts here
        extract_metadata_start = time.time()
        # Get injections starts here
        if config["idika_integration"]["is_enabled"]:
            injection_pages, injection_dosages = get_injections(
                date=scan_date, config=config["api"], monitoring=self.monitoring
            )
        else:
            injection_pages = pd.DataFrame(columns=["execution", "id", "prescription_scanned_pages", "prescription"])
            injection_dosages = pd.DataFrame(columns=[])
        # Get injections ends here

        # Get past partial executions starts here
        past_partial_exec_pdfs = glob.glob(str(past_partial_exec_dir / "*" / "*.pdf"))
        past_partial_exec_checks = extract_metadata(
            dir_list=past_partial_exec_pdfs, specific_prescriptions=specific_prescriptions, monitoring=self.monitoring
        )
        # Get past partial executions ends here
        current_day_checks = extract_metadata(
            dir_list=pdfs, specific_prescriptions=specific_prescriptions, monitoring=self.monitoring
        )

        extract_metadata_end = time.time()
        extract_metadata_runtime = extract_metadata_end - extract_metadata_start
        extract_metadata_formatted_elapsed_time = str(datetime.timedelta(seconds=int(extract_metadata_runtime)))
        self.monitoring.logger_adapter.warning(
            "Extract metadata Runtime : " f"{extract_metadata_formatted_elapsed_time}"
        )
        # Extract metadata ends here
        run_timestamp = datetime.datetime.now()
        # TODO: extract time measuring in function
        self.monitoring.logger_adapter.warning("API Dosages Started")
        api_files_generation_start = time.time()
        api_dosages_df: DataFrame = DataFrame(
            columns=[
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
        )
        api_partial_prescriptions_summaries_df = DataFrame(
            columns=[
                "prescription",
                "execution",
                "contains_high_cost_drug_above_limit",
                "retail_price",
                "authenticity_tapes",
            ]
        )
        api_full_prescriptions_summaries_df = DataFrame(
            columns=[
                "prescription",
                "doctor_specialty_id",
                "contains_desensitization_vaccine",
                "medical_report_required",
                "doctor_specialty_name",
                "authenticity_tapes",
            ]
        )

        try:
            clinical_documents: list[ClinicalDocument] = clinical_document_retriever.retrieve_clinical_documents(
                [str(prescription) for prescription in prescription_values] if prescription_values else []
            )
            partial_clinical_documents = clinical_document_retriever.retrieve_partial_clinical_documents(ps_ids)
            try:
                api_dosages_df = clinical_document_mappers.map_to_dosages_dataframe_from_list(clinical_documents)
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.error("api_dosages generation failed")
            try:
                api_full_prescriptions_summaries_df = clinical_document_mappers.map_to_full_summary_dataframe_from_list(
                    clinical_documents
                )
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.error("api_full_prescriptions_summaries generation failed")
                raise ApiFullPrescriptionsSummariesParsingException()
            try:
                api_partial_prescriptions_summaries_df = (
                    clinical_document_mappers.map_to_partial_prescription_summaries_dataframe_from_list(
                        partial_clinical_documents, config["business_rules"]["fyk_limit"]
                    )
                )
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.error("api_partial_prescriptions_summaries generation failed")
                raise ApiPartialPrescriptionsSummariesParsingException()

        except Exception as e:
            self.monitoring.logger_adapter.exception(e)
            self.monitoring.logger_adapter.error("Failed to retrieve partial and full prescriptions from API")
        api_files_generation_end = time.time()
        api_files_generation_runtime = api_files_generation_end - api_files_generation_start
        api_files_generation_formatted_elapsed_time = str(datetime.timedelta(seconds=int(api_files_generation_runtime)))

        self.monitoring.logger_adapter.warning(
            f"API Files Generation Runtime : {api_files_generation_formatted_elapsed_time}"
        )
        self.monitoring.logger_adapter.warning(f"API_Dosages_df_csv was saved in {results_dir}")
        self.monitoring.logger_adapter.warning(f"API_Partial_Prescriptions_Summaries_df_csv was saved in {results_dir}")
        # dosages start
        dosages_start = time.time()
        dosages_df = pd.DataFrame([])
        
        # Concatenate both past_partial_exec_checks and current_day_checks
        # in the dosages file with a is_past_partial_exec column
        for i, checks in enumerate([past_partial_exec_checks, current_day_checks]):
            for prescription_id, check in checks.items():
                for three_digits, data in check.items():
                    if i == 0:
                        data["dosages"]["is_past_partial_exec"] = True
                    else:
                        data["dosages"]["is_past_partial_exec"] = False
                    data["dosages"]["prescription"] = prescription_id
                    data["dosages"]["scan_last_three_digits"] = three_digits
                    dosages_df = pd.concat([dosages_df, data["dosages"]], axis=0)

        # Group by 'prescription' and 'description' and sum
        # the 'boxes_provided' column
        grouped_df = dosages_df.groupby(["prescription", "description"], as_index=False).agg({"boxes_provided": "sum"})
        # Rename the aggregated column
        grouped_df = grouped_df.rename(columns={"boxes_provided": "boxes_provided_multiple_executions"})
        # Merge the grouped data with the original data
        dosages_df = dosages_df.merge(grouped_df, on=["prescription", "description"], how="inner")
        # Apply the 'generate_dosage_check' function to each row
        dosages_df["dosage_check"] = dosages_df.apply(
            lambda row: generate_dosage_check(
                row["boxes_provided_multiple_executions"],
                row["boxes_required"],
                row["dosage"],
                row["dosage_qnt"],
            ),
            axis=1,
        )
        dosages_df["dosage"] = dosages_df["dosage"].astype(str)

        dosages_end = time.time()
        dosages_runtime = dosages_end - dosages_start
        dosages_formatted_elapsed_time = str(datetime.timedelta(seconds=int(dosages_runtime)))
        # dosages end
        self.monitoring.logger_adapter.warning(f"Dosages Runtime : {dosages_formatted_elapsed_time}")

        # pages start
        if not config["dosages_only"]:
            if progress_bar:
                progress_bar["text"] = "Ανάλυση εγγράφων: "
            pages_df = create_pages_df(
                checks=current_day_checks,
                scan_dir=scan_dir,
                detectors_config=config["detectors"],
                multiprocessing_controls=self.multiprocessing_controls,  # type: ignore[arg-type]
                monitoring=self.monitoring,
                tubro_mode=config["turbo_mode"],
                is_debug_enabled=config["is_debug_enabled"],
                progress_bar=progress_bar,
            )
            index_df = pd.read_csv(glob.glob(str(scan_dir / "index.csv"))[0]).astype(index_dtype)
            stack_position_df = index_df.copy()
            stack_position_df = stack_position_df.drop("id", axis=1)

            # TODO: Rough Patch - need to reiterate
            pages_df.loc[pages_df["type"] == "pharmacist", "scan_last_three_digits"] = pages_df[
                "pharmacist_idika_prescription_full"
            ].str[-3:]

            pres_timestamp_df = _get_daily_pres_list_df(download_dir=download_dir)

            if is_test_user:
                pages_df.to_csv("1.pages_df.csv")
                pres_timestamp_df.to_csv("1.pres_timestamp_df.csv")
                dosages_df.to_csv("1.dosages_df.csv")
                index_df.to_csv("1.index_df.csv")
                stack_position_df.to_csv("1.stack_position_df.csv")
                

            grouped_dosages_df = (
                dosages_df[dosages_df["dosage_check"] == "False"]
                .groupby(["prescription", "scan_last_three_digits"], as_index=False)
                .agg({"dosage_check": "first"})
            )

            grouped_dosages_df["prescription"] = (
                grouped_dosages_df["prescription"].astype(pd.Int64Dtype()).astype(pd.StringDtype())
            )
            grouped_dosages_df["scan_last_three_digits"] = grouped_dosages_df["scan_last_three_digits"].astype(
                pd.StringDtype()
            )

            pages_df = (
                pages_df.merge(pres_timestamp_df, on=["prescription", "execution"], how="outer")
                .merge(stack_position_df, on="prescription_scanned_pages", how="outer")
                .merge(
                    grouped_dosages_df.assign(page=1),
                    on=["prescription", "scan_last_three_digits", "page"],
                    how="left",
                )
            )
            # pages end
            # pages now have the injections and the multiple executions that were not included in the stack of prescriptions
            if is_test_user:
                pres_timestamp_df.to_csv("2.pres_timestamp_df.csv")
                stack_position_df.to_csv("2.stack_position_df.csv")
                grouped_dosages_df.to_csv("2.grouped_dosages_df.csv")
                pages_df.to_csv("2.pages_df.csv")

            pages_df.loc[(pages_df["type"] == "doctor") & (pages_df["digital"] == True), "sign_check"] = True

            grouped_api_partial_prescriptions_df = (
                api_partial_prescriptions_summaries_df.groupby(["prescription", "execution"])["authenticity_tapes"]
                .agg(lambda x: list(set(sum(x, []))))  # Flattens lists and gets unique values
                .reset_index()
            )

            # Add execution column with value "1" to full prescriptions dataframe
            api_full_prescriptions_summaries_df["execution"] = 1

            # Combine the dataframes
            tapes_summary_df = (
                grouped_api_partial_prescriptions_df.drop_duplicates(subset=["prescription", "execution"], keep="first")
                .set_index(["prescription", "execution"])["authenticity_tapes"]
                .combine_first(
                    api_full_prescriptions_summaries_df.drop_duplicates(
                        subset=["prescription", "execution"], keep="first"
                    ).set_index(["prescription", "execution"])["authenticity_tapes"]
                )
                .reset_index()
            )

            api_full_prescriptions_summaries_df = api_full_prescriptions_summaries_df.drop(columns=["execution"])
            pages_df = process_missing_tapes(pages_df=pages_df, tapes_summary_df=tapes_summary_df)

            dosages_file_path = results_dir / get_dosages_file_name(scan_date, run_timestamp)
            dosages_df = pd.concat([dosages_df, injection_dosages], ignore_index=True)

            if is_test_user:
                injection_pages.to_csv("3.injection_pages.csv")
                pages_df.to_csv("3.pages.csv")
                dosages_df.to_csv("3.dosages_df.csv")
                dosages_df.to_csv(dosages_file_path.as_posix(), sep="|", index=False)
                self.monitoring.logger_adapter.warning(f"Dosages_df_csv was saved in {results_dir}")

            self.output.dosages = dosages_df
            self.monitoring.logger_adapter.warning("Dosages_df updated")

            index_df["id"] = index_df["id"].astype(pd.StringDtype())
            injection_pages["execution"] = injection_pages["execution"].astype(pd.StringDtype())

            injection_pages = injection_pages.merge(
                index_df.rename(columns={"id": "prescription"}), on="prescription", how="left"
            )
            merged_df = pages_df.merge(
                injection_pages, on="prescription_scanned_pages", how="outer", suffixes=["_df1", "_df2"]
            )
            overlapping_columns = [
                col
                for col in pages_df.columns
                if col in injection_pages.columns and col != "prescription_scanned_pages"
            ]
            for column in overlapping_columns:
                merged_df[column] = merged_df[column + "_df1"].combine_first(merged_df[column + "_df2"])
                merged_df = merged_df.drop(columns=[column + "_df1", column + "_df2"])
            pages_df = merged_df
            
            if is_test_user:
                index_df.to_csv("4.index_df.csv")
                pages_df.to_csv("4.pages_df.csv")
                injection_pages.to_csv("4.injection_pages.csv")
                
            self.output.pages = pages_df[pages_columns_for_excel()]
            self.monitoring.logger_adapter.warning("Pages_df updated")
            if is_test_user:
                pages_file_path = results_dir / get_pages_file_name(scan_date, run_timestamp)
                pages_df[pages_columns_for_excel()].to_csv(pages_file_path.as_posix(), sep="|", index=False)
                self.monitoring.logger_adapter.warning(f"Pages_df_csv file created: {pages_file_path}")

            self.output.api_dosages = api_dosages_df
            self.monitoring.logger_adapter.warning("Api_Dosages_df updated")
            if is_test_user:
                api_dosages_file_path = results_dir / get_api_dosages_file_name(scan_date, run_timestamp)
                api_dosages_df.to_csv(api_dosages_file_path.as_posix(), sep="|", index=False)
                self.monitoring.logger_adapter.warning(f"Api_Dosages_df_csv file created: {api_dosages_file_path}")
            self.output.api_partial_prescriptions_summaries = api_partial_prescriptions_summaries_df
            self.monitoring.logger_adapter.warning("Api_Partial_Prescriptions_Summaries_df updated")

            self.output.api_full_prescriptions_summaries = api_full_prescriptions_summaries_df
            self.monitoring.logger_adapter.warning("Api_Full_Prescriptions_Summaries_df updated")

            if is_test_user:
                api_partial_prescriptions_summaries_path = (
                    results_dir / get_api_partial_prescriptions_summaries_file_name(scan_date, run_timestamp)
                )
                api_partial_prescriptions_summaries_df.to_csv(
                    api_partial_prescriptions_summaries_path.as_posix(), sep="|", index=False
                )
                self.monitoring.logger_adapter.warning(
                    f"Api_Partial_Prescriptions_Summaries_df_csv file "
                    f"created: {api_partial_prescriptions_summaries_path}"
                )
                api_full_prescriptions_summaries_path = results_dir / get_api_full_prescriptions_summaries_file_name(
                    scan_date, run_timestamp
                )
                api_full_prescriptions_summaries_df.to_csv(
                    api_full_prescriptions_summaries_path.as_posix(), sep="|", index=False
                )
                self.monitoring.logger_adapter.warning(
                    f"Api_Full_Prescriptions_Summaries_df_csv file created: {api_full_prescriptions_summaries_path}"
                )

    def update_pharmacy_id(
        self,
        config: dict[str, Any],
        idika_api_client: IdikaAPIClient,
        unique_recognized_scanned_barcodes: list[str],
        guessing_pharmacy_id_config: dict[str, Any],
    ) -> None:
        pharmacy_id: int = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=unique_recognized_scanned_barcodes[:15],
            guessing_pharmacy_id_config=guessing_pharmacy_id_config,
            monitoring=self.monitoring,
        )
        idika_api_client.pharmacy_id = pharmacy_id
        config["api"]["pharmacy_id"] = pharmacy_id

    def check_temp_scan_dir(
        self, application: Application, prescription_values: list[str], scan_pres_ids: list[str], username: str
    ) -> None:
        idika_similarity = list_similarity(scan_pres_ids, prescription_values)
        if idika_similarity.ratio == 0:
            self.monitoring.logger_adapter.warning("Total_unique_elements are zero.")

        day_is_correct = idika_similarity.ratio >= DAY_IS_CORRECT_RATIO_THRESHOLD
        scans_similarity = list_similarity(prescription_values, scan_pres_ids)
        sufficient_scans_present = scans_similarity.ratio >= SUFFICIENT_SCANS_RATIO_THRESHOLD
        self.monitoring.logger_adapter.warning(
            f"Number of unique elements in idika list: {len(set(prescription_values))}"
        )
        self.monitoring.logger_adapter.warning(f"Number of unique elements in scan list: {len(set(scan_pres_ids))}")
        self.monitoring.logger_adapter.warning(f"Number of common elements: {len(idika_similarity.common_elements)}")
        self.monitoring.logger_adapter.warning(
            f" Number of common elements that exist in scan list: {idika_similarity.ratio}"
        )
        self.idika_over_scan_ratio.record(idika_similarity.ratio, {"username": username})
        self.monitoring.logger_adapter.warning(
            f"Number of common elements that exist in idika list: {scans_similarity.ratio}"
        )
        self.scan_over_idika_ratio.record(scans_similarity.ratio, {"username": username})
        if not day_is_correct:
            application.wrong_date_review()
            self.wrong_day_counter.add(1, {"username": username})
            raise WrongDayException()
        if not sufficient_scans_present:
            self.few_scans_found_counter.add(1, {"username": username})
            raise FewScansException()

    def is_file_empty(self, file_path: Path) -> bool:
        """Check if file is empty by confirming if its size is 0 bytes or it contains only blank lines/spaces."""
        # Check if file exist and it is not empty
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            # Check if file contains only blank lines and spaces
            with open(file_path, "r") as file:
                for line in file:
                    # strip() removes leading/trailing spaces, so if a line has only spaces
                    # or is empty, it will result in an empty string
                    if line.strip():
                        # A non-empty line was found
                        return False
            # If we get here, all lines were either empty or contained only spaces
            return True
        else:
            # File is empty
            return True

    def cleanup(self) -> None:
        for manager, pool, queue in self.multiprocessing_controls:
            try:
                queue.put(src.autoscription.core.logging.STOP_TOKEN)
            except EOFError:
                pass
            pool.terminate()  # type: ignore[attr-defined]
            manager.shutdown()  # type: ignore[attr-defined]

    def delete_last_scan_folder(self, scanner_output_directory: str, is_debug_enabled: bool) -> None:
        if not is_debug_enabled:
            try:
                # Check if the directory exists
                if os.path.exists(scanner_output_directory) and os.path.isdir(scanner_output_directory):
                    # Remove the whole directory
                    for item in os.listdir(scanner_output_directory):
                        item_path = os.path.join(scanner_output_directory, item)
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    self.monitoring.logger_adapter.warning(f"Directory {scanner_output_directory} has been removed")
                else:
                    self.monitoring.logger_adapter.warning(f"The directory {scanner_output_directory} does not exist")
            except Exception as e:
                self.monitoring.logger_adapter.warning(f"An error occurred: {e}")
        else:
            self.monitoring.logger_adapter.warning(f"Debbuging mode: {scanner_output_directory} has not been removed")

    def prepare_scan_files(self, source_dir: Path, target_dir: Path, progress_bar: dict[str, ModifiedDict]) -> None:
        """
        Prepare scan files.
        Read image files from the source directory, decode barcodes,
        and move the files to the target directory
        with appropriate names.
        Create an index.csv file containing barcode, stack number,
        and prescription scanned pages.

        In more detail:
        Read from input dir in time sequence
        Detect barcode value
        Move and rename file to target_dir using barcode
        Create index file (csv)
            id(Barcode), stack_number(sequence),
            prescription_scanned_pages(fileName(date, barcode, counter))
        """
        # Define the path of the index.csv file
        csv_path = target_dir / "index.csv"

        def has_only_header(csv_path_local: str) -> bool:
            with open(csv_path_local, mode="r", newline="") as csvfile:
                csv_reader = csv.reader(csvfile)
                row_count = sum(1 for row in csv_reader)
            return row_count == 1

        if os.path.exists(csv_path):
            if has_only_header(csv_path.as_posix()):
                os.remove(csv_path)
                self.monitoring.logger_adapter.warning(f"{csv_path} had only the header and has been deleted.")

        def check_and_delete(source_dir: Path, target_dir: Path) -> None:
            # List all jpg files in directory1 and directory2
            jpg_files1 = [f for f in os.listdir(source_dir) if f.endswith(".jpg")]
            jpg_files2 = [f for f in os.listdir(target_dir) if f.endswith(".jpg")]

            # If the number of jpg files in last_scan is not 0
            if len(jpg_files1) != 0:
                # If the number of jpg files in both directories are the same
                if len(jpg_files1) != len(jpg_files2):
                    # Delete all files in directory1
                    all_files2 = os.listdir(target_dir)
                    for f in all_files2:
                        os.remove(os.path.join(target_dir, f))
                    self.monitoring.logger_adapter.warning(f"Deleted all files in {target_dir}")
                else:
                    self.monitoring.logger_adapter.warning("The number of jpg files in the directories are equal.")
            else:
                self.monitoring.logger_adapter.warning("The last_scan folder is empty.")

        check_and_delete(source_dir, target_dir)

        # If index.csv doesn't exist, start processing images
        if not Path(csv_path).exists():
            self.monitoring.logger_adapter.info("Prepare_scan_files function starts")
            # Collect all images with png and jpg extensions
            images: list[Path] = []
            for image_suffix in ["png", "jpg"]:
                images.extend(pathlib.Path(source_dir).glob("*." + image_suffix))

            # Sort images based on their modification time
            # images.sort(key=os.path.getmtime)
            images.sort()
            self.monitoring.logger_adapter.info("Scanned images sorted by name (datetime & counter)")

            # Initialize an empty dataframe with columns for the index.csv file
            dataframe = pd.DataFrame(
                columns=["id", "stack_number", "prescription_scanned_pages", "probable_barcodes", "old_filname"]
            )

            # Get the current date and time
            now = datetime.datetime.now()

            # Initialize OCR Reader
            try:
                reader = easyocr.Reader(["en"], str(get_weights_dir()))
            except Exception as e:
                self.monitoring.logger_adapter.error("Failed to Initialize OCR Reader, Retrying...")
                self.monitoring.logger_adapter.exception(RetriedException(e))
                gc.collect()
                reader = easyocr.Reader(["en"], str(get_weights_dir()))

            self.monitoring.logger_adapter.info("Processing each image in the sorted list")

            if progress_bar:
                progress_bar["counter"] = ModifiedDict({"value": 0})  # type: ignore[index]
            # Process each image in the sorted list
            for index, filepath in enumerate(images):
                if progress_bar:
                    progress_bar["counter"].value += 1  # type: ignore[index,attr-defined]
                # Read the image and adjust its contrast and brightness
                img = cv2.imread(filepath.as_posix())
                img_adj = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)[1]
                img_adj_1 = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)[1]
                img_adj_2 = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)[1]
                # Decode any barcodes present in the image
                prescription_barcodes = self.retrieve_prescription_barcodes(filepath, img_adj)
                probable_barcodes: str = ""
                # Extract the barcode data, if available
                if len(prescription_barcodes) > 0:
                    barcode = prescription_barcodes.pop().data.decode("utf-8")
                else:
                    # Probability that a vertical strike exists. We need to get back to the original
                    # image (not binary) in order to find the barcode.
                    prescription_barcodes = self.retrieve_prescription_barcodes(filepath, img_adj_1)
                    # If we have not found during the previous two phases
                    if not prescription_barcodes:
                        prescription_barcodes = self.retrieve_prescription_barcodes(filepath, img_adj_2)

                    # If we have not found during the previous two phases
                    if not prescription_barcodes:
                        barcode, probable_barcodes = get_barcode_ocr(reader, filepath, monitoring=self.monitoring)
                    else:
                        barcode = prescription_barcodes.pop().data.decode("utf-8")
                # Count existing barcodes in the dataframe
                existing_barcodes = dataframe[dataframe.id == barcode].shape[0]

                # Construct the target file name using date, barcode, and
                # existing barcode count
                date_str = now.strftime("%Y%m%d")
                target_file_name = (
                    date_str + "_" + barcode + "_" + str(existing_barcodes + 1).zfill(3) + filepath.suffix
                )

                # Add a new row to the dataframe with the barcode, index,
                # and target file name
                dataframe.loc[len(dataframe.index)] = [
                    barcode,
                    index,
                    target_file_name,
                    probable_barcodes,
                    filepath.name,
                ]

                # Copy the image file to the target directory
                # with the new file name
                target_file = target_dir / target_file_name
                shutil.copyfile(filepath, target_file)

                self.monitoring.logger_adapter.info(
                    f"Processing image {filepath.name}, " f"barcode detected={barcode}, saved as {target_file_name}"
                )

            # Save the index.csv file to the target directory
            index_df = pd.DataFrame(
                dataframe,
                columns=["id", "stack_number", "prescription_scanned_pages", "probable_barcodes", "old_filname"],
            )
            index_df.to_csv(csv_path, index=False)
            self.monitoring.logger_adapter.info(f"Scans Index file created: {csv_path}")

        else:
            self.monitoring.logger_adapter.warning("The index csv path exists and the preparation was skipped.")

    def retrieve_prescription_barcodes(self, filepath: Path, img: NDArray) -> list[Decoded]:
        try:
            detected_barcodes = decode(img)
        except Exception as e:
            self.monitoring.logger_adapter.error(f"Failed to Decode Barcode, Skipping barcode detection for {filepath}")
            self.monitoring.logger_adapter.exception(SkippedException(e))
            detected_barcodes = []
        prescription_barcodes = [
            barcode
            for barcode in detected_barcodes
            if len(barcode.data.decode("utf-8")) == 16
            or (barcode.type == "CODE128" and len(barcode.data.decode("utf-8")) == 13)
        ]
        return prescription_barcodes

    def validate_and_rename_scanned_filenames(self, target_dir: Path, idika_barcodes: list[str], username: str) -> None:
        csv_path = target_dir / "index.csv"
        index_df = pd.read_csv(csv_path)

        for index, row in index_df.iterrows():
            if str(row["probable_barcodes"]) not in ["nan", "[]"]:
                probable_barcodes = str(row["probable_barcodes"]).split("|")
                matched_barcodes = list(set(probable_barcodes) & set(idika_barcodes))

                if matched_barcodes:
                    old_filename = index_df.loc[index, "prescription_scanned_pages"]
                    exec_date = old_filename.split("_", 1)[0]
                    new_filename = f"{exec_date}_{matched_barcodes[0]}_001.jpg"
                    self.runs_counter.add(1, {"username": username})
                    self.monitoring.logger_adapter.warning(
                        "1. The barcode matched with the idika list "
                        + f"| Probable barcode:{probable_barcodes}={matched_barcodes}"
                    )

                    if os.path.exists(new_filename):
                        count = 2
                        while True:
                            new_filename = f"{exec_date}_{matched_barcodes[0]}_{count:03d}.jpg"
                            self.monitoring.logger_adapter.warning(
                                "2. The barcode matched with the idika list "
                                + f"| Probable barcode:{probable_barcodes}={matched_barcodes}"
                            )
                            if not os.path.exists(new_filename):
                                self.monitoring.logger_adapter.warning(
                                    "3. The barcode matched with the idika list "
                                    + f"| Probable barcode:{probable_barcodes}={matched_barcodes}"
                                )
                                break
                            count += 1
                    if not os.path.exists(new_filename):
                        try:
                            index_df.loc[index, "prescription_scanned_pages"] = new_filename
                            index_df.loc[index, "id"] = matched_barcodes[0]
                            new_filename = index_df.loc[index, "prescription_scanned_pages"]
                            os.rename(target_dir / old_filename, target_dir / new_filename)
                        except FileExistsError:
                            self.monitoring.logger_adapter.warning(
                                f"File trying to be renamed {new_filename} already exists"
                            )
                            continue
        index_df.to_csv(csv_path, index=False)
