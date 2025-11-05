import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.partial_clinical_document import (
    map_partial_clinical_document,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Act,
    Component,
    Entry,
    EntryRelationship,
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
    Supply,
)


class TestMapPartialClinicalDocument:
    def test_should_return_partial_clinical_document_when_all_required_values_are_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"),
            component=Component(
                structured_body=StructuredBody(
                    component=Component(
                        section=Section(
                            entry=[
                                Entry(),
                                Entry(
                                    supply=Supply(
                                        entry_relationship=[
                                            EntryRelationship(act=Act(id=[Id(root="2.10.11", extension="5000")]))
                                        ]
                                    )
                                ),
                            ]
                        )
                    )
                )
            ),
        )
        result = map_partial_clinical_document(idika_partial_clinical_document, 1)
        assert result.barcode == "123"
        assert result.execution == 1
        assert result.summary is None
        assert len(result.product_supplies) == 1

    def test_should_raise_exception_when_required_values_are_not_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root=None, extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=Section(entry=[Entry()])))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_partial_clinical_document(idika_partial_clinical_document, 1)

    def test_should_raise_exception_when_no_entries_are_present(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=Section(entry=[])))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_partial_clinical_document(idika_partial_clinical_document, 1)

    def test_should_raise_exception_when_section_is_none(self):
        idika_partial_clinical_document = IdikaPartialClinicalDocument(
            id=Id(root="1.21", extension="123"),
            component=Component(structured_body=StructuredBody(component=Component(section=None))),
        )
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_partial_clinical_document(idika_partial_clinical_document, 1)
