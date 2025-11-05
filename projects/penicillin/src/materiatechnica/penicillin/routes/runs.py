import calendar
import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from azure.data.tables import TableServiceClient
from flask import Blueprint, jsonify, request
from flask.templating import render_template
from injector import inject
from materiatechnica.penicillin.auth import auth

runs = Blueprint("runs", __name__)


def create_query(username: str, run_from: str, run_to: str) -> str:
    return (
        f"PartitionKey eq '{username}' "
        f"and RowKey ge '{run_from}' "
        f"and RowKey le '{run_to}' "
        f"and run_status eq 'success'"
    )


def is_input_valid(input_json: Dict[str, str]) -> bool:
    run_date: str = input_json["run_date"]
    run_status: str = input_json["run_status"]
    try:
        datetime.strptime(run_date, "%Y%m%d")
    except Exception as e:
        logging.error("invalid input", e)
        return False

    return run_status in ["success", "failure"]


@runs.route("/run/status/report", methods=["POST"])
@auth.login_required  # type:ignore[misc]
@inject  # type:ignore[misc]
def report_run_status(azure_table_storage: TableServiceClient) -> Any:
    if is_input_valid(request.json):
        table_client = azure_table_storage.get_table_client("runs")
        # if else block for backwards compatibility
        if "total_amount" in request.json:
            total_amount = float(request.json["total_amount"])
        else:
            total_amount = 0.0
        if "total_insurance_amount" in request.json:
            total_insurance_amount = float(request.json["total_insurance_amount"])
        else:
            total_insurance_amount = 0.0
        if "total_patient_amount" in request.json:
            total_patient_amount = float(request.json["total_patient_amount"])
        else:
            total_patient_amount = 0.0
        if "total_eopyy_amount" in request.json:
            total_eopyy_amount = float(request.json["total_eopyy_amount"])
        else:
            total_eopyy_amount = 0.0
        if "total_other_funds_amount" in request.json:
            total_other_funds_amount = float(request.json["total_other_funds_amount"])
        else:
            total_other_funds_amount = 0.0
        entity = {
            "PartitionKey": request.json["username"],  # TODO: trim input
            "RowKey": request.json["run_date"],  # TODO: trim input
            "run_status": request.json["run_status"],  # TODO: trim input
            "total_prescriptions": request.json["total_prescriptions"],
            "total_scanned_documents": request.json["total_scanned_documents"],
            "total_amount": total_amount,
            "total_insurance_amount": total_insurance_amount,
            "total_patient_amount": total_patient_amount,
            "total_eopyy_amount": total_eopyy_amount,
            "total_other_funds_amount": total_other_funds_amount,
        }
        table_client.upsert_entity(entity)
        return jsonify({"status": "ok"})
    else:
        response = jsonify({"status": "not ok", "message": "invalid input"})
        response.status = 409
        return response


def generate_html_result(result: List[str]) -> str:
    return f"<html>{result}</html>"


def convert_to_html_results(result_list: List[str], current_date: date) -> str:
    greek_month_names = [
        "Ιανουάριος",
        "Φεβρουάριος",
        "Μάρτιος",
        "Απρίλιος",
        "Μάιος",
        "Ιούνιος",
        "Ιούλιος",
        "Αύγουστος",
        "Σεπτέμβριος",
        "Οκτώβριος",
        "Νοέμβριος",
        "Δεκέμβριος",
    ]

    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
    start_day = date(current_date.year, current_date.month, 1).weekday()
    software_run_days = [int(day[-2:]) for day in result_list]
    return render_template(
        "email_calendar.html",
        softwareRunDays=software_run_days,
        greekMonthNames=greek_month_names,
        daysInMonth=days_in_month,
        startDay=start_day,
        year=current_date.year,
        month=current_date.month,
        today=current_date.day,
    )


def to_date(date_string: str) -> str:
    datetime.strptime(date_string, "%Y%m")
    return date_string


@runs.route("/run/status", methods=["GET"])
@auth.login_required  # type:ignore[misc]
@inject  # type:ignore[misc]
def retrieve_run_statuses(azure_table_storage: TableServiceClient) -> Any:
    username: Optional[str] = request.args.get("username", type=str)
    if username is None:
        response = jsonify({"status": "not ok", "message": "invalid input"})
        response.status = 409
        return response
    year_month: str = request.args.get("year_month", type=to_date, default=date.today().strftime("%Y%m"))
    run_from: str = year_month + "01"
    run_to: str = year_month + "31"
    table_client = azure_table_storage.get_table_client("runs")
    result = [
        v["RowKey"]
        for v in list(table_client.query_entities(create_query(username=username, run_from=run_from, run_to=run_to)))
    ]  # TODO: map table rows to run data domain objects
    return convert_to_html_results(result, date.today())
