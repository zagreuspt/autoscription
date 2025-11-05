import glob
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict

import requests

from src.autoscription.core.errors import (
    ApiDosagesFileNotFoundException,
    ApiPartialPrescriptionsSummariesFileNotFoundException,
)

sys.path.append("..")


def get_project_root() -> Path:
    return Path(os.getcwd())


def get_temp_scan_dir() -> Path:
    return get_project_root() / "executions" / ".temp" / "scans"


def get_scan_dir(scan_date: date) -> Path:
    return get_project_root() / "executions" / scan_date.strftime("%Y%m%d") / "scans"


def get_download_dir(scan_date: date) -> Path:
    return get_project_root() / "executions" / scan_date.strftime("%Y%m%d") / "idika"


def get_results_dir(scan_date: date) -> Path:
    return get_project_root() / "executions" / scan_date.strftime("%Y%m%d") / "results"


def get_past_partial_exec_dir(scan_date: date) -> Path:
    return get_project_root() / "executions" / scan_date.strftime("%Y%m%d") / "past_partial_exec"


def get_report_dir() -> Path:
    return get_project_root() / "executions" / "reports"


def get_dosages_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return f'dosages_{scan_date.strftime("%Y%m%d")}-{runtime_datetime.strftime("%Y%m%d_%H%M%S")}.csv'


def get_api_partial_prescriptions_summaries_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return (
        f'api_partial_prescriptions_summaries_{scan_date.strftime("%Y%m%d")}'
        f'-{runtime_datetime.strftime("%Y%m%d_%H%M%S")}.csv'
    )


def get_api_full_prescriptions_summaries_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return (
        f'api_full_prescriptions_summaries_{scan_date.strftime("%Y%m%d")}'
        f'-{runtime_datetime.strftime("%Y%m%d_%H%M%S")}.csv'
    )


def get_api_dosages_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return f"api_{get_dosages_file_name(scan_date, runtime_datetime)}"


def get_pages_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return f'pages_{scan_date.strftime("%Y%m%d")}-{runtime_datetime.strftime("%Y%m%d_%H%M%S")}.csv'


def get_config_file_name(scan_date: date, runtime_datetime: datetime) -> str:
    return f'config_{scan_date.strftime("%Y%m%d")}-{runtime_datetime.strftime("%Y%m%d_%H%M%S")}.json'


def get_report_templates_path() -> Path:
    return get_project_root() / "resources" / "report" / "templates"


def get_weights_dir() -> Path:
    return get_project_root() / "resources" / "weights"


def get_log_file_path(scan_date: datetime) -> Path:
    return get_results_dir(scan_date) / f'application_{scan_date.strftime("%Y-%m-%d_%H%M%S")}.log'


def get_newest_dosages_path(run_date: date) -> str:
    formatted_date = run_date.strftime("%Y%m%d")
    dosages_paths_pattern = (
        Path(config["download_directory"]) / formatted_date / "results" / f"dosages_{formatted_date}-*.csv"
    )
    newest_dosages_path = glob.glob(dosages_paths_pattern.as_posix()).pop()
    # TODO: throw custom exception instead of asserting
    assert Path(newest_dosages_path).exists(), "dosages file path not found"
    return newest_dosages_path


def get_newest_api_dosages_path(run_date: date) -> str:
    formatted_date = run_date.strftime("%Y%m%d")
    api_dosages_paths_pattern = (
        Path(config["download_directory"]) / formatted_date / "results" / f"api_dosages_{formatted_date}-*.csv"
    )
    newest_api_dosages_paths = glob.glob(api_dosages_paths_pattern.as_posix())
    if len(newest_api_dosages_paths) > 0:
        return newest_api_dosages_paths.pop()
    else:
        raise ApiDosagesFileNotFoundException()


def get_newest_api_partial_prescriptions_summaries_path(run_date: date) -> str:
    formatted_date = run_date.strftime("%Y%m%d")
    api_partial_prescriptions_summaries_paths_pattern = (
        Path(config["download_directory"])
        / formatted_date
        / "results"
        / f"api_partial_prescriptions_summaries_{formatted_date}-*.csv"
    )
    newest_api_partial_prescriptions_summaries_paths = glob.glob(
        api_partial_prescriptions_summaries_paths_pattern.as_posix()
    )
    if len(newest_api_partial_prescriptions_summaries_paths) > 0:
        return newest_api_partial_prescriptions_summaries_paths.pop()
    else:
        raise ApiPartialPrescriptionsSummariesFileNotFoundException()


def get_newest_api_full_prescriptions_summaries_path(run_date: date) -> str:
    formatted_date = run_date.strftime("%Y%m%d")
    api_full_prescriptions_summaries_paths_pattern = (
        Path(config["download_directory"])
        / formatted_date
        / "results"
        / f"api_full_prescriptions_summaries_{formatted_date}-*.csv"
    )
    newest_api_full_prescriptions_summaries_paths = glob.glob(api_full_prescriptions_summaries_paths_pattern.as_posix())
    if len(newest_api_full_prescriptions_summaries_paths) > 0:
        return newest_api_full_prescriptions_summaries_paths.pop()
    else:
        raise Exception("file not found")


def use_combined_certs() -> None:
    if sys.platform == "win32":
        combined_certs_path = Path(get_project_root() / "certs" / "combined_certs.pem")
        import certifi_win32

        certifi_win32.generate_pem()
        certifi_pem = certifi_win32.wincerts.where()
        requests_certs = requests.certs.where()  # type: ignore[attr-defined]
        with open(requests_certs, "rb") as requests_certs_file:
            requests_certs_content = requests_certs_file.read()
            with open(certifi_pem, "rb") as certifi_pem_file:
                certifi_pem_content = certifi_pem_file.read()
                combined_certs = certifi_pem_content + requests_certs_content
                combined_certs_path.parent.mkdir(parents=True, exist_ok=True)
                with open(combined_certs_path, "wb") as combined_certs_file:
                    combined_certs_file.write(combined_certs)
        os.environ["REQUESTS_CA_BUNDLE"] = combined_certs_path.as_posix()


def get_newest_pages_path(run_date: date) -> str:
    formatted_date = run_date.strftime("%Y%m%d")
    pages_paths_pattern = (
        Path(config["download_directory"]) / formatted_date / "results" / f"pages_{formatted_date}-*.csv"
    )
    newest_pages_path = glob.glob(pages_paths_pattern.as_posix()).pop()
    # TODO: throw custom exception instead of asserting
    assert Path(newest_pages_path).exists(), "pages file path not found"
    return newest_pages_path


# Note:
# use this config for local testing against wiremock, which can be found under projects/wiremock
# "whitelist_url": "http://localhost:8383/user_configuration"

config: Dict[str, Any] = {
    "terms_version": 2.0,
    "api": {"base_url": "https://eps.e-prescription.gr", "api_key": "a23e52a205b1562526f247847bfcf13e"},
    "backend": {
        "file_uploader": {
            "test_user": False,
            "client_id": "1f179234-06b4-4bcc-bab1-40dd04d6a67f",
            "tenant_id": "7d56198a-7d43-4d5d-8d6f-420187962fa2",
            "account_url": "https://stautoscriptionext002.blob.core.windows.net",
            "data_container": "customer-data",
        },
        "summary_report_url": "https://penicillin.azurewebsites.net/run/status/report",
        "token": "7cgU2MXoqpK0PDuCAmHMpROat",
        "send_report_url": "https://prod-104.westeurope.logic.azure.com:443/workflows/"
        + "12fa6f6b96e346a3a379090b2b1abaf0/triggers/manual/paths/invoke"
        + "?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0"
        + "&sig=LcAep_HmVunS_Daox2p_LaDqUtDE6HQ1B-uLUx6zmE4",
        "whitelist_url": "https://autoscription-whitelist.info4805.workers.dev/",
    },
    "monitoring": {
        "is_enabled": True,
        "connection_string": "InstrumentationKey=abd4a9ca-695d-4982-9378-6180576ed643;"
        + "IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;"
        + "LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/",
    },
    "reporting": {"execution_time_ordering": False, "show_overview": True, "category_breakdown": False},
    "turbo_mode": True,
    "dosages_only": False,
    "idika_integration": {
        "is_enabled": True,
        "guessing_pharmacy_id": {"is_enabled": False, "success_rate_threshold": 0.8},
    },
    "is_debug_enabled": False,
    "is_summary_enabled": True,
    "business_rules": {"fyk_limit": 3000.0},
    "detectors": {
        "ignore_digital": True,
        "ignore_full_participation": True,
        "preprocessing": {
            "is_enabled": True,
            "options": {
                "template_file_paths": [
                    str(get_project_root() / "resources" / f"bottom_right_tempate_{i}.jpg") for i in range(1, 32)
                ],
                "template_matching_threshold": 0.5,
                "color": (255, 0, 255),  # RGB values 0-255
                "right_margin": 400,
                "left_margin": 1600,
                "top_margin": 50,
                "bottom_margin": 0,
            },
        },
        "stamp": {
            "is_enabled": True,
            "options": {
                "template_file_paths": [
                    str(get_project_root() / "resources" / f"bottom_right_tempate_{i}.jpg") for i in range(1, 32)
                ],
                "template_matching_threshold": 0.5,  # 0.7 0-1
                "max_rotation_angle": 90,  # 0-180
                "horizontal_crop_point": 0.35,  # 0-1
                "vertical_crop_point": 0.85,  # 0-1
                "area_ratio_threshold": 0.008,  # 0-1 0.015
                "color": (255, 255, 255),  # RGB values 0-255
                "right_margin": 400,
                "left_margin": 1600,
                "top_margin": 50,
                "bottom_margin": 0,
                "black_pixel_percentage": 12,
                "binary_threshold_value": 220,
            },
        },
        "signature": {
            "weight_directory": str(get_weights_dir()),
            "is_enabled": True,
            "options": {
                "doc_vertical_crop_point": 0.85,  # 0-1
                "doc_horizontal_crop_points": [(0.55, 0.95)],
                "pharma_vertical_crop_point": 0.85,  # 0-1
                "pharma_horizontal_crop_points_1": [(0.33, 0.95)],
                "pharma_horizontal_crop_points_2": [(0.33, 0.55), (0.55, 0.95)],
                "pharma_horizontal_crop_points_3": [
                    (0.33, 0.45),
                    (0.45, 0.65),
                    (0.65, 0.95),
                ],
                "min_area": 2000,
                "doc_min_area": 8000,
                "min_right_area": 15000,
                # after the cropper the judger removes if the min_box_height
                # is less than the threshold.
                "min_box_height": 30,
                "preprocessing": {
                    "remove_line": True,
                    "cropper": {
                        "clean_y_axis": True,
                        # If set to True, it will keep only the
                        # largest area in the Y axis
                        # Forcibly increase the area of each box.
                        # It might help with box merging
                        "increase_box_margin": 0,
                        "min_region_size": 1000,
                    },
                    # Filters out final boxes under the specified threshold
                    "extract_signatures": {
                        "is_enabled": True,
                        "debug": False,
                        # If set to True, it will draw the boxes
                        # found by the cropper
                        "options": {
                            "primary_extractor_sensitivity": 3.6,
                            "secondary_extractor": True,
                            "secondary_extractor_sensitivity": 9,
                        },
                    },
                    "remove_texts": {
                        "is_enabled": True,
                        "options": {
                            "run_in_whole_doc": False,
                            "run_in_stamp_area": True,
                            "min_right_area": 8000,
                            # if the text removal works  then the
                            # min right area is
                        },
                    },
                },
            },
        },
        "missing_coupons": {
            "options": {
                "template_file_paths": [
                    str(get_project_root() / "resources" / f"emptyCoupon_template{i}.jpg") for i in range(1, 16)
                ],
                "template_matching_threshold": 0.5,
                "template_matching": False,
            },
            "is_enabled": True,
        },
        "pages": {
            "template_file_paths": [
                str(get_project_root() / "resources" / f"pharma_page_template_{i}.jpg") for i in range(1, 6)
            ]
        },
        "template_matching_threshold": 0.4,
    },
    "download_directory": str(get_project_root() / "executions"),
    "last_scan_dir": str("C:/ScanSnap/raw_scans/last_scan"),
    "fernet_key": b"EKmVZerFWcOepXunO8uWL8pYVrxULUyKqD7aBwK-wnY=",
}
