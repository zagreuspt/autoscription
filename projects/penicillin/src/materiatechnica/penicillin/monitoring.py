import logging
from typing import Any

from azure.monitor.opentelemetry import configure_azure_monitor
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes


def setup_monitoring(app: Flask) -> None:
    FlaskInstrumentor().instrument_app(app, excluded_urls="/healthcheck")
    default_logger = logging.getLogger("")
    connection_string = app.config["APPLICATIONINSIGHTS_CONNECTION_STRING"]

    configure_azure_monitor(
        connection_string=connection_string,
        logger_name=default_logger.name,
        logging_level=logging.WARNING,
        resource=Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: "penicillin",
            }
        ),
    )
    default_logger.addHandler(create_console_handler())


def create_console_handler() -> Any:
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.name = "console_handler"
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    return console
