from test.autoscription.idika_client.api_client.fixtures import *
from unittest.mock import MagicMock

import pytest

from src.autoscription.core.core import select_pharmacy_id
from src.autoscription.core.errors import IdikaAuthenticationException
from src.autoscription.core.logging import TestMonitoring
from src.autoscription.idika_client.api_client import IdikaAPIClient


class TestGuessPharmacyId:
    def test_guess_pharmacy_id_all_clinical_document_requests_fail(
        self, authenticated_response, pharmacist_units_response
    ):
        idika_http_client = MagicMock()
        idika_http_client.get_clinical_document.side_effect = lambda pharmacy_id, pres_id: MagicMock(status_code=404)

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        get_pharmacist_units_http_response = MagicMock()
        get_pharmacist_units_http_response.status_code = 200
        get_pharmacist_units_http_response.text = pharmacist_units_response
        get_pharmacist_units_http_response.raise_for_status.side_effect = None
        idika_http_client.get_pharmacist_units.return_value = get_pharmacist_units_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        result = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=["pres_id_1", "pres_id_2"],
            guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )
        assert 12345 == result

    def test_guess_pharmacy_id_authentication_exception_thrown(self, authenticated_response):
        idika_http_client = MagicMock()
        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 404
        idika_http_client.authenticate.return_value = authenticated_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        with pytest.raises(IdikaAuthenticationException):
            select_pharmacy_id(
                idika_api_client=idika_api_client,
                scanned_prescription_ids_sample=["pres_id_1", "pres_id_2"],
                guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
                monitoring=TestMonitoring(),
            )

    def test_guess_pharmacy_id_no_active_units(self, authenticated_response):
        idika_http_client = MagicMock()

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        idika_api_client.get_active_pharmacist_units = lambda: []
        result = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=["pres_id_1", "pres_id_2"],
            guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )
        assert 12345 == result

    def test_guess_pharmacy_id_no_prescriptions(self, authenticated_response, pharmacist_units_response):
        idika_http_client = MagicMock()
        idika_http_client.get_clinical_document.side_effect = lambda pharmacy_id, pres_id: MagicMock(status_code=404)

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        get_pharmacist_units_http_response = MagicMock()
        get_pharmacist_units_http_response.status_code = 200
        get_pharmacist_units_http_response.text = pharmacist_units_response
        get_pharmacist_units_http_response.raise_for_status.side_effect = None
        idika_http_client.get_pharmacist_units.return_value = get_pharmacist_units_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        assert 12345 == select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=[],
            guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )

    def test_guess_pharmacy_id_success_rate_below_0_8(self, authenticated_response, pharmacist_units_response):
        idika_http_client = MagicMock()
        clinical_document_responses = {
            11073: {
                "pres_id_1": MagicMock(status_code=200),
                "pres_id_2": MagicMock(status_code=200),
                "pres_id_3": MagicMock(status_code=200),
                "pres_id_4": MagicMock(status_code=200),
                "pres_id_5": MagicMock(status_code=200),
                "pres_id_6": MagicMock(status_code=404),
                "pres_id_7": MagicMock(status_code=404),
                "pres_id_8": MagicMock(status_code=404),
                "pres_id_9": MagicMock(status_code=404),
                "pres_id_10": MagicMock(status_code=404),
            },
            11074: {
                "pres_id_1": MagicMock(status_code=404),
                "pres_id_2": MagicMock(status_code=404),
                "pres_id_3": MagicMock(status_code=404),
                "pres_id_4": MagicMock(status_code=404),
                "pres_id_5": MagicMock(status_code=404),
                "pres_id_6": MagicMock(status_code=404),
                "pres_id_7": MagicMock(status_code=404),
                "pres_id_8": MagicMock(status_code=404),
                "pres_id_9": MagicMock(status_code=404),
                "pres_id_10": MagicMock(status_code=404),
            },
        }

        idika_http_client.get_clinical_document.side_effect = lambda pharmacy_id, pres_id: clinical_document_responses[
            pharmacy_id
        ][pres_id]

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        get_pharmacist_units_http_response = MagicMock()
        get_pharmacist_units_http_response.status_code = 200
        get_pharmacist_units_http_response.text = pharmacist_units_response
        get_pharmacist_units_http_response.raise_for_status.side_effect = None
        idika_http_client.get_pharmacist_units.return_value = get_pharmacist_units_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        result = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=[
                "pres_id_1",
                "pres_id_2",
                "pres_id_3",
                "pres_id_4",
                "pres_id_5",
                "pres_id_6",
                "pres_id_7",
                "pres_id_8",
                "pres_id_9",
                "pres_id_10",
            ],
            guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )
        assert 12345 == result

    def test_guess_pharmacy_id_success_rate_greater_than_0_8_guessing_enabled(
        self, authenticated_response, pharmacist_units_response
    ):
        idika_http_client = MagicMock()
        clinical_document_responses = {
            11073: {
                "pres_id_1": MagicMock(status_code=200),
                "pres_id_2": MagicMock(status_code=200),
                "pres_id_3": MagicMock(status_code=200),
                "pres_id_4": MagicMock(status_code=200),
                "pres_id_5": MagicMock(status_code=200),
                "pres_id_6": MagicMock(status_code=200),
                "pres_id_7": MagicMock(status_code=200),
                "pres_id_8": MagicMock(status_code=200),
                "pres_id_9": MagicMock(status_code=200),
                "pres_id_10": MagicMock(status_code=404),
            },
            11074: {
                "pres_id_1": MagicMock(status_code=404),
                "pres_id_2": MagicMock(status_code=404),
                "pres_id_3": MagicMock(status_code=404),
                "pres_id_4": MagicMock(status_code=404),
                "pres_id_5": MagicMock(status_code=404),
                "pres_id_6": MagicMock(status_code=404),
                "pres_id_7": MagicMock(status_code=404),
                "pres_id_8": MagicMock(status_code=404),
                "pres_id_9": MagicMock(status_code=404),
                "pres_id_10": MagicMock(status_code=404),
            },
        }

        idika_http_client.get_clinical_document.side_effect = lambda pharmacy_id, pres_id: clinical_document_responses[
            pharmacy_id
        ][pres_id]

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        get_pharmacist_units_http_response = MagicMock()
        get_pharmacist_units_http_response.status_code = 200
        get_pharmacist_units_http_response.text = pharmacist_units_response
        get_pharmacist_units_http_response.raise_for_status.side_effect = None
        idika_http_client.get_pharmacist_units.return_value = get_pharmacist_units_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        result = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=[
                "pres_id_1",
                "pres_id_2",
                "pres_id_3",
                "pres_id_4",
                "pres_id_5",
                "pres_id_6",
                "pres_id_7",
                "pres_id_8",
                "pres_id_9",
                "pres_id_10",
            ],
            guessing_pharmacy_id_config={"is_enabled": True, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )
        assert 11073 == result

    def test_guess_pharmacy_id_success_rate_greater_than_0_8_guessing_disabled(
        self, authenticated_response, pharmacist_units_response
    ):
        idika_http_client = MagicMock()
        clinical_document_responses = {
            11073: {
                "pres_id_1": MagicMock(status_code=200),
                "pres_id_2": MagicMock(status_code=200),
                "pres_id_3": MagicMock(status_code=200),
                "pres_id_4": MagicMock(status_code=200),
                "pres_id_5": MagicMock(status_code=200),
                "pres_id_6": MagicMock(status_code=200),
                "pres_id_7": MagicMock(status_code=200),
                "pres_id_8": MagicMock(status_code=200),
                "pres_id_9": MagicMock(status_code=200),
                "pres_id_10": MagicMock(status_code=404),
            },
            11074: {
                "pres_id_1": MagicMock(status_code=404),
                "pres_id_2": MagicMock(status_code=404),
                "pres_id_3": MagicMock(status_code=404),
                "pres_id_4": MagicMock(status_code=404),
                "pres_id_5": MagicMock(status_code=404),
                "pres_id_6": MagicMock(status_code=404),
                "pres_id_7": MagicMock(status_code=404),
                "pres_id_8": MagicMock(status_code=404),
                "pres_id_9": MagicMock(status_code=404),
                "pres_id_10": MagicMock(status_code=404),
            },
        }

        idika_http_client.get_clinical_document.side_effect = lambda pharmacy_id, pres_id: clinical_document_responses[
            pharmacy_id
        ][pres_id]

        authenticated_http_response = MagicMock()
        authenticated_http_response.raise_for_status.side_effect = None
        authenticated_http_response.status_code = 200
        authenticated_http_response.text = authenticated_response
        idika_http_client.authenticate.return_value = authenticated_http_response

        get_pharmacist_units_http_response = MagicMock()
        get_pharmacist_units_http_response.status_code = 200
        get_pharmacist_units_http_response.text = pharmacist_units_response
        get_pharmacist_units_http_response.raise_for_status.side_effect = None
        idika_http_client.get_pharmacist_units.return_value = get_pharmacist_units_http_response

        idika_api_client = IdikaAPIClient(idika_http_client=idika_http_client)
        result = select_pharmacy_id(
            idika_api_client=idika_api_client,
            scanned_prescription_ids_sample=[
                "pres_id_1",
                "pres_id_2",
                "pres_id_3",
                "pres_id_4",
                "pres_id_5",
                "pres_id_6",
                "pres_id_7",
                "pres_id_8",
                "pres_id_9",
                "pres_id_10",
            ],
            guessing_pharmacy_id_config={"is_enabled": False, "success_rate_threshold": 0.8},
            monitoring=TestMonitoring(),
        )
        assert 12345 == result
