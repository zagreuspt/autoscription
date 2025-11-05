#!/usr/bin/python
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

import diskcache
import tkcalendar

import src.autoscription.core.config
from src.autoscription.core.logging import Monitoring
from src.autoscription.overrides.tkcalendar import _btns_date_range


def script_method(fn, _rcb=None):  # type: ignore[no-untyped-def]  # noqa: U101
    return fn


def script(obj, optimize=True, _frames_up=0, _rcb=None):  # type: ignore[no-untyped-def]  # noqa: U101, U100
    return obj


import torch.jit  # noqa: E402

torch.jit.script_method = script_method
torch.jit.script = script

tkcalendar.Calendar._btns_date_range = _btns_date_range

from multiprocessing import freeze_support  # noqa: E402

from ttkthemes.themed_tk import ThemedTk  # noqa: E402

from src.autoscription.gui.Application import Application  # noqa: E402
from src.autoscription.gui.TermsAndConditions import TermsAndConditionsUI  # noqa: E402

#  https://stackoverflow.com/questions/74186441/tkinter-multiprocessing-tkinter-keeps-opening-windows
freeze_support()


def cleanup_directories() -> None:
    dirs_to_remove = [
        Path(src.autoscription.core.config.get_project_root() / "executions" / "20240202"),
        Path(src.autoscription.core.config.get_project_root() / "executions" / "20240215"),
    ]

    for d in dirs_to_remove:
        if d.exists():
            shutil.rmtree(d)
    files_to_remove = [
        Path(
            src.autoscription.core.config.get_project_root()
            / "executions"
            / "reports"
            / "report_20240202-20240308_174042.pdf"
        ),
        Path(
            src.autoscription.core.config.get_project_root()
            / "executions"
            / "reports"
            / "report_20240215-20240312_140716.pdf"
        ),
    ]
    for f in files_to_remove:
        if f.exists():
            os.unlink(f)


class CustomThemedTk(ThemedTk):  # type: ignore[misc]
    monitoring: Monitoring

    def __init__(self, monitoring: Monitoring, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.monitoring = monitoring

    def report_callback_exception(self, exc, val, tb) -> None:  # type: ignore[no-untyped-def]
        super().report_callback_exception(exc, val, tb)
        self.monitoring.logger_adapter.error(f"Exception thrown in the ui {val}")
        self.monitoring.logger_adapter.exception(val)


def run() -> None:
    # Load the application configuration from a module called 'core.config'
    application_configuration: Dict[str, Any] = src.autoscription.core.config.config

    # Initialize a monitoring object using the monitoring configuration from 'application_configuration'
    monitoring: Monitoring = Monitoring(monitoring_config=application_configuration["monitoring"])

    # Configure Azure Monitor for logging
    monitoring.config_azure_monitor(logger=logging.getLogger(""))

    # Free up any unused GPU memory
    torch.cuda.empty_cache()

    # Disable gradient calculations for PyTorch (useful in inference mode to save memory and speed up computations)
    torch.set_grad_enabled(False)

    # Close the splash screen if the application is bundled with PyInstaller
    if hasattr(sys, "_MEIPASS"):
        import pyi_splash

        pyi_splash.close()

    try:
        # Initialize a disk-based cache with the directory "cache"
        cleanup_directories()

        cached_data = diskcache.Cache("cache")

        # Check if the terms and conditions have been accepted
        if cached_data.get("accept_terms") != True or application_configuration["terms_version"] != cached_data.get(
            "terms_version"
        ):
            # If not accepted, display a UI window for terms and conditions
            terms_root = CustomThemedTk(theme="breeze", monitoring=monitoring)
            TermsAndConditionsUI(
                master=terms_root, monitoring=monitoring, terms_version=application_configuration["terms_version"]
            )

        # If terms and conditions have been accepted
        # TODO: check for return value of termsAndConditionsUI window instead of a side effect
        if cached_data.get("accept_terms") == True:
            # Create the main application window
            root = CustomThemedTk(theme="breeze", monitoring=monitoring)
            app = Application(master=root, application_configuration=application_configuration, monitoring=monitoring)
            # Start the main event loop of the application
            app.mainloop()

    # If any exception occurs during the above process
    except Exception as e:
        # Log the exception using the monitoring system
        monitoring.logger_adapter.exception(e)
