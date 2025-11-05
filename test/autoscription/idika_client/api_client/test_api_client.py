from test.autoscription.idika_client.api_client.fixtures import *
from unittest.mock import MagicMock

import requests

from src.autoscription.core.errors import (
    IdikaAuthenticationException,
    IdikaPharmacyNotSelectedException,
    IdikaWrongStatusCodeException,
    MappingIdikaResponseMissingRequiredValueException,
    XmlParsingException,
)
from src.autoscription.idika_client.api_client import IdikaAPIClient


class TestIdikaAPIClient:
    def test_authenticate_success(self, authenticated_response):
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = None
        idika_http_client.authenticate.return_value = mock_response
        mock_response.text = authenticated_response
        mock_response.status_code = 200

        client = IdikaAPIClient(idika_http_client=idika_http_client)

        result = client.authenticate()

        assert result == 12345
        idika_http_client.authenticate.assert_called_once()

    def test_authenticate_failure(self):
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_response.status_code = 400
        idika_http_client.authenticate.return_value = mock_response

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        with pytest.raises(IdikaAuthenticationException):
            client.authenticate()

        idika_http_client.authenticate.assert_called_once()

    def test_get_clinical_document_request_failure(self):
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        idika_http_client.get_clinical_document.return_value = mock_response
        mock_response.text = "3333"

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = 1234

        with pytest.raises(IdikaWrongStatusCodeException):
            client.get_clinical_document("3333")

    def test_get_clinical_document_request_failure_pharmacy_id_is_none(self):
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        idika_http_client.get_clinical_document.return_value = mock_response
        idika_http_client.authenticate.return_value = mock_response

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = None

        with pytest.raises(IdikaPharmacyNotSelectedException):
            client.get_clinical_document("3333")

    def test_get_clinical_document_request_failure_token_expired_failed_reauthenticate(self):
        idika_http_client = MagicMock()
        mock_get_clinical_document_response = MagicMock()
        mock_authentication_response = MagicMock()
        mock_authentication_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get_clinical_document_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get_clinical_document_response.status_code = 403
        idika_http_client.get_clinical_document.return_value = mock_get_clinical_document_response
        idika_http_client.authenticate.return_value = mock_authentication_response

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = 1234

        with pytest.raises(IdikaAuthenticationException):
            client.get_clinical_document("3333")
        idika_http_client.authenticate.assert_called_once()
        idika_http_client.get_clinical_document.assert_called_once()

    def test_get_clinical_document_request_failure_token_expired_successful_reauthentication(
        self, authenticated_response
    ):  # + pharmacy_id is None + 403
        idika_http_client = MagicMock()
        mock_get_clinical_document_response = MagicMock()
        mock_authentication_response = MagicMock()
        mock_authentication_response.raise_for_status.side_effect = None
        mock_authentication_response.status_code = 200
        mock_authentication_response.text = authenticated_response
        mock_get_clinical_document_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get_clinical_document_response.status_code = 403
        idika_http_client.get_clinical_document.return_value = mock_get_clinical_document_response
        idika_http_client.authenticate.return_value = mock_authentication_response

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = 1234

        with pytest.raises(IdikaWrongStatusCodeException):
            client.get_clinical_document("3333")
        idika_http_client.authenticate.assert_called_once()
        assert idika_http_client.get_clinical_document.call_count == 2

    def test_get_clinical_document_wrong_data_failure(self):
        xml_response = """
        <a><b><c>example</c><d>Example</d></b></a>
        """
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = None
        idika_http_client.get_clinical_document.return_value = mock_response
        mock_response.text = xml_response
        mock_response.status_code = 200

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = 1234
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            client.get_clinical_document("3333")

    def test_get_clinical_document_contains_minimum_required_data(self, clinical_document_minimum_requirements):
        idika_http_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = None
        idika_http_client.get_clinical_document.return_value = mock_response
        mock_response.text = clinical_document_minimum_requirements
        mock_response.status_code = 200

        client = IdikaAPIClient(idika_http_client=idika_http_client)
        client.pharmacy_id = 1234
        result = client.get_clinical_document("3333")

        assert result.section.substance_administrations == []
        idika_http_client.authenticate.assert_not_called()
