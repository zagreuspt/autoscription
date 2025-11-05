from unittest.mock import MagicMock

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.partial_clinical_document import (
    map_product_supply,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Act,
    Entry,
    EntryRelationship,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Id1 as Id,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import Supply


class TestMapProductSupply:
    def test_should_return_product_supply_when_all_required_values_are_present(self):
        mock_entry = Entry(
            supply=Supply(entry_relationship=[EntryRelationship(act=Act(id=[Id(root="2.10.11", extension="5000")]))])
        )
        product_supply = map_product_supply(mock_entry)
        assert product_supply.execution_details is not None

    def test_should_raise_exception_when_required_values_are_not_present(self):
        mock_entry_relationship = MagicMock()
        mock_entry_relationship.act = None
        mock_entry = Entry(supply=Supply(entry_relationship=[mock_entry_relationship]))
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_product_supply(mock_entry)

    def test_should_raise_exception_when_no_entry_relationships_are_present(self):
        mock_entry = Entry(supply=Supply(entry_relationship=[]))
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_product_supply(mock_entry)

    def test_should_raise_exception_when_supply_is_none(self):
        mock_entry = Entry(supply=None)
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_product_supply(mock_entry)
