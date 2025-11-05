from __future__ import annotations

import datetime
import itertools
import logging
import math
import multiprocessing
import os
import pathlib
import re
import time
from collections.abc import Generator
from dataclasses import dataclass
from functools import partial
from logging.handlers import QueueHandler
from multiprocessing import Manager, Pool, Queue
from threading import Lock
from typing import Any

import pandas as pd
import pytz
import requests
import xmltodict
from opentelemetry.trace import Tracer, get_tracer

from src.autoscription.core.data_types import (
    daily_pres_dtype,
    dosages_dtype,
    injection_pages_dtype,
)
from src.autoscription.core.errors import SignInException
from src.autoscription.core.logging import Monitoring, log_queue


def divide_chunks(
    data: list[dict[str, Any]], size: int = 4
) -> Generator[list[dict[str, Any]], Any, None]:
    for i in range(0, len(data), size):
        yield data[i : i + size]


def download_prescriptions(
    ps_ids: list[dict[str, Any]],
    download_dir: pathlib.Path,
    download_counter: int,
    shared_counter: Any,
    lock: Lock | None,
    log_queue: Any,
    config: dict[str, Any],
    monitoring: Monitoring,
) -> tuple[list[dict[str, str]], list[str]]:
    # create a logger
    logger = logging.getLogger("")
    monitoring.config_azure_monitor(logger=logger)
    tracer: Tracer = get_tracer(__name__)
    with tracer.start_as_current_span(
        "check_prescriptions", context=monitoring.get_parent_context()
    ):  # add a handler that uses the shared queue
        if log_queue:
            logger.addHandler(QueueHandler(log_queue))
        curr_proc = multiprocessing.current_process()
        if curr_proc._identity:
            download_dir = download_dir / str(curr_proc._identity[0])
        else:
            download_dir = download_dir / "0"
        download_dir.mkdir(parents=True, exist_ok=True)
        delete_mismatched_files(download_dir, monitoring=monitoring)
        execution_timestamps = []
        failed_multi_prescriptions = []
        for ps_id in ps_ids:
            download_counter = download_counter + 1
            monitoring.logger_adapter.info(
                f"{download_counter}/{len(ps_ids)} : {ps_id}"
            )
            barcode = ps_id["prescription"]
            url_end = f"pharmacistapi/api/v1/prescriptions/print/{barcode}"
            headers = {
                "Authorization": f"Basic {config['credentials_base64']}",
                "api-key": config["api_key"],
                "Accept": "application/pdf, application/xml",
                "Content-Type": "application/xml",
            }

            # Define the request payload with your parameters
            params = {"executionNo": ps_id["execution"]}

            # Send a GET request with the headers
            max_retries = 4
            retry_interval = 10

            for _ in range(max_retries):
                try:
                    response = requests.get(
                        f"{config['base_url']}/{url_end}",
                        headers=headers,
                        params=params,
                    )
                    # Check for a successful response
                    if response.status_code == 200:
                        break  # Success, exit the loop
                except requests.exceptions.ConnectionError:
                    monitoring.logger_adapter.warning(
                        f"ConnectionError occurred. Retrying in {retry_interval} seconds..."
                    )
                    time.sleep(retry_interval)
            else:
                monitoring.logger_adapter.error("Max retries reached. Request failed.")

            # Check the response
            if response.status_code == 200:
                if str(ps_id["execution"]) != "1":
                    execution_timestamps.append(ps_id)
                # Open the PDF file in binary write mode and write the content from the API response.
                with open(
                    download_dir / f"{ps_id['prescription']}_{ps_id['execution']}.pdf",
                    "wb",
                ) as pdf_file:
                    pdf_file.write(response.content)
            else:
                failed_multi_prescriptions.extend(ps_id["prescription"])
            if lock:
                with lock:
                    shared_counter.value += 1
            delete_mismatched_files(download_dir, monitoring=monitoring)
        return execution_timestamps, failed_multi_prescriptions


@dataclass
class ListSimilarity:
    ratio: float
    common_elements: set[Any]


# TODO: Update function to check similarity in both lists
def list_similarity(list1: list[Any], list2: list[Any]) -> ListSimilarity:
    common_elements = set(list1).intersection(set(list2))
    len_common_elements = len(common_elements)
    total_unique_elements_list_1 = len(set(list1))
    similarity_ratio: float
    if total_unique_elements_list_1 == 0:
        similarity_ratio = 0
    else:
        similarity_ratio = len_common_elements / total_unique_elements_list_1

    return ListSimilarity(ratio=similarity_ratio, common_elements=common_elements)


def retrieve_prescription_ids(
    ps_ids: list[dict[str, Any]],
    download_dir: pathlib.Path,
    config: dict[str, Any],
    multiprocessing_controls: list[tuple[Manager, Pool, Queue]],  # type: ignore[valid-type, type-arg]
    progress_bar: dict[str, Any],
    monitoring: Monitoring,
) -> list[str]:
    monitoring.logger_adapter.info("Username & Password Set")
    if progress_bar:
        progress_bar["total_prescriptions"] = len(ps_ids)
    monitoring.logger_adapter.info("Prescription IDs collected")
    # TODO: extract to method in SearchPage
    threads = multiprocessing.cpu_count()
    if threads >= 3:
        threads = 3
    chunk_size: int = math.ceil(len(ps_ids) / threads)
    monitoring.logger_adapter.warning(
        f"Chunk size (number of prescriptions / cpu count) : {chunk_size}"
    )
    # will work even if the length of the dataframe is not evenly divisible
    # by num_processes
    chunks: list[list[dict[str, Any]]] = [
        item for item in divide_chunks(ps_ids, chunk_size)
    ]
    # apply the parser function to each chunk in the list
    lock: Lock | None
    counter = None
    manager = multiprocessing.Manager()
    lock = None  # Why do we need this one?
    if progress_bar:
        lock = manager.Lock()
        counter = manager.Value(int, 0)
        progress_bar["counter"] = counter
    logger_queue = manager.Queue()
    pool = multiprocessing.Pool(threads)
    # Apply the parser function to each chunk in the list using apply_async
    return_items = pool.map(
        partial(
            download_prescriptions,
            download_dir=download_dir,
            download_counter=0,
            lock=lock,
            shared_counter=counter,
            log_queue=logger_queue,
            config=config,
            monitoring=monitoring,
        ),
        chunks,
    )
    multiprocessing_controls.append((manager, pool, logger_queue))  # type: ignore[arg-type]
    pool.close()
    pool.join()
    log_queue(logger_queue)
    execution_timestamps_list, failed_multi_prescriptions_list = zip(*return_items)
    failed_multi_prescriptions = list(itertools.chain(*failed_multi_prescriptions_list))
    return failed_multi_prescriptions


def delete_mismatched_files(download_dir: pathlib.Path, monitoring: Monitoring) -> None:
    # Define the regex pattern for the file name
    pattern = re.compile(r"^\d{13}_\d+\.pdf$")

    # Iterate through the files in the directory
    for filename in os.listdir(download_dir):
        # Check if the file name matches the pattern
        if not pattern.match(filename):
            # If the file name doesn't match the pattern, delete the file
            file_path = os.path.join(download_dir, filename)
            # Check if the file has a .pdf extension
            if file_path.lower().endswith(".pdf"):
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        monitoring.logger_adapter.warning(
                            f"A file has been deleted : {file_path}"
                        )
                except Exception as e:
                    monitoring.logger_adapter.error(
                        f"Failed to delete {file_path}. Reason: {e}"
                    )


def _get_daily_pres_list(
    download_dir: pathlib.Path, date: str, config: dict[str, Any]
) -> list[dict[str, Any]]:
    url_end = "pharmacistapi/api/v1/prescription-execution/search"
    headers = {
        "Authorization": f"Basic {config['credentials_base64']}",
        "api-key": config["api_key"],
        "Accept": "application/x-hl7, application/xml",
        "Content-Type": "application/xml",
    }
    params = {"executionDate": date, "pharmacyId": config["pharmacy_id"], "page": "0"}

    # Make the first request to get the total number of pages
    response = requests.get(
        f"{config['base_url']}/{url_end}", headers=headers, params=params
    )
    data = xmltodict.parse(response.text)
    total_pages = int(data["Page"]["totalPages"])
    prescriptions = []
    # Assume the API returns local Athens time (even though it uses "+0000") – so localize accordingly.
    athens_tz = pytz.timezone("Europe/Athens")

    # Loop through the pages in reverse order
    for page in range(total_pages, 0, -1):
        params["page"] = str(page - 1)
        response = requests.get(
            f"{config['base_url']}/{url_end}", headers=headers, params=params
        )
        data = xmltodict.parse(response.text)
        items = data["Page"]["contents"]["item"]
        if not isinstance(items, list):
            items = [items]
        # Loop through the items
        for item in reversed(items):
            # Parse the timestamp as a naïve datetime using the format provided.
            naive_dt = datetime.datetime.strptime(item["executionDate"], "%Y-%m-%dT%H:%M:%S.%f+0000")
            # Localize the parsed datetime to Athens timezone instead of assuming UTC.
            execution_timestamp = athens_tz.localize(naive_dt)
            execution_date = str(execution_timestamp.date())
            if execution_date == date:
                prescriptions.append(
                    {
                    "pr_order_timestamp": execution_timestamp.strftime(
                        "%Y-%m-%dT%H:%M:%S.%f%z"
                        ),
                        "prescription": item["prescription"]["barcode"],
                        "execution": item["executionNo"],
                    }
                )
            elif execution_date < date:
                pd.DataFrame(prescriptions).to_csv(
                    str(download_dir / "daily_pres_list.csv"), index=False
                )
                return prescriptions
    pd.DataFrame(prescriptions).to_csv(
        str(download_dir / "daily_pres_list.csv"), index=False
    )
    return prescriptions


def _get_daily_pres_list_df(download_dir: pathlib.Path) -> pd.DataFrame:
    df = pd.read_csv(str(download_dir / "daily_pres_list.csv"))
    #Not sure we need this for the code to work properly
    # Convert the pr_order_timestamp column from its ISO format (with offset) to a tz-aware datetime.
    df["pr_order_timestamp"] = pd.to_datetime(df["pr_order_timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%z")
    # Ensure the datetime is in Athens time (even if the CSV record already has an offset)
    df["pr_order_timestamp"] = df["pr_order_timestamp"].dt.tz_convert("Europe/Athens")
    return df.astype(daily_pres_dtype)


def injection_user_login(config: dict[str, Any], monitoring: Monitoring) -> None:
    # Set up the request headers with Basic Authentication
    headers = {
        "Authorization": f"Basic {config['credentials_base64']}",
        "api-key": config["api_key"],
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    url_end = "vaccinationregistry/influenzavacregistry/api/v2/users/me"
    response = requests.get(f"{config['base_url']}/{url_end}", headers=headers)

    if response.status_code != 200:
        monitoring.logger_adapter.error(
            f"SignIn Injection API status code: {response.status_code}"
        )
        raise SignInException


def get_injections(
    date: datetime.datetime, config: dict[str, Any], monitoring: Monitoring
) -> tuple[pd.DataFrame, pd.DataFrame]:
    injection_user_login(config=config, monitoring=monitoring)
    url_end = "vaccinationregistry/influenzavacregistry/api/v2/execution/search"
    headers = {
        "Authorization": f"Basic {config['credentials_base64']}",
        "api-key": config["api_key"],
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    pages = []
    dosages = []
    params = {
        "pharmacyId": config["pharmacy_id"],
        "from": str(date),
        "until": str(date),
        "page": 0,
    }
    while True:
        try:
            response = requests.get(
                f"{config['base_url']}/{url_end}", headers=headers, params=params
            )
        except requests.exceptions.ConnectionError:
            raise SignInException
        if response.status_code == 200:
            for item in response.json()["content"]:
                injection_info = {
                    "prescription": item["barcode"],
                    "pharmacist_idika_prescription_full": item["barcode"],
                    "doc_name": "",
                    "scan_last_three_digits": "000",
                    "file_path": None,
                    "type": "pharmacist",
                    "first_execution": True,
                    "digital": True,
                    "100%": False,
                    "stamps_found": 0,
                    "sign_found": 0,
                    "sign_required": 0,
                    "category": 1,
                    "category_name": (
                        item["patient"]["socialInsurance"]["socInsShortName"]
                        if item["patient"]["socialInsurance"]
                        else ""
                    ),
                    "unit": "",
                    "sign_check": False,
                    "stamps_check": False,
                    "coupon_check": False,
                    "coupon_precheck": False,
                    "coupons_found": "",
                    "coupons_required": 0,
                    "stamps_required": 0,
                    "pdf_file_name": "",
                    "page": 1,
                    "pages": 1,
                    "patient_name": item["patient"]["lastName"]
                    + " "
                    + item["patient"]["firstName"],
                    "execution": 1,
                    "pr_order_timestamp": datetime.datetime.strptime(
                        item["executionDate"], "%Y-%m-%dT%H:%M:%S"
                    )
                    .replace(tzinfo=pytz.utc)
                    .astimezone(pytz.timezone("Europe/Athens"))
                    .strftime("%Y-%m-%dT%H:%M:%S.%f+0000"),
                    "dosage_check": "True",
                    "document_type": "injection",
                    "insurance_amount": item["insurancePartAmt"],
                    "patient_amount": item["patientPartAmt"],
                    "missing_tapes": "",
                    "surplus_tapes": "",
                }
                patient_part = (
                    f'{int(float(item["patientPartAmt"]) / float(item["totalPrice"]))}'
                    if item["totalPrice"]
                    else "0%"
                )
                diff = (
                    str(
                        abs(
                            float(item["insurancePartAmt"])
                            - float(item["patientPartAmt"])
                        )
                    ).replace(".", ",")
                    if item["patientPartAmt"]
                    else 0.0
                )
                dosage_info = {
                    "boxes_required": 1,
                    "boxes_provided": item["quantity"] if item["quantity"] else 1,
                    "dosage_category": "ΕΝΕΣΗ",
                    "dosage_description": (
                        item["icd10"]["title"] if item["icd10"] else ""
                    ),
                    "description": item["medicine"]["commercialNameOnly"],
                    "pills_required": 1,
                    "description_quantity": 1,
                    "dosage": 1,
                    "dosage_qnt": 1,
                    "dosage_repeat": 1,
                    "patient_part": patient_part,
                    "unit_price": 0.0,
                    "patient_return": 0.0,
                    "total": item["totalPrice"] if item["totalPrice"] else 0.0,
                    "diff": diff,
                    "patient_contrib": (
                        item["patientPartAmt"] if item["patientPartAmt"] else 0.0
                    ),
                    "gov_contrib": (
                        item["insurancePartAmt"] if item["insurancePartAmt"] else 0.0
                    ),
                    "description_org": item["medicine"]["commercialNameOnly"],
                    "dosage_check": "True",
                    "prescription": item["barcode"],
                    "scan_last_three_digits": "100",
                    "boxes_provided_multiple_executions": 1,
                    "is_past_partial_exec": False,
                }
                if (
                    datetime.datetime.strptime(
                        injection_info["pr_order_timestamp"],
                        "%Y-%m-%dT%H:%M:%S.%f+0000",
                    ).date()
                    == date
                ):
                    # if barcode exists and the prescription does
                    # not have a cancelDate (meaning it is canceled)
                    # then append
                    if item["barcode"] and not item["cancelDate"]:
                        monitoring.logger_adapter.warning(
                            f"API Injections: {item['barcode']} , "
                            f"{datetime.datetime.strptime(item['executionDate'], '%Y-%m-%dT%H:%M:%S')}"
                        )
                        pages.append(injection_info)
                        dosages.append(dosage_info)
            if response.json()["lastPage"]:
                break
        else:
            monitoring.logger_adapter.error(
                f"Loop Injection API status code: {response.status_code}"
            )
            raise SignInException
        params["page"] += 1
    if len(pages) > 0:
        pages_df = pd.DataFrame.from_dict(pages)
    else:
        pages_df = pd.DataFrame(
            columns=[
                "prescription",
                "pharmacist_idika_prescription_full",
                "doc_name",
                "scan_last_three_digits",
                "file_path",
                "type",
                "first_execution",
                "digital",
                "100%",
                "stamps_found",
                "sign_found",
                "sign_required",
                "category",
                "category_name",
                "unit",
                "sign_check",
                "stamps_check",
                "coupon_check",
                "coupon_precheck",
                "coupons_found",
                "coupons_required",
                "stamps_required",
                "pdf_file_name",
                "page",
                "pages",
                "patient_name",
                "execution",
                "pr_order_timestamp",
                "dosage_check",
                "document_type",
                "insurance_amount",
                "patient_amount",
                "missing_tapes",
                "surplus_tapes",
            ]
        )

    if len(dosages) > 0:
        dosages_df = pd.DataFrame.from_dict(dosages)
    else:
        dosages_df = pd.DataFrame(
            columns=[
                "boxes_required",
                "boxes_provided",
                "dosage_category",
                "dosage_description",
                "description",
                "pills_required",
                "description_quantity",
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

    # TODO: Test user should create csv (backend not found in the config)
    # if config["backend"]["file_uploader"]["test_user"]:
    #     dosages_df.to_csv("get_injections_dosages_df_output.csv")
    #     pages_df.to_csv("get_injections_pages_df_output.csv")

    pages_df = pages_df.astype(injection_pages_dtype)
    dosages_df = dosages_df.astype(dosages_dtype)
    monitoring.logger_adapter.warning(f"Injection prescriptions: {len(pages)}")
    return pages_df, dosages_df
