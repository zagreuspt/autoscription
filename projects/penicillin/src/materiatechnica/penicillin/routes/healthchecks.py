from typing import Any

from flask import Blueprint, jsonify

health = Blueprint("health_check", __name__)


@health.route("/healthcheck", methods=["GET"])
def health_check() -> Any:
    return jsonify({"status": "ok"})
