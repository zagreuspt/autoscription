import asyncio
import datetime
from pathlib import Path

from core.logging import TestMonitoring
from pytest_mock import MockerFixture

from src.autoscription.backend.core import Backend


class TestBackendSendRequest:
    def test_backend_send_request(self, mocker: MockerFixture) -> None:
        mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
        backend: Backend = Backend(
            monitoring=TestMonitoring(),
            configuration={
                "file_uploader": {
                    "client_id": "test",
                    "client_secret": "test",  # expires on June 30th 2025
                    "tenant_id": "test",
                    "account_url": "https://test.net",
                    "data_container": "customer-data",
                },
                "summary_report_url": "https://test.net",
                "token": "test",
                "send_report_url": "test",
            },
        )
        loop = asyncio.new_event_loop()
        loop.run_until_complete(backend.send_report(username="test", path=Path(), dt=datetime.date.today()))
        loop.close()
