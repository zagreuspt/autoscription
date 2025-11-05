from unittest.mock import MagicMock

import pytest

from src.autoscription.core.errors import (
    IdikaWrongStatusCodeException,
    XmlParsingException,
)
from src.autoscription.core.retriever import ClinicalDocumentRetriever


class TestClinicalDocumentRetriever:
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

    def test_retrieve_clinical_document_success(self, document_retriever, mock_api_client):
        """Test successful retrieval of a clinical document."""
        # Arrange
        test_prescription_id = "123"
        expected_document = MagicMock()
        mock_api_client.get_clinical_document.return_value = expected_document

        # Act
        result = document_retriever.retrieve_clinical_document(test_prescription_id)

        # Assert
        mock_api_client.get_clinical_document.assert_called_once_with(test_prescription_id)
        assert result == expected_document

    def test_retrieve_clinical_document_with_xml_parsing_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of XmlParsingException."""
        # Arrange
        test_prescription_id = "123"
        mock_api_client.get_clinical_document.side_effect = XmlParsingException("Parsing error")

        # Act & Assert
        with pytest.raises(XmlParsingException):
            document_retriever.retrieve_clinical_document(test_prescription_id)

        mock_monitoring.logger_adapter.exception.assert_called()
        mock_monitoring.logger_adapter.error.assert_called_with(f"Failed to parse prescription {test_prescription_id}")

    def test_retrieve_clinical_document_with_wrong_status_code_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of IdikaWrongStatusCodeException."""
        # Arrange
        test_prescription_id = "456"
        mock_api_client.get_clinical_document.side_effect = IdikaWrongStatusCodeException(
            "Wrong status code", expected_status=200, actual_status=400, arguments={"test": "test"}, response="<>"
        )

        # Act & Assert
        with pytest.raises(IdikaWrongStatusCodeException):
            document_retriever.retrieve_clinical_document(test_prescription_id)

        mock_monitoring.logger_adapter.exception.assert_called()

    def test_retrieve_clinical_document_with_generic_exception(
        self, document_retriever, mock_api_client, mock_monitoring
    ):
        """Test handling of generic Exception."""
        # Arrange
        test_prescription_id = "789"
        mock_api_client.get_clinical_document.side_effect = Exception("Generic error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            document_retriever.retrieve_clinical_document(test_prescription_id)

        assert "Generic error" in str(exc_info.value)
        mock_monitoring.logger_adapter.exception.assert_called()
        mock_monitoring.logger_adapter.error.assert_called_with(
            f"Failed to retrieve or parse prescription {test_prescription_id}"
        )

    def test_retrieve_clinical_documents_success(self, document_retriever, mock_api_client):
        """Test successful retrieval of multiple clinical documents."""
        # Arrange
        prescription_ids = ["123", "456"]
        documents = [MagicMock(), MagicMock()]
        mock_api_client.get_clinical_document.side_effect = documents

        # Act
        results = document_retriever.retrieve_clinical_documents(prescription_ids)

        # Assert
        assert results == documents
        assert mock_api_client.get_clinical_document.call_count == len(prescription_ids)

    def test_retrieve_clinical_documents_partial_success(self, document_retriever, mock_api_client):
        """Test partial success in retrieving multiple clinical documents."""
        # Arrange
        prescription_ids = ["123", "999"]  # Assuming 999 fails
        documents = [MagicMock(), XmlParsingException("Parsing error")]
        mock_api_client.get_clinical_document.side_effect = documents

        # Act
        results = document_retriever.retrieve_clinical_documents(prescription_ids)

        # Assert
        assert results == [documents[0]]
        assert mock_api_client.get_clinical_document.call_count == 3  # 2 calls for 999, 1 call for 123

    def test_retrieve_clinical_documents_all_fail(self, document_retriever, mock_api_client, mock_monitoring):
        """Test failure to retrieve any clinical documents."""
        # Arrange
        prescription_ids = ["999", "998"]  # Assuming both failed
        mock_api_client.get_clinical_document.side_effect = XmlParsingException("Parsing error")

        # Act
        results = document_retriever.retrieve_clinical_documents(prescription_ids)

        # Assert
        assert len(results) == 0
        assert mock_api_client.get_clinical_document.call_count == 4  # 2 calls for 999, 2 calls for 998
