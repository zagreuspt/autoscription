from typing import Any, Dict, List

from src.autoscription.core.errors import (
    IdikaWrongStatusCodeException,
    RetriedException,
    XmlParsingException,
)
from src.autoscription.core.logging import Monitoring
from src.autoscription.idika_client.api_client import IdikaAPIClient
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document import (
    PartialClinicalDocument,
)


class ClinicalDocumentRetriever:
    """
    A class for retrieving clinical documents using the Idika API client.

    This class provides methods to retrieve single or multiple clinical documents
    associated with given prescription IDs. It handles various exceptions that may
    occur during the retrieval and parsing of the clinical documents, and logs
    these exceptions using a monitoring system.
    """

    idika_api_client: IdikaAPIClient
    monitoring: Monitoring

    def __init__(self, idika_api_client: IdikaAPIClient, monitoring: Monitoring):
        self.idika_api_client = idika_api_client
        self.monitoring = monitoring

    def retrieve_clinical_document(self, prescription_id: str) -> ClinicalDocument:
        try:
            return self.idika_api_client.get_clinical_document(prescription_id)
        except XmlParsingException as e:
            self.monitoring.logger_adapter.exception(e)
            self.monitoring.logger_adapter.error(f"Failed to parse prescription {prescription_id}")
            raise e
        except IdikaWrongStatusCodeException as e:
            self.monitoring.logger_adapter.exception(e)
            raise e
        except Exception as e:
            self.monitoring.logger_adapter.exception(e)
            self.monitoring.logger_adapter.error(f"Failed to retrieve or parse prescription {prescription_id}")
            raise e

    def retrieve_clinical_documents(self, prescription_ids: List[str]) -> List[ClinicalDocument]:
        retrieved_documents = []
        failed_to_retrieve_documents = []
        for p in prescription_ids:
            try:
                retrieved_documents.append(self.retrieve_clinical_document(p))
            except Exception as e:
                self.monitoring.logger_adapter.exception(RetriedException(e))
                self.monitoring.logger_adapter.error(f"Failed to retrieve prescription {p}")
                failed_to_retrieve_documents.append(p)

        for f in failed_to_retrieve_documents:
            try:
                retrieved_documents.append(self.retrieve_clinical_document(f))
                failed_to_retrieve_documents.remove(f)
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.error(f"Failed to retrieve prescription {f}")

        if failed_to_retrieve_documents:
            self.monitoring.logger_adapter.exception(
                "Failed to retrieve the following prescriptions: " f"{failed_to_retrieve_documents}"
            )
            self.monitoring.logger_adapter.error(
                "Failed to retrieve the following prescriptions: " f"{failed_to_retrieve_documents}"
            )

        return retrieved_documents

    def retrieve_partial_clinical_document(self, prescription_id: str, execution: int) -> PartialClinicalDocument:
        try:
            return self.idika_api_client.get_partial_clinical_document(prescription_id, execution)
        except XmlParsingException as e:
            self.monitoring.logger_adapter.exception(e)
            self.monitoring.logger_adapter.error(
                f"Failed to parse partial prescription {prescription_id} with execution {execution}"
            )
            raise e
        except IdikaWrongStatusCodeException as e:
            self.monitoring.logger_adapter.exception(e)
            raise e
        except Exception as e:
            self.monitoring.logger_adapter.exception(e)
            self.monitoring.logger_adapter.error(
                f"Failed to retrieve or parse partial prescription {prescription_id} with execution {execution}"
            )
            raise e

    def retrieve_partial_clinical_documents(
        self, prescription_details: List[Dict[str, Any]]
    ) -> List[PartialClinicalDocument]:
        retrieved_partial_documents = []
        failed_to_retrieve_partial_documents = []
        for d in prescription_details:
            try:
                retrieved_partial_documents.append(
                    self.retrieve_partial_clinical_document(d["prescription"], int(d["execution"]))
                )
            except Exception as e:
                self.monitoring.logger_adapter.exception(RetriedException(e))
                self.monitoring.logger_adapter.error(f"Failed to retrieve partial prescription {d}")
                failed_to_retrieve_partial_documents.append(d)

        for fd in failed_to_retrieve_partial_documents:
            try:
                retrieved_partial_documents.append(
                    self.retrieve_partial_clinical_document(fd["prescription"], int(fd["execution"]))
                )
                failed_to_retrieve_partial_documents.remove(fd)
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.error(f"Failed to retrieve partial prescription {fd}")

        if failed_to_retrieve_partial_documents:
            self.monitoring.logger_adapter.exception(
                "Failed to retrieve the following partial prescriptions: " f"{failed_to_retrieve_partial_documents}"
            )
            self.monitoring.logger_adapter.error(
                "Failed to retrieve the following partial prescriptions: " f"{failed_to_retrieve_partial_documents}"
            )

        return retrieved_partial_documents
