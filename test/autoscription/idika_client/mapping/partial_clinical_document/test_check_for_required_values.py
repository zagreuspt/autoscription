import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.partial_clinical_document import (
    check_for_required_values,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Component,
    Entry,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Id1 as Id,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    PartialClinicalDocument as IdikaPartialClinicalDocument,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Section,
    StructuredBody,
)


class TestCheckForRequiredValues:
    def test_should_not_raise_exception_when_all_required_values_are_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=Section(entry=[Entry()])))),
        )
        check_for_required_values(idika_partial_clinical_document)

    def test_should_raise_exception_when_id_root_is_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root=None, extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=Section()))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            check_for_required_values(idika_partial_clinical_document)

    def test_should_raise_exception_when_id_extension_is_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension=None),
            component=Component(structured_body=StructuredBody(component=Component(section=Section()))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            check_for_required_values(idika_partial_clinical_document)

    def test_should_raise_exception_when_component_is_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"), component=None
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            check_for_required_values(idika_partial_clinical_document)

    def test_should_raise_exception_when_structured_body_is_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"), component=Component(structured_body=None)
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            check_for_required_values(idika_partial_clinical_document)

    def test_should_raise_exception_when_section_is_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=None))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            check_for_required_values(idika_partial_clinical_document)
