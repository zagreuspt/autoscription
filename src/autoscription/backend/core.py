from __future__ import annotations

import base64
import datetime
import json
import random
import string
from pathlib import Path
from typing import Any

import requests
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from pandas import DataFrame
from requests.adapters import HTTPAdapter, Retry

from src.autoscription.core.logging import Monitoring


class FileUploader:
    container_client: ContainerClient
    monitoring: Monitoring

    def __init__(
        self,
        configuration: dict[str, str],
        monitoring: Monitoring,
    ) -> None:
        credentials = ClientSecretCredential(
            configuration["tenant_id"], configuration["client_id"], configuration["client_secret"]
        )

        self.container_client = BlobServiceClient(
            account_url=configuration["account_url"], credential=credentials
        ).get_container_client(configuration["data_container"])
        self.monitoring = monitoring
        self.test_user = configuration["test_user"]

    def __generate_file_path(
        self,
        filename: str,
        suffix: str,
        scan_date: datetime.date,
        execution_timestamp: datetime.datetime,
        username: str,
    ) -> str:
        scan_date_formatted = scan_date.strftime("%Y-%m-%d")
        execution_timestamp_formatted = execution_timestamp.strftime("%Y%m%d_%H%M%S")
        if self.test_user:
            username = "test"
        return f"{filename}/username={username}/run_date={scan_date_formatted}/{execution_timestamp_formatted}.{suffix}"

    def upload_data(
        self,
        filename: str,
        data: DataFrame,
        scan_date: datetime.date,
        execution_timestamp: datetime.datetime,
        username: str,
        file_format: str,
    ) -> None:
        if file_format == "csv":
            content = str.encode(
                data.assign(execution_timestamp=execution_timestamp.strftime("%Y%m%d_%H%M%S")).to_csv(index=False)
            )
        elif file_format == "parquet":
            content = data.assign(execution_timestamp=execution_timestamp.strftime("%Y%m%d_%H%M%S")).to_parquet()
        else:
            raise ValueError("Unsupported file format")

        self.container_client.upload_blob(
            name=self.__generate_file_path(
                filename=filename,
                suffix=file_format,
                scan_date=scan_date,
                execution_timestamp=execution_timestamp,
                username=username,
            ),
            data=content,
            overwrite=True,
        )


def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


class Backend:
    file_uploader: FileUploader
    monitoring: Monitoring
    summary_report_url: str
    token: str
    send_report_url: str
    whitelist_url: str
    whitelist_session: requests.Session

    def __init__(self, configuration: dict[str, Any], monitoring: Monitoring) -> None:
        self.monitoring = monitoring
        self.summary_report_url = configuration["summary_report_url"]
        self.send_report_url = configuration["send_report_url"]
        self.whitelist_url = configuration["whitelist_url"]
        self.token = configuration["token"]
        self.file_uploader = FileUploader(
            configuration=configuration["file_uploader"],
            monitoring=self.monitoring,
        )
        self.whitelist_session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            backoff_jitter=1,
            status_forcelist=[429, 500, 502, 503, 504],
            # DEFAULT_ALLOWED_METHODS does not include POST
            allowed_methods=Retry.DEFAULT_ALLOWED_METHODS.union({"POST"}),
        )
        self.whitelist_session.mount(self.whitelist_url, HTTPAdapter(max_retries=retry, pool_connections=20))

    async def report_run_summary(
        self,
        run_status: str,
        scan_date: datetime.date,
        username_low_case: str,
        total_prescriptions: int,
        total_scanned_documents: int,
        total_amount: float,
        total_patient_amount: float,
        total_insurance_amount: float,
        total_eopyy_amount: float,
        total_other_funds_amount: float,
    ) -> None:
        payload = {
            "run_status": run_status,
            "run_date": scan_date.strftime("%Y%m%d"),
            "username": username_low_case,
            "total_prescriptions": total_prescriptions,
            "total_scanned_documents": total_scanned_documents,
            "total_amount": total_amount,
            "total_patient_amount": total_patient_amount,
            "total_insurance_amount": total_insurance_amount,
            "total_eopyy_amount": total_eopyy_amount,
            "total_other_funds_amount": total_other_funds_amount,
        }
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(self.summary_report_url, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            self.monitoring.logger_adapter.exception(e)

    def upload(
        self,
        filename: str,
        dataframe: DataFrame,
        scan_date: datetime.date,
        execution_timestamp: datetime.datetime,
        username: str,
        file_format: str,
    ) -> None:
        self.file_uploader.upload_data(
            filename=filename,
            data=dataframe,
            scan_date=scan_date,
            execution_timestamp=execution_timestamp,
            username=username,
            file_format=file_format,
        )

    # TODO: move logic inside penicillin so that we have only one contact point for backend
    async def send_report(self, path: Path, dt: datetime.date, username: str) -> None:
        self.monitoring.logger_adapter.info("entered send report method")
        try:
            with open(path, "rb") as file:
                self.monitoring.logger_adapter.info("file opened: %s", path.as_posix())
                encoded_string = base64.b64encode(file.read())
                json_value = {"data": encoded_string.decode(), "date": dt.strftime("%Y%m%d"), "username": username}
                r = requests.post(self.send_report_url, json=json_value, timeout=5 * 60)
                if r.status_code == 202:
                    self.monitoring.logger_adapter.info("report sent")
                else:
                    self.monitoring.logger_adapter.error(
                        "report failed to be send to: %s with status code: %d", self.send_report_url[:50], r.status_code
                    )
        except Exception as e:
            self.monitoring.logger_adapter.error("failed to send report")
            self.monitoring.logger_adapter.exception(e)

    def get_user_configuration(self, username: str) -> dict[str, int | bool]:
        check_string = generate_random_string(5)
        response = self.whitelist_session.post(
            self.whitelist_url,
            data=json.dumps({"username": username, "check_string": check_string}),
            timeout=10,
        ).json()
        return {
            "is_user_allowed": (bool(response["is_whitelisted"]) and response["check_string"] == check_string),
            "time_order": bool(response["time_order"]),
            "reporting_show_overview": bool(response["reporting_show_overview"]),
            "report_category_breakdown": bool(response["report_category_breakdown"]),
            "detectors_max_threads": int(response["detectors_max_threads"]),
            "use_selfsigned_certificates": bool(response["use_selfsigned_certificates"]),
            "should_guess_pharmacy_id": bool(response["should_guess_pharmacy_id"]),
        }
