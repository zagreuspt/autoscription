import logging
from datetime import datetime
from logging import LoggerAdapter
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import NonRecordingSpan, SpanContext, set_span_in_context

from src.autoscription.core.config import get_project_root, get_results_dir

if TYPE_CHECKING:
    _LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    _LoggerAdapter = logging.LoggerAdapter

STOP_TOKEN = "stop queue"


def get_software_version() -> str:
    version = "undefined"  # get version
    version_txt_path = get_project_root() / "version.txt"
    if version_txt_path.exists():
        with open(get_project_root() / "version.txt", "r") as version_file:
            version = version_file.read()
    return version


class Monitoring:
    is_enabled: bool
    connection_string: str
    run_context: SpanContext
    logger_adapter: _LoggerAdapter
    logger: logging.Logger = logging.getLogger("")  # TODO: dont use default Logger, Pass logger as constructor argument

    def __init__(self, monitoring_config: Dict[str, Any]) -> None:
        self.is_enabled = monitoring_config["is_enabled"]
        self.connection_string = monitoring_config["connection_string"]
        version = get_software_version()
        self.logger_adapter: _LoggerAdapter = LoggerAdapter(logger=self.logger, extra={"version": version})

    def set_logger_adapter_extra(self, extra: Dict[str, str]) -> None:
        merged_extra = {}
        if self.logger_adapter.extra:
            merged_extra = dict(self.logger_adapter.extra)
        merged_extra.update(extra)
        self.logger_adapter: _LoggerAdapter = LoggerAdapter(logger=self.logger, extra=merged_extra)

    def config_azure_monitor(self, logger: logging.Logger) -> None:
        if self.is_enabled:
            configure_azure_monitor(
                connection_string=self.connection_string,
                logger_name=logger.name,
                logging_level=logging.WARNING,
                resource=Resource.create(
                    {
                        ResourceAttributes.SERVICE_NAME: "autoscription",
                    }
                ),
            )
            logger.handlers[-1].setLevel(logging.WARNING)  # TODO: Remove on first chance
            active_loggers: List[str] = [str(k) for k in logging.Logger.manager.loggerDict.keys()]
            for l_name in active_loggers:
                if "azure" or "opentelemetry" in l_name:
                    logging.getLogger(l_name).setLevel(logging.WARNING)

    def restart(self, monitoring_config: Dict[str, Any]) -> None:
        self.is_enabled = monitoring_config["is_enabled"]
        self.connection_string = monitoring_config["connection_string"]
        version = get_software_version()
        self.logger_adapter: _LoggerAdapter = LoggerAdapter(logger=self.logger, extra={"version": version})

        self.config_azure_monitor(logger=logging.getLogger(""))

    def get_parent_context(self) -> Optional[Context]:
        if self.run_context:
            # Parent Span Context
            parent_context = SpanContext(
                trace_id=self.run_context.trace_id,
                span_id=self.run_context.span_id,
                is_remote=True,
                trace_flags=self.run_context.trace_flags,
            )
            return set_span_in_context(NonRecordingSpan(parent_context))
        return None

    def info(self, msg: Any, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        self.logger_adapter.info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        self.logger_adapter.warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        self.logger_adapter.error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        self.logger_adapter.critical(msg, *args, **kwargs)

    def exception(self, msg: Any, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        self.logger_adapter.exception(msg, *args, **kwargs)


class TestMonitoring(Monitoring):
    def __init__(self) -> None:
        super().__init__(monitoring_config={"is_enabled": False, "connection_string": ""})

    def config_azure_monitor(self, logger: logging.Logger) -> None:  # noqa: [U100]
        pass

    def get_parent_context(self) -> None:  # noqa: [U100]
        pass


def setup_logging(monitoring: Monitoring, scan_date: datetime) -> None:
    logger = monitoring.logger
    handlers_for_removal = [h for h in logger.handlers if h.name == "console_handler" or h.name == "file_handler"]
    for h in handlers_for_removal:
        logger.handlers.remove(h)
    logger.addHandler(create_console_handler())
    results_dir = get_results_dir(scan_date)
    results_dir.mkdir(parents=True, exist_ok=True)
    # scan_datetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    # log_file: Path = results_dir / f"application_{scan_datetime}.log"
    # log_file: Path = get_log_file_path(datetime.now())
    # logger.addHandler(create_file_handler(log_file))
    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("fontTools.subset").setLevel(logging.WARNING)


def log_queue(queue: Any) -> None:
    logger = logging.getLogger()
    while queue.empty() is False:
        # consume a log message, block until one arrives
        message = queue.get()
        # log the message
        logger.handle(message)


def logger_process(queue: Any, log_file: Path) -> None:
    logger_name: str = ""  # TODO: pass as argument
    # create a logger
    logger = logging.getLogger(logger_name)
    # configure a stream handler
    log_file
    # logger.addHandler(create_file_handler(log_file))
    logger.addHandler(logging.StreamHandler())
    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
    # log all messages, debug and up
    # run forever
    while True:
        # consume a log message, block until one arrives
        message = queue.get()
        # check for shutdown
        if message is STOP_TOKEN:
            break
        # log the message
        logger.handle(message)


def create_console_handler() -> Any:
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.name = "console_handler"
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    return console


def create_file_handler(log_file: Path) -> logging.FileHandler:
    # Change this line to include the encoding argument
    file_handler: logging.FileHandler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.name = "file_handler"
    # Create a formatter that includes the timestamp.
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Set the formatter for the file handler.
    file_handler.setFormatter(formatter)
    return file_handler
