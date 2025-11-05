from unittest.mock import MagicMock

import pytest

from src.autoscription.core.errors import (
    IdikaWrongStatusCodeException,
    XmlParsingException,
)
from src.autoscription.core.retriever import ClinicalDocumentRetriever


class TestClinicalDocumentRetrieverPartial:
    @pytest.fixture
    def mock_api_client(self):
        """Fixture to mock IdikaAPIClient."""
        return MagicMock()

    @pytest.fixture
    def mock_monitoring(self):
        """Fixture to mock Monitoring."""
        mock = MagicMock()
        mock.logger_adapter = MagicMock()
        return mock

    @pytest.fixture
    def document_retriever(self, mock_api_client, mock_monitoring):
        return ClinicalDocumentRetriever(idika_api_client=mock_api_client, monitoring=mock_monitoring)

    def test_retrieve_partial_clinical_document_success(self, document_retriever, mock_api_client):
        """Test successful retrieval of a clinical document."""
        # Arrange
        prescription = "456"
        execution = 2
        expected_document = MagicMock()
        mock_api_client.get_partial_clinical_document.return_value = expected_document

        # Act
        result = document_retriever.retrieve_partial_clinical_document(prescription, execution)

        # Assert
        mock_api_client.get_partial_clinical_document.assert_called_once_with(prescription, execution)
        assert result == expected_document

    def test_retrieve_partial_clinical_document_with_xml_parsing_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of XmlParsingException."""
        # Arrange
        prescription = "123"
        execution = 1
        mock_api_client.get_partial_clinical_document.side_effect = XmlParsingException("Parsing error")

        # Act & Assert
        with pytest.raises(XmlParsingException):
            document_retriever.retrieve_partial_clinical_document(prescription, execution)

        mock_monitoring.logger_adapter.exception.assert_called()
        mock_monitoring.logger_adapter.error.assert_called_with(
            f"Failed to parse partial prescription {prescription} with execution {execution}"
        )

    def test_retrieve_partial_clinical_document_with_wrong_status_code_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of IdikaWrongStatusCodeException."""
        # Arrange
        prescription = "456"
        execution = 2
        mock_api_client.get_partial_clinical_document.side_effect = IdikaWrongStatusCodeException(
            "Wrong status code", expected_status=200, actual_status=400, arguments={"test": "test"}, response="<>"
        )

        # Act & Assert
        with pytest.raises(IdikaWrongStatusCodeException):
            document_retriever.retrieve_partial_clinical_document(prescription, execution)

        mock_monitoring.logger_adapter.exception.assert_called()

    def test_retrieve_partial_clinical_document_with_generic_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of generic Exception."""
        # Arrange
        prescription = "456"
        execution = 2
        mock_api_client.get_partial_clinical_document.side_effect = Exception("Generic error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            document_retriever.retrieve_partial_clinical_document(prescription, execution)

        assert "Generic error" in str(exc_info.value)
        mock_monitoring.logger_adapter.exception.assert_called()
        mock_monitoring.logger_adapter.error.assert_called_with(
            f"Failed to retrieve or parse partial prescription {prescription} with execution {execution}"
        )

    def test_retrieve_partial_clinical_documents_success(self, document_retriever, mock_api_client):
        """Test successful retrieval of multiple clinical documents."""
        # Arrange
        prescription_details = [{"prescription": "123", "execution": 1}, {"prescription": "456", "execution": 2}]
        documents = [MagicMock(), MagicMock()]
        mock_api_client.get_partial_clinical_document.side_effect = documents

        # Act
        results = document_retriever.retrieve_partial_clinical_documents(prescription_details)

        # Assert
        assert results == documents
        assert mock_api_client.get_partial_clinical_document.call_count == len(prescription_details)

    def test_retrieve_partial_clinical_documents_partial_success(self, document_retriever, mock_api_client):
        """Test partial success in retrieving multiple clinical documents."""
        # Arrange
        prescription_details = [
            {"prescription": "123", "execution": 1},
            {"prescription": "999", "execution": 2},
        ]  # Assuming 999 fails
        documents = [MagicMock(), XmlParsingException("Parsing error")]
        mock_api_client.get_partial_clinical_document.side_effect = documents

        # Act
        results = document_retriever.retrieve_partial_clinical_documents(prescription_details)

        # Assert
        assert results == [documents[0]]
        assert mock_api_client.get_partial_clinical_document.call_count == 3  # 2 calls for 999, 1 call for 123

    def test_retrieve_partial_clinical_documents_all_fail(self, document_retriever, mock_api_client, mock_monitoring):
        """Test failure to retrieve any clinical documents."""
        # Arrange
        prescription_details = [
            {"prescription": "999", "execution": 1},
            {"prescription": "998", "execution": 2},
        ]  # Assuming both failed
        mock_api_client.get_partial_clinical_document.side_effect = XmlParsingException("Parsing error")

        # Act
        results = document_retriever.retrieve_partial_clinical_documents(prescription_details)

        # Assert
        assert len(results) == 0
        assert mock_api_client.get_partial_clinical_document.call_count == 4  # 2 calls for 999, 2 calls for 998
