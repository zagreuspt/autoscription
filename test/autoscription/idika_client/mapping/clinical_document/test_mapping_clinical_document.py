from test.autoscription.idika_client.mapping.clinical_document.fixtures import *

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.clinical_document_mt import (
    map_clinical_document,
)

# TODO: add test for throwing MappingIdikaResponseException


class TestMappingClinicalDocument:
    def test_map_clinical_document(self, clinical_document):
        result = map_clinical_document(clinical_document)
        assert result.barcode == clinical_document.id.extension
        assert result.effective_time.since == "10"
        assert result.effective_time.until == "20"
        assert result.author.assigned_author.doctor_specialty_id == "specialty_id"
        assert result.author.assigned_author.doctor_specialty_name == "specialty_name"
        assert result.custodian is None
        assert result.doctor_visit is None
        assert result.patient_role is None
        assert result.legal_authenticator is None
        assert result.section.barcode is None
        assert result.section.text is None
        assert result.section.summary.contains_high_cost_drug is False
        assert result.section.summary.contains_desensitization_vaccine is True
        assert result.section.summary.medical_report_required is False
        assert len(result.section.substance_administrations) == 1

    def test_map_clinical_document_invalid_id_root(self, clinical_document):
        clinical_document.id.root = "1212121"
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_clinical_document(clinical_document)

    def test_map_clinical_document_missing_required_attribute(self, clinical_document):
        clinical_document.id = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_clinical_document(clinical_document)
