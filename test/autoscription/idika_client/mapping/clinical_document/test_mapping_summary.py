import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
    MappingIdikaResponseUnexpectedValueException,
)
from src.autoscription.idika_client.mapping.clinical_document_mt import map_summary
from src.autoscription.idika_client.model.idika import Act, Entry, Id


class TestMappingSummary:
    def test_map_summary_with_valid_entry(self):
        valid_entry = Entry(
            act=Act(
                id=[Id(root="1.1.7", extension="0"), Id(root="1.1.8", extension="1"), Id(root="1.1.23", extension="1")]
            )
        )
        summary = map_summary(valid_entry)
        assert summary.contains_high_cost_drug is False
        assert summary.contains_desensitization_vaccine is True
        assert summary.medical_report_required is True

    def test_map_summary_missing_required_ids(self):
        invalid_entry_missing_ids = Entry(act=Act(id=[Id(root="1.1.8", extension="1")]))
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_summary(invalid_entry_missing_ids)

    def test_map_summary_with_unexpected_value(self):
        invalid_entry_unexpected_value = Entry(
            act=Act(
                id=[Id(root="1.1.8", extension="2"), Id(root="1.1.7", extension="0"), Id(root="1.1.23", extension="1")]
            )
        )
        with pytest.raises(MappingIdikaResponseUnexpectedValueException):
            map_summary(invalid_entry_unexpected_value)

    def test_map_summary_missing_act(self):
        entry_without_act = Entry(act=None)
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_summary(entry_without_act)
