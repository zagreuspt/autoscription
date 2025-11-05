from unittest.mock import MagicMock

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.partial_clinical_document import (
    map_execution_details,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Act,
    EntryRelationship,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Id1 as Id,
)


class TestMapExecutionDetails:
    def test_should_return_execution_details_when_required_id_is_present(self):
        mock_entry_relationship = EntryRelationship(act=Act(id=[Id(root="2.10.11", extension="5000")]))
        execution_details = map_execution_details(mock_entry_relationship)
        assert execution_details.retail_price == 5000.0

    def test_should_raise_exception_when_required_id_is_not_present(self):
        mock_entry_relationship = EntryRelationship(act=Act(id=[Id(root="2.10.12", extension="5000")]))
        execution_details = map_execution_details(mock_entry_relationship)
        assert execution_details.retail_price is None

    def test_should_raise_exception_when_no_ids_are_present(self):
        mock_entry_relationship = EntryRelationship(act=Act(id=[]))
        execution_details = map_execution_details(mock_entry_relationship)
        assert execution_details.retail_price is None

    def test_should_raise_exception_when_act_is_none(self):
        mock_entry_relationship = EntryRelationship(act=None)
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_execution_details(mock_entry_relationship)
