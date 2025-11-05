from __future__ import annotations

import gc
import glob
import itertools
import logging
import math
import multiprocessing
import re
from collections import defaultdict
from collections.abc import Generator
from itertools import islice
from logging.handlers import QueueHandler
from math import ceil
from multiprocessing import Manager, Pool
from multiprocessing.managers import ValueProxy
from pathlib import Path
from queue import Queue
from typing import Any, Optional

import cv2
import pandas as pd
import pdfplumber
from opentelemetry.trace import Tracer, get_tracer
from pandas import DataFrame
from PIL.Image import Image
from PyPDF2 import PdfReader

from src.autoscription.core.data_types import pages_dtype
from src.autoscription.core.errors import (
    ExtractMetadataFailedException,
    RetriedException,
    SkippedException,
)
from src.autoscription.core.logging import Monitoring, log_queue
from src.autoscription.core.utils import (
    draw_barcodes,
    draw_bottom_right_templates,
    draw_signature_areas,
    draw_signatures,
    draw_stamps,
    ipython_clear_output,
    remove_templates,
    show_image,
)
from src.autoscription.coupons_detection.utils import (
    barcode_reader,
    get_authenticity_tapes,
    match_missing_coupons,
)
from src.autoscription.dosage_extractor.product_number_extractor import (
    NO_NEED_TO_IDENTIFY,
    UNABLE_TO_IDENTIFY,
    number_of_products_per_container,
)
from src.autoscription.signature_detection.signature_detection import SignatureDetector
from src.autoscription.stamp_detection import Detector


def divide_chunks(data: dict[str, Any], size: int = 5) -> Generator[dict[str, Any], Any, None]:
    it = iter(data)
    for _ in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}


def extract_3_digits(text: str) -> str:
    end = text.find("ΘΕΡΑΠΕΙΑ :")
    result = text[:end][-3:]
    if result.isdigit():
        return result
    else:
        end = text.find("ΕΠΑΝΑΛΗΨΗ :")
        return text[:end][-3:]


def extract_text(file_name: str) -> tuple[int, str]:
    reader = PdfReader(file_name)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return len(reader.pages), text


def extract_pills(x: str) -> int:
    try:
        expr = re.findall(r"\w\s*X\s*\d+|\d+X\d+", x)[0].replace(" ", "")
        return (
            int(expr.split("X")[0]) * int(expr.split("X")[-1])
            if expr.split("X")[0].isdigit()
            else int(expr.split("X")[-1])
        )
    except IndexError:
        return 999


# TODO: rewrite function, check if repeats is str before using it, return only int
def extract_dosage_repeat(text: str) -> int | float | str:
    if not text:
        return 0
    elif "εφάπαξ" in text:
        return 999
    repeats = text.strip().replace("κάθε ", "").split(" ", 1)[0]
    if "εβδομάδα" in text:
        return int(repeats) / 7
    elif "εβδομάδες" in text:
        return 1 / (7 * int(repeats))
    elif repeats.isdigit():
        return repeats
    else:
        return 1


def clean_description(description: str) -> str:
    return (
        re.sub(r"\([^)]*\)", "", description)
        .upper()
        .replace("Χ", "X")
        .replace("Α", "A")
        .replace("Ε", "E")
        .replace("Ι", "I")
        .replace("Υ", "Y")
        .replace("Ο", "O")
        .replace("Η", "H")
        .replace("Ό", "O")
        .replace("Ί", "I")
        .replace("Ά", "A")
        .replace("Έ", "E")
        .replace("Ή", "H")
        .replace("Ύ", "Y")
        .replace("Τ", "T")
        .replace("Β", "B")
        .replace("Μ", "M")
        .replace("Ρ", "P")
        .replace("Ν", "N")
        .replace("Κ", "K")
        .strip()
    )


# TODO: change the signature to return string, no need for true and
# false if we have 3 cases
def generate_dosage_check(boxes_provided: float, boxes_required: int, dosage: int, dosage_qnt: int) -> str:
    try:
        boxes_provided = float(boxes_provided)
    except ValueError:
        return "False"
    if boxes_provided == 1:
        return "True"
    elif float(dosage_qnt) == 999:
        return "True"
    elif float(dosage) == 999 or float(dosage) == 0:
        return "False"
    elif boxes_provided > float(boxes_required):
        return "False"
    elif boxes_provided == float(boxes_required):
        return "True"
    else:
        return "CHECK"


def get_boxes_required(row: dict[str, int]) -> int:
    # dosage_qnt 999
    if row["dosage_qnt"] == 999:
        return row["boxes_provided"]
    # data correlation
    elif row["description_quantity"] == UNABLE_TO_IDENTIFY:
        return 1
    elif row["description_quantity"] == NO_NEED_TO_IDENTIFY:
        return 999
    return ceil(row["pills_required"] / row["description_quantity"])


def extract_dosages(row: str) -> float:
    if not row:
        return 0.0  # check this out "0"

    row = row.strip().upper()  # Work in uppercase for consistency

    # Attempt to find a quantity followed by "ML" dosage
    combined_match = re.search(r"(\d+\.?\d*)\s*ΠΟΣ\D+(\d+\.?\d*)\s*ML", row)
    if combined_match:
        quantity, ml_dosage = map(float, combined_match.groups())
        return quantity * ml_dosage

    # If no combined "quantity and ML" dosage, check for ML dosage
    ml_match = re.search(r"(\d+\.?\d*)\s*ML", row)
    if ml_match:
        return float(ml_match.group(1))

    # If no explicit "ML" dosage, proceed with other checks
    number_match = re.search(r"(\d+)/(\d+)|(\d+\.?\d*)", row)
    if number_match:
        # Fractional number
        if number_match.group(1) and number_match.group(2):
            numerator, denominator = map(int, [number_match.group(1), number_match.group(2)])
            number = numerator / denominator
        else:  # Decimal or integer number
            number = float(number_match.group(3))

        # Apply conversion for specific terms indicating drops or similar measures
        if any(
            term in row
            for term in ["ΟΦΘ.ΣΤΑΓΟΝΕΣ", "ΟΦΘΑΛΜΙΚΕΣ", "ΠΟΣ.ΣΤΑΓΟΝΕΣ", "ΠΟΣΙΜΕΣ", "ΟΤΙΚΟ", "ΥΠΟΓΛΩΣΣΙΕΣ", "ΕΝΑΙΩΡΗΜΑ"]
        ):
            return number * 0.05
        else:
            return number

    return 0.0


def clean_boxes_provided(boxes: str) -> Optional[int]:
    try:
        # Remove content within parentheses
        no_parentheses = re.sub(r"\(.*?\)", "", boxes)

        # Remove unwanted characters
        cleaned_boxes = no_parentheses.replace("-", "").replace("\n", "")

        # Find all number sequences in the string
        numbers = re.findall(r"\d+", cleaned_boxes)

        if numbers:
            # If there's at least one number, return the first one converted to integer
            return int(numbers[0])
        else:
            # If there are no numbers, return None
            return None
    except ValueError:
        # If anything goes wrong, return None
        return 555


def extract_table(file_name: str) -> DataFrame:
    table_columns: list[str] = [
        "description",
        "patient_part",
        "boxes_provided",
        "unit_price",
        "patient_return",
        "total",
        "diff",
        "patient_contrib",
        "gov_contrib",
    ]

    dataframe_columns: list[str] = [
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
    ]
    columns_to_replace_comma = ["unit_price", "patient_return", "total", "diff", "patient_contrib", "gov_contrib"]

    pdf = pdfplumber.open(file_name)
    # from the first page, get all the tables and ignore the first 3 tables
    table = pdf.pages[0].extract_table()[3:]
    df = pd.DataFrame(table, columns=table_columns)
    df[columns_to_replace_comma] = df[columns_to_replace_comma].apply(lambda x: x.str.replace(",", "."))
    for col in columns_to_replace_comma:
        df[col] = pd.to_numeric(df[col].str.replace(",", "."), errors="coerce")
    # TODO:
    # ValueError: invalid literal for int() with base 10
    # Mostly about galiniko skeuasma. When the system breaks here it does not flag the broken prescription.
    # In pages df the 100% flag which is deduced by the table is left without a flag.
    # The report that excluded the 100% in count of prescriptions loses one as it is not 100%==False but 100%==""
    # fixed with the clean_boxes_provided function???

    # df["boxes_provided"] = df["boxes_provided"].apply(
    #     lambda boxes: boxes.strip().replace("g", "").replace("mg", "").replace("-", "").replace("\n","") \
    #     .replace("(σταγονα)","").replace("(","").replace(")","")
    # )

    df["boxes_provided"] = df["boxes_provided"].apply(clean_boxes_provided)

    df[["description", "dosage"]] = df["description"].str.replace("\n", " ").str.split("ΔΟΣΟΛΟΓΙΑ :", 1, expand=True)
    df["dosage_description"] = df["dosage"]
    df[["dosage", "dosage_qnt", "dosage_repeat"]] = df["dosage"].str.split("x", n=2, expand=True)
    df["dosage_category"] = df["dosage"].str.strip().str.split(" ", n=2).str[1]
    # THIS IS WHERE THE DOSAGES ARE CHECKED
    df["description_org"] = df["description"]
    df["description"] = df["description"].apply(lambda x: clean_description(x))
    number_of_products_per_container_results = df.apply(
        lambda x: number_of_products_per_container(x["dosage_category"], x["description"]), axis=1, result_type="expand"
    )
    df["description_quantity"] = number_of_products_per_container_results[0]
    df["description_quantity_rule"] = number_of_products_per_container_results[1]

    df["dosage"] = df["dosage"].apply(lambda row: extract_dosages(row)).astype(pd.StringDtype())
    df["dosage_qnt"] = df["dosage_qnt"].apply(lambda x: float(extract_dosage_repeat(x)))
    df["dosage_repeat"] = df["dosage_repeat"].apply(lambda x: int(x.strip().split(" ", 1)[0]) if x else 0)
    df["pills_required"] = df.apply(
        lambda row: float(row["dosage"]) * row["dosage_qnt"] * float(row["dosage_repeat"]),
        axis=1,
    )
    df["boxes_required"] = df.apply(lambda row: get_boxes_required(row), axis=1)
    df["dosage_check"] = df.apply(
        lambda row: generate_dosage_check(
            row["boxes_provided"],
            row["boxes_required"],
            row["dosage"],
            row["dosage_qnt"],
        ),
        axis=1,
    )
    # TODO: here for example in galinika which are not deducted correctly
    # it will break as it will not be able to change to int a string
    df["boxes_provided"] = df["boxes_provided"].astype(float)

    df = df.reset_index(drop=True)
    df["row"] = df.index
    # extracted_table_df=df[dataframe_columns]
    # extracted_table_df.to_excel(extracted_table_df)
    return df[dataframe_columns]


def is_immatereal(text: str) -> bool:
    if "Άυλη συνταγογράφηση" in text:
        return True
    else:
        return False


# TODO: update to bool instead of int
def is_prototype(text: str) -> int:
    if "επιθυμώ να λάβω ακριβότερο φάρμακο" in text:
        return 1
    else:
        return 0


def get_category(text: str) -> int | None:
    try:
        for line in text.split("\n"):
            if "ΕΩΣ :" in line:
                return int(line.split("/")[-1].strip()[2])
    except IndexError:
        return 8
    return None


# def get_category_name(text):
#     if "Ε.Δ.Ο.Ε.Α.Π." in text:
#         return "Ε.Δ.Ο.Ε.Α.Π."
#     mk1 = text.find("ΚΟΙΝΩΝΙΚΗΣ ΑΣΦΑΛΙΣΗΣ") + 23
#     mk2 = text.find("Σ Υ Ν Τ Α Γ Η", mk1)
#     return text[mk1:mk2]


# Do not delete
# def get_category_name(text):
#     mk1 = text.find('ΚΟΙΝΩΝΙΚΗΣ ΑΣΦΑΛΙΣΗΣ')
#     if mk1 != -1:
#         mk1 += 23
#     else:
#         mk1 = 4
#     mk2 = text.find('Σ Υ Ν Τ Α Γ Η', mk1)
#     return text[mk1: mk2]


def get_category_name(text: str) -> str:
    mk1 = text.find("ΚΟΙΝΩΝΙΚΗΣ ΑΣΦΑΛΙΣΗΣ")
    if mk1 != -1:
        mk1 += len("ΚΟΙΝΩΝΙΚΗΣ ΑΣΦΑΛΙΣΗΣ")
    else:
        mk1 = text.find("ΥΠΟΥΡΓΕΙΟ ΕΘΝΙΚΗΣ ΑΜΥΝΑΣ")
        if mk1 != -1:
            mk1 += len("ΥΠΟΥΡΓΕΙΟ ΕΘΝΙΚΗΣ ΑΜΥΝΑΣ")
        else:
            mk1 = 4
    mk2 = text.find("Σ Υ Ν Τ Α Γ Η", mk1)
    return text[mk1:mk2].strip().replace("\n", " ")


def get_names(text: str) -> tuple[str, str]:
    doc_surname_start = text.find("ΕΠΩΝΥΜΟ :") + 10
    doc_surname_end = text.find(" ΕΠΩΝΥΜΟ :", doc_surname_start)
    patient_surname_end = text.find("\nΟΝΟΜΑ :", doc_surname_end)
    patient_surname = text[doc_surname_end + 11 : patient_surname_end]
    doc_surname = text[doc_surname_start:doc_surname_end]
    doc_name_start = text.find("ΟΝΟΜΑ :") + 8
    doc_name_end = text.find(" ΟΝΟΜΑ :", doc_name_start)
    doc_name = text[doc_name_start:doc_name_end]
    patient_name_end = text.find("\nΑ.Μ.Κ.Α.", doc_name_end)
    patient_name = text[doc_name_end + 9 : patient_name_end]
    return f"{doc_surname} {doc_name}", f"{patient_surname} {patient_name}"


def find_unit(page: str) -> str:
    mk1 = page.find("ΜΟΝΑΔΑ : ") + 9
    mk2 = page.find(" ΔΙΕΥΘΥΝΣΗ", mk1)
    return page[mk1:mk2]


def find_insurance_amount(text: str, file: str, monitoring: Monitoring) -> Optional[float]:
    phrase = "ΠΛΗΡΩΤΕΟ ΠΟΣΟ ΑΠΟ ΤΑΜΕΙΟ €"
    start_pos = text.find(phrase)
    if start_pos == -1:
        monitoring.logger_adapter.exception(
            f"Phrase '{phrase}' not found in text", SkippedException(ValueError(f"Phrase '{phrase}' not found in text"))
        )
        return None
    value_start_pos = start_pos + len(phrase)
    value_str = text[value_start_pos:].split("\n")[0].strip().replace(".", "").replace(",", ".")
    try:
        return float(value_str)
    except ValueError as ve:
        monitoring.logger_adapter.exception(
            f"Failed to convert '{value_str}' to float in file: {file}", SkippedException(ve)
        )
        return None


def find_patient_amount(text: str, file: str, monitoring: Monitoring) -> Optional[float]:
    phrase = "ΠΛΗΡΩΤΕΟ ΠΟΣΟ ΑΠΟ ΑΣΦ/ΝΟ €"
    start_pos = text.find(phrase)
    if start_pos == -1:
        monitoring.logger_adapter.exception(
            f"Phrase '{phrase}' not found in text", SkippedException(ValueError(f"Phrase '{phrase}' not found in text"))
        )
        return None
    value_start_pos = start_pos + len(phrase)
    value_str = text[value_start_pos:].split("\n")[0].strip().replace(".", "").replace(",", ".")
    try:
        return float(value_str)
    except ValueError as ve:
        monitoring.logger_adapter.exception(
            f"Failed to convert '{value_str}' to float in file: {file}", SkippedException(ve)
        )
        return None


def extract_metadata(
    dir_list: list[str], specific_prescriptions: Optional[list[str]], monitoring: Monitoring
) -> dict[str, Any]:
    # Initialize the checks dictionary and aggregated_stats dictionary
    monitoring.logger_adapter.info("The metadata extraction from pdfs has started")

    if len(dir_list) == 0:
        monitoring.logger_adapter.error("The pdf prescription folder is empty. Imminent crash.")

    checks: defaultdict[str, Any] = defaultdict(lambda: {})
    aggregated_stats: dict[str, Any] = {
        "total_presciptions": 0,
        "participation_bool": 0,
        "categories": {1: 0, 2: 0, 3: 0, 4: 0, 8: 0},
    }
    counter = 0

    for file in dir_list:
        try:
            counter = counter + 1

            # Extract the prescription ID from the filename
            file_name = file.split("/")[-1].split("\\")[-1]
            prescription_id, execution = file_name.replace(".pdf", "").split("_")

            # If specific_prescriptions is not empty and prescription_id is
            # not in specific_prescriptions, skip the current iteration
            if specific_prescriptions and prescription_id not in specific_prescriptions:
                continue

            # Extract the number of pages and text content from the file
            pages, text = extract_text(file)

            # Extract the last 3 digits from the text
            idika_3_digits = str(extract_3_digits(text))
            # monitoring.logger_adapter.info(f"idika three digits: {idika_3_digits}")
            monitoring.logger_adapter.info(f"{counter} : {prescription_id}{idika_3_digits}")
            # Populate the checks dictionary with extracted data
            checks[prescription_id][idika_3_digits] = {
                "pharmacist_idika_prescription_full": f"{prescription_id}{idika_3_digits}",
                "document_type": "prescription",
                "first_execution": True if int(idika_3_digits[-1]) in [0, 1] else False,
                "is_digital": is_immatereal(text),
                "unit": find_unit(text),
                "category": get_category(text),
                "category_name": get_category_name(text),
                "is_prototype": is_prototype(text),
                "dosages": pd.DataFrame(),
                "doc_sign_found": 0,
                "pharm_sign_found": 0,
                "doc_stamps_found": 0,
                "pharm_stamps_found": 0,
                "pharm_sign_required": 0,
                "doc_sign_required": 0,
                "pharm_stamps_required": 0,
                "doc_stamps_required": 0,
                "pdf_file_name": file_name,
                "execution": execution,
                "pages": pages,
                "insurance_amount": find_insurance_amount(text, file, monitoring),
                "patient_amount": find_patient_amount(text, file, monitoring),
                "missing_tapes": "",
                "surplus_tapes": "",
            }

            # Extract doctor and patient names from the text
            (
                checks[prescription_id][idika_3_digits]["doc_name"],
                checks[prescription_id][idika_3_digits]["patient_name"],
            ) = get_names(text)

            # checks[prescription_id][idika_3_digits]['3_digits'].append(extract_3_digits(text))
            checks[prescription_id][idika_3_digits]["dosages"] = extract_table(file)

            # Extract patient contribution
            patient_contrib = checks[prescription_id][idika_3_digits]["dosages"]["patient_part"].unique()

            # Determine if the patient has 100% participation
            checks[prescription_id][idika_3_digits]["participation_bool"] = bool(
                len(patient_contrib) == 1 and patient_contrib[0] == "100%"
            )

            # Store the patient's participation value
            checks[prescription_id][idika_3_digits]["participation"] = (
                patient_contrib[0] if len(patient_contrib) == 1 else ""
            )

            # Update aggregated_stats dictionary
            aggregated_stats["total_presciptions"] += 1
            aggregated_stats["categories"][checks[prescription_id][idika_3_digits]["category"]] += 1
            if checks[prescription_id][idika_3_digits]["participation_bool"]:
                aggregated_stats["participation_bool"] += 1

            # Calculate the total paid by the patient
            checks[prescription_id][idika_3_digits]["patient_paid"] = (
                checks[prescription_id][idika_3_digits]["dosages"]["patient_contrib"]
                # .str.replace(".", "")
                # .str.replace(",", ".")
                .apply(float).sum()
            )
            # Calculate the total paid by the government
            checks[prescription_id][idika_3_digits]["gov_paid"] = (
                checks[prescription_id][idika_3_digits]["dosages"]["gov_contrib"]
                # .str.replace(".", "")
                # .str.replace(",", ".")
                .apply(float).sum()
            )

            # Calculate the total number of coupons
            try:
                checks[prescription_id][idika_3_digits]["coupons"] = int(
                    checks[prescription_id][idika_3_digits]["dosages"]["boxes_provided"].apply(int).sum()
                )
            except ValueError:
                checks[prescription_id][idika_3_digits]["coupons"] = 0

        except Exception as e:
            monitoring.logger_adapter.warning(f"Exception_extract_metadata :{e} for {prescription_id}")
            monitoring.logger_adapter.exception(e)
            raise ExtractMetadataFailedException(e)
        ipython_clear_output()
    return checks


def create_pages_df(
    checks: dict[str, Any],
    scan_dir: Path,
    detectors_config: dict[str, Any],
    multiprocessing_controls: list[tuple[Manager, Pool, Queue]],  # type: ignore[valid-type, type-arg]
    monitoring: Monitoring,
    tubro_mode: bool = False,
    is_debug_enabled: bool = False,
    progress_bar: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    stamp_detector = Detector(config=detectors_config["stamp"]["options"])
    monitoring.logger_adapter.info("Create_pages_df functions started.")
    # if the queries are less than the number of processors,
    # run it concurrently
    if len(checks) < 8 or not tubro_mode:
        pages_dict_list = check_prescriptions(
            checks,
            detectors_config=detectors_config,
            stamp_detector=stamp_detector,
            scan_dir=scan_dir,
            is_debug_enabled=is_debug_enabled,
            monitoring=monitoring,
        )

    else:  # run it in parallel
        # create a many processes as there are CPUs
        avail_num_processes = multiprocessing.cpu_count()
        num_processes = min(avail_num_processes, int(detectors_config["max_threads"]))
        # calculate the chink size as an integer
        chunk_size = math.ceil(len(checks) / num_processes)
        monitoring.logger_adapter.warning(f"CPU count : {avail_num_processes}")
        monitoring.logger_adapter.info(f"Processes count : {num_processes}")
        monitoring.logger_adapter.warning(f"Chunk size (number of prescriptions / cpu count) : {chunk_size}")
        # will work even if the length of the dataframe is not evenly
        # divisible by num_processes
        chunks = [item for item in divide_chunks(checks, chunk_size)]
        # create the pool with 'num_processes' processes
        lock = None
        # counter = None
        manager = multiprocessing.Manager()
        if progress_bar:
            lock = manager.Lock()
            counter: ValueProxy[int] = manager.Value(int, 0)
            progress_bar["counter"] = counter

        logger_queue = manager.Queue()

        # Create the pool with 'num_processes' processes
        pool = multiprocessing.Pool(num_processes)
        # apply the parser function to each chunk in the list

        # Apply the parser function to each chunk in the list using apply_async
        async_results = []
        for chunk in chunks:
            result = pool.apply_async(
                check_prescriptions,
                args=(
                    chunk,
                    detectors_config,
                    monitoring,
                    stamp_detector,
                    scan_dir,
                    is_debug_enabled,
                    counter,
                    lock,
                    logger_queue,
                ),
            )
            async_results.append(result)
        multiprocessing_controls.append((manager, pool, logger_queue))
        return_items = []
        for result in async_results:
            try:
                return_items.append(result.get())
            except Exception as e:
                # out of memory fix
                monitoring.logger_adapter.error("application failed to append to df - Retrying...", e)
                monitoring.logger_adapter.exception(RetriedException(e))
                gc.collect()
                return_items.append(result.get())

        pool.close()
        pool.join()
        log_queue(logger_queue)
        pages_dict_list = list(itertools.chain(*return_items))
        # with open('checks2.json', 'w') as json_file:
        #     json.dump(pages_dict_list, json_file)
    # with open('checks2.json', 'r') as json_file:
    #     pages_dict_list = json.load(json_file)
    df = pd.DataFrame.from_dict(pages_dict_list).drop_duplicates(
        subset=[
            "prescription_scanned_pages",
            "prescription",
            "scan_last_three_digits",
            "page",
            "execution",
        ]
    )
    int_columns = [
        "coupons_found",
        "coupons_required",
        "execution",
        "prescription",
        "scan_last_three_digits",
        "page",
        "pages",
        "category",
        "sign_found",
        "sign_required",
        "stamps_found",
        "stamps_required",
        "insurance_amount",
        "patient_amount",
    ]
    for col in int_columns:
        df[col] = df[col].fillna(0)
    return df.astype(pages_dtype)


def check_prescriptions(
    checks: dict[str, Any],  # noqa: C901
    detectors_config: dict[str, Any],
    monitoring: Monitoring,
    stamp_detector: Detector,
    scan_dir: Path,
    is_debug_enabled: bool,
    shared_counter: Optional[ValueProxy[int]] = None,
    lock: Optional[multiprocessing.synchronize.Lock] = None,
    log_queue: Optional[Queue[Any]] = None,
) -> list[dict[str, Any]]:
    stamp_detector_config: dict[str, Any] = detectors_config["stamp"]
    signature_detector_config: dict[str, Any] = detectors_config["signature"]
    missing_coupons_config: dict[str, Any] = detectors_config["missing_coupons"]
    counter: int = 0
    pages_dict_list: list[dict[str, Any]] = []
    prescription_id: str
    check: dict[str, Any]
    idika_last_three_digits: str
    data: dict[str, Any]
    file: str
    # create a logger
    logger = logging.getLogger("")
    monitoring.config_azure_monitor(logger=logger)
    # add a handler that uses the shared queue
    # TODO: when end to end comment out the following line
    tracer: Tracer = get_tracer(__name__)
    signature_detector: SignatureDetector = SignatureDetector(
        configuration=signature_detector_config, monitoring=monitoring, is_debug_enabled=is_debug_enabled
    )
    monitoring.logger_adapter.info("check_prescriptions function started.")
    with tracer.start_as_current_span("check_prescriptions", context=monitoring.get_parent_context()):
        if not is_debug_enabled and log_queue:
            logger.addHandler(QueueHandler(log_queue))
        for prescription_id, check in checks.items():
            if __is_prescription_unknown(prescription_id):
                continue
            for idika_last_three_digits, data in check.items():
                counter = counter + 1
                __log_counter(
                    counter=counter,
                    prescription_id=prescription_id,
                    idika_last_three_digits=idika_last_three_digits,
                    monitoring=monitoring,
                )
                __set_prescription_requirements(data)
                __initialise_prescription_values(data)
                pharma_file_found: bool = False
                doctor_file_found: bool = False
                for file in __get_prescription_files(prescription_id=prescription_id, scan_dir=scan_dir):
                    scan_last_three_digits: str = __calculate_scan_last_three_digits(file)
                    page: dict[str, Any] = __get_file_found_page(
                        data,
                        file,
                        scan_last_three_digits,
                        __is_pharm_prescription(scan_last_three_digits),
                        prescription_id,
                    )
                    if idika_last_three_digits != scan_last_three_digits and page["type"] == "pharmacist":
                        continue
                    page_image: Image = cv2.cvtColor(cv2.imread(file), cv2.COLOR_RGB2BGR)
                    # TODO: add debug if statement inside draw function
                    if is_debug_enabled:
                        draw_bottom_right_templates(
                            img=page_image,
                            detectors_preprocessing_config=detectors_config["preprocessing"],
                            monitoring=monitoring,
                        )
                    if page["type"] == "pharmacist":
                        pharma_file_found = True
                    elif page["type"] == "doctor":
                        doctor_file_found = True
                    if __is_not_full_participation(data=data, detectors_config=detectors_config):
                        if page["type"] == "pharmacist":
                            if str(idika_last_three_digits) != str(scan_last_three_digits):
                                continue
                            page_image = update_page_and_data_for_pharmacist(
                                data,
                                detectors_config,
                                file,
                                idika_last_three_digits,
                                is_debug_enabled,
                                missing_coupons_config,
                                page,
                                page_image,
                                scan_last_three_digits,
                                signature_detector_config,
                                stamp_detector,
                                monitoring=monitoring,
                                signature_detector=signature_detector,
                            )
                        else:
                            if __is_prescription_not_digital(data=data, detectors_config=detectors_config):
                                page_image = update_page_and_data_for_doctor(
                                    data,
                                    detectors_config,
                                    file,
                                    is_debug_enabled,
                                    page,
                                    page_image,
                                    signature_detector_config,
                                    stamp_detector,
                                    stamp_detector_config,
                                    monitoring=monitoring,
                                    signature_detector=signature_detector,
                                )
                    else:
                        pharma_file_found = True
                    __update_page_sign_check(page, signature_detector_config)
                    __update_stamp_check(page, stamp_detector_config)
                    # TODO: add debug if statement inside draw function
                    if is_debug_enabled:
                        show_image(page_image)
                    pages_dict_list.append(page)
                if not pharma_file_found:
                    page = __get_file_not_found_page(data, prescription_id)
                    pages_dict_list.append(page)
                if (
                    not doctor_file_found
                    and not data["is_digital"]
                    and is_full_or_first_prescription_execution(idika_last_three_digits=idika_last_three_digits)
                ):
                    page = __get_file_not_found_page(data=data, prescription_id=prescription_id)
                    doctor_page = create_missing_doctor_page(
                        idika_last_three_digits=idika_last_three_digits, page=page.copy()
                    )
                    pages_dict_list.append(doctor_page)
            if lock:
                with lock:
                    if shared_counter:
                        shared_counter.value += 1
        # missing_coupons_ps_ids = __get_missing_coupons_ids(pages_dict_list)
        # __update_pages_dict_list_with_missing_coupons(
        #     missing_coupons_config=missing_coupons_config,
        #     missing_coupons_ps_ids=missing_coupons_ps_ids,
        #     pages_dict_list=pages_dict_list,
        #     monitoring=monitoring,
        # )
        return pages_dict_list


def create_missing_doctor_page(idika_last_three_digits: str, page: dict[str, Any]) -> dict[str, Any]:
    doctor_page = page.copy()
    doctor_page["type"] = "doctor"
    idika_doctor_last_three_digits = f"0{idika_last_three_digits[-2:-1]}0"
    doctor_page["scan_last_three_digits"] = idika_doctor_last_three_digits
    return doctor_page


def is_full_or_first_prescription_execution(idika_last_three_digits: str) -> bool:
    return idika_last_three_digits[-1] in ("0", "1")


def update_page_and_data_for_doctor(
    data: dict[str, Any],
    detectors_config: dict[str, Any],
    file: str,
    is_debug_enabled: bool,
    page: dict[str, Any],
    page_image: Image,
    signature_detector_config: dict[str, Any],
    stamp_detector: Detector,
    stamp_detector_config: dict[str, Any],
    signature_detector: SignatureDetector,
    monitoring: Monitoring,
) -> Image:
    __update_page_and_data_with_signature_information_for_doctor_pres(
        data=data,
        detectors_config=detectors_config,
        file_path=file,
        img=page_image,
        is_debug_enabled=is_debug_enabled,
        page_dict=page,
        signature_detector_config=signature_detector_config,
        monitoring=monitoring,
        signature_detector=signature_detector,
    )
    page_image = __update_page_and_data_with_stamp_information_for_doctor_pres(
        data=data,
        file_path=file,
        img=page_image,
        is_debug_enabled=is_debug_enabled,
        page=page,
        stamp_detector=stamp_detector,
        stamp_detector_config=stamp_detector_config,
        monitoring=monitoring,
    )
    return page_image


def update_page_and_data_for_pharmacist(
    data: dict[str, Any],
    detectors_config: dict[str, Any],
    file: str,
    idika_last_three_digits: str,
    is_debug_enabled: bool,
    missing_coupons_config: dict[str, Any],
    page: dict[str, Any],
    page_image: Image,
    scan_last_three_digits: str,
    signature_detector_config: dict[str, Any],
    stamp_detector: Detector,
    signature_detector: SignatureDetector,
    monitoring: Monitoring,
) -> Image:
    page["page"] = __calculate_page_number(
        data=data, detectors_config=detectors_config, img=page_image, monitoring=monitoring
    )
    __update_page_and_data_with_coupon_information_for_pharm_pres(
        file_path=file,
        img=page_image,
        is_debug_enabled=is_debug_enabled,
        scan_last_three_digits=scan_last_three_digits,
        missing_coupons_config=missing_coupons_config,
        page_dict=page,
        idika_last_three_digits=idika_last_three_digits,
        monitoring=monitoring,
    )
    __update_page_and_data_with_signature_information_for_pharm_pres(
        data=data,
        detectors_config=detectors_config,
        file_path=file,
        img=page_image,
        is_debug_enabled=is_debug_enabled,
        page_dict=page,
        signature_detector_config=signature_detector_config,
        monitoring=monitoring,
        signature_detector=signature_detector,
    )
    page_image = __update_page_and_data_with_stamp_information_for_pharm_pres(
        data, file, page_image, is_debug_enabled, page, stamp_detector, monitoring=monitoring
    )
    return page_image


def __update_stamp_check(page: dict[str, Any], stamp_detector_config: dict[str, Any]) -> None:
    if stamp_detector_config["is_enabled"]:
        page["stamps_check"] = page["stamps_required"] == page["stamps_found"]


def __update_page_sign_check(page: dict[str, Any], signature_detector_config: dict[str, Any]) -> None:
    if signature_detector_config["is_enabled"]:
        page["sign_check"] = page["sign_required"] == page["sign_found"]


def __update_page_and_data_with_stamp_information_for_doctor_pres(
    data: dict[str, Any],
    file_path: str,
    img: Image,
    is_debug_enabled: bool,
    page: dict[str, Any],
    stamp_detector: Detector,
    stamp_detector_config: dict[str, Any],
    monitoring: Monitoring,
) -> Image:
    if stamp_detector_config["is_enabled"]:
        predictions, angle = stamp_detector.count_stamps(file_path, data["doc_stamps_required"], monitoring=monitoring)
        data["doc_stamps_found"] = len(predictions)
        page["stamps_found"] = len(predictions)
        if is_debug_enabled:
            img = draw_stamps(img, predictions, angle)
    return img


def __update_page_and_data_with_signature_information_for_doctor_pres(
    data: dict[str, Any],
    detectors_config: dict[str, Any],
    file_path: str,
    img: Image,
    is_debug_enabled: bool,
    page_dict: dict[str, Any],
    signature_detector_config: dict[str, Any],
    signature_detector: SignatureDetector,
    monitoring: Monitoring,
) -> None:
    if signature_detector_config["is_enabled"]:
        # TODO: pass signature_detector_config in count signatures
        doc_signatures_boxes, signature_count = signature_detector.count_signatures(
            file=file_path,
            horizontal_crop_points=signature_detector_config["options"]["doc_horizontal_crop_points"],
            detectors_preprocessing_config=detectors_config["preprocessing"],
            min_right_area=8000,
        )
        data["doc_sign_found"] += signature_count
        page_dict["sign_found"] = signature_count

        # page_dict["sign_required"] = data["doc_sign_required"] TODO?

        if is_debug_enabled:
            draw_signature_areas(
                img,
                signature_detector_config["options"]["doc_vertical_crop_point"],
                signature_detector_config["options"]["doc_horizontal_crop_points"],
            )
            draw_signatures(img, doc_signatures_boxes, monitoring=monitoring)


def __is_prescription_not_digital(data: dict[str, Any], detectors_config: dict[str, Any]) -> bool:
    return not (data["is_digital"] and detectors_config["ignore_digital"])


def __update_page_and_data_with_stamp_information_for_pharm_pres(
    data: dict[str, Any],
    file_path: str,
    img: Image,
    is_debug_enabled: bool,
    page_dict: dict[str, Any],
    stamp_detector: Detector,
    monitoring: Monitoring,
) -> Image:
    predictions, angle = stamp_detector.count_stamps(file_path, data["pharm_stamps_required"], monitoring=monitoring)
    data["pharm_stamps_found"] += len(predictions)
    page_dict["stamps_found"] = len(predictions)
    if is_debug_enabled:
        img = draw_stamps(img, predictions, angle)
    return img


def __update_page_and_data_with_signature_information_for_pharm_pres(
    data: dict[str, Any],
    detectors_config: dict[str, Any],
    file_path: str,
    img: Image,
    is_debug_enabled: bool,
    page_dict: dict[str, Any],
    signature_detector_config: dict[str, Any],
    signature_detector: SignatureDetector,
    monitoring: Monitoring,
) -> None:
    if signature_detector_config["is_enabled"]:
        if page_dict["page"] == 1:
            if data["is_prototype"]:
                pharma_horizontal_crop_points = signature_detector_config["options"]["pharma_horizontal_crop_points_3"]
                page_dict["sign_required"] = 3
            else:
                pharma_horizontal_crop_points = signature_detector_config["options"]["pharma_horizontal_crop_points_2"]
                page_dict["sign_required"] = 2
        else:
            pharma_horizontal_crop_points = signature_detector_config["options"]["pharma_horizontal_crop_points_1"]
            page_dict["sign_required"] = 1
        pharm_signatures_boxes, signature_count = signature_detector.count_signatures(
            file=file_path,
            horizontal_crop_points=pharma_horizontal_crop_points,
            detectors_preprocessing_config=detectors_config["preprocessing"],
        )
        data["pharm_sign_found"] += signature_count
        page_dict["sign_found"] = signature_count
        if is_debug_enabled:
            draw_signature_areas(
                img,
                signature_detector_config["options"]["pharma_vertical_crop_point"],
                pharma_horizontal_crop_points,
            )
            draw_signatures(img, pharm_signatures_boxes, monitoring=monitoring)


def __update_page_and_data_with_coupon_information_for_pharm_pres(
    file_path: str,
    img: Image,
    is_debug_enabled: bool,
    scan_last_three_digits: str,
    missing_coupons_config: dict[str, Any],
    page_dict: dict[str, Any],
    idika_last_three_digits: str,
    monitoring: Monitoring,
) -> None:
    missing_coupons_config["is_enabled"] = True
    if missing_coupons_config["is_enabled"] and scan_last_three_digits == idika_last_three_digits:
        # coupons, _ = count_coupons(barcode_reader(file_path), monitoring=monitoring)
        coupons = barcode_reader(file_path)
        authenticity_tapes = get_authenticity_tapes(coupons)
        page_dict["coupons_found"] = authenticity_tapes
        if authenticity_tapes:
            page_dict["coupon_check"] = False
        if is_debug_enabled:
            draw_barcodes(img, coupons, monitoring=monitoring)


def __calculate_page_number(
    data: dict[str, Any], detectors_config: dict[str, Any], img: Image, monitoring: Monitoring
) -> int:
    return (
        2
        if (
            data["pages"] > 1
            and not remove_templates(
                color_converted=img,
                template_paths=detectors_config["pages"]["template_file_paths"],
                template_matching_threshold=0.5,
                monitoring=monitoring,
            )
        )
        else 1
    )


def __is_not_full_participation(data: dict[str, Any], detectors_config: dict[str, Any]) -> bool:
    return not (data.get("participation_bool") and detectors_config["ignore_full_participation"])


def __is_pharm_prescription(scan_last_three_digits: str) -> bool:
    return bool(int(scan_last_three_digits[0]))


def __calculate_scan_last_three_digits(file_path: str) -> str:
    return file_path.split("_")[-2][-3:]


def __get_file_found_page(
    data: dict[str, Any],
    file_path: str,
    scan_last_three_digits: str,
    pharm_pres: bool,
    prescription_id: str,
) -> dict[str, Any]:
    return {
        "prescription": prescription_id,
        "pharmacist_idika_prescription_full": data["pharmacist_idika_prescription_full"],
        "scan_last_three_digits": scan_last_three_digits,
        "file_path": file_path,
        "prescription_scanned_pages": Path(file_path).name,
        "type": "pharmacist" if pharm_pres else "doctor",
        "first_execution": data["first_execution"],
        "digital": data["is_digital"],
        "100%": data.get("participation_bool"),
        "stamps_found": 0,
        "sign_found": 0,
        "sign_required": 0 if pharm_pres else 1,
        "doc_name": data["doc_name"],
        "patient_name": data["patient_name"],
        "category": data["category"],
        "category_name": data["category_name"],
        "unit": data["unit"],
        "sign_check": True,
        "stamps_check": True,
        "coupon_check": True,
        "coupon_precheck": True,
        "coupons_found": "",
        "coupons_required": data.get("coupons") if pharm_pres else 0,
        "stamps_required": 1 if pharm_pres else data["doc_stamps_required"],
        "pdf_file_name": data["pdf_file_name"],
        "page": 1,
        "pages": data["pages"],
        "execution": data["execution"],
        "document_type": data["document_type"],
        "insurance_amount": data["insurance_amount"],
        "patient_amount": data["patient_amount"],
        "missing_tapes": "",
        "surplus_tapes": "string",
    }


def __get_file_not_found_page(data: dict[str, Any], prescription_id: str) -> dict[str, Any]:
    return {
        "prescription": prescription_id,
        "pharmacist_idika_prescription_full": data["pharmacist_idika_prescription_full"],
        "prescription_scanned_pages": "",
        "file_path": "",
        "page": 1,
        "pages": data["pages"],
        "scan_last_three_digits": None,
        "doc_name": data["doc_name"],
        "patient_name": data["patient_name"],
        "category": data["category"],
        "category_name": data["category_name"],
        "unit": data["unit"],
        "type": "pharmacist",
        "sign_check": True,
        "coupons_found": "",
        "coupons_required": 0,
        "first_execution": data["first_execution"],
        "digital": data["is_digital"],
        "100%": data.get("participation_bool"),
        "sign_found": None,
        "sign_required": None,
        "stamps_found": None,
        "stamps_required": None,
        "coupon_check": None,
        "coupon_precheck": None,
        "stamps_check": True,
        "pdf_file_name": data["pdf_file_name"],
        "execution": data["execution"],
        "document_type": data["document_type"],
        "insurance_amount": data["insurance_amount"],
        "patient_amount": data["patient_amount"],
        "missing_tapes": "",
        "surplus_tapes": "string",
    }


def __set_prescription_requirements(data: dict[str, Any]) -> None:
    data["pharm_sign_required"] = __get_pharm_signs_required(data)
    data["doc_stamps_required"] = __get_doc_stamps_required(data)
    data["doc_sign_required"] = __get_doc_signs_required(data)


def __log_counter(counter: int, prescription_id: str, idika_last_three_digits: str, monitoring: Monitoring) -> None:
    monitoring.logger_adapter.info(f"{counter} : {prescription_id}{idika_last_three_digits}")


def __initialise_prescription_values(data: dict[str, Any]) -> None:
    data["pharm_sign_found"] = 0
    data["doc_sign_found"] = 0
    data["pharm_stamps_found"] = 0
    data["doc_stamps_found"] = 0


def __get_pharm_signs_required(data: dict[str, Any]) -> int:
    return 2 + int(data["is_prototype"] + (data["pages"] - 1))


def __get_doc_signs_required(data: dict[str, Any]) -> int:
    return 0 if data["is_digital"] else 1


def __get_doc_stamps_required(data: dict[str, Any]) -> int:
    if data["is_digital"]:
        return 0
    else:
        return 2 if "νοσοκομ" in data["unit"].lower() else 1


def __get_prescription_files(prescription_id: str, scan_dir: Path) -> list[str]:
    # TODO: support png as well
    return glob.glob(str(scan_dir / f"*{prescription_id}*.jpg"))


def __get_missing_coupons_ids(pages_dict_list: list[dict[str, Any]]) -> list[str]:
    # Convert input list of dictionaries to a pandas DataFrame
    pages_df = pd.DataFrame.from_dict(pages_dict_list)

    # Define aggregation functions
    agg_funcs = {"coupons_found": "sum", "coupons_required": "first"}

    # Group the DataFrame by 'prescription' and 'scan_last_three_digits'
    # columns, and apply aggregation functions, and reset the index
    g_df = (
        pages_df[pages_df["type"] == "pharmacist"]
        .groupby(["prescription", "scan_last_three_digits"], as_index=False)
        .agg(agg_funcs)
    )

    # Filter the groups where 'coupons_found' is less than 'coupons_required',
    # extract unique 'prescription' values, and convert to a list
    missing_coupons_ps_ids: list[str] = (
        g_df[g_df["coupons_found"] < g_df["coupons_required"]]["prescription"].unique().tolist()
    )

    # Return the list of missing 'prescription' values
    return missing_coupons_ps_ids


def __update_pages_dict_list_with_missing_coupons(
    missing_coupons_config: dict[str, Any],
    missing_coupons_ps_ids: list[str],
    pages_dict_list: list[dict[str, Any]],
    monitoring: Monitoring,
) -> None:
    for page in pages_dict_list:
        if page["type"] == "pharmacist" and page["prescription"] in missing_coupons_ps_ids:
            page["coupon_precheck"] = False
            if missing_coupons_config["options"]["template_matching"]:
                try:
                    img = cv2.cvtColor(cv2.imread(page["file_path"]), cv2.COLOR_RGB2BGR)
                    page["coupon_check"] = not match_missing_coupons(
                        config=missing_coupons_config, image=img, monitoring=monitoring
                    )
                except Exception as e:
                    monitoring.logger_adapter.exception(e)
                    page["coupon_check"] = False
            else:
                page["coupon_check"] = False


def __is_prescription_unknown(prescription_id: str) -> bool:
    unknown_prescription_id = str(0).zfill(16)
    return unknown_prescription_id in prescription_id
