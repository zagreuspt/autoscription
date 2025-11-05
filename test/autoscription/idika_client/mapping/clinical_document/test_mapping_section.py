from test.autoscription.idika_client.mapping.clinical_document.fixtures import *

from src.autoscription.idika_client.mapping.clinical_document_mt import map_section


class TestMappingSection:
    def test_map_section(self, section):
        result = map_section(section)
        assert result.barcode is None
        assert result.text is None
        assert result.summary.contains_high_cost_drug is False
        assert result.summary.contains_desensitization_vaccine is True
        assert len(result.substance_administrations) == 1
        assert result.substance_administrations[0].barcode is not None
        assert result.substance_administrations[0].status_code is not None

    def test_map_section_missing_attribute(self, section):
        section.text = None
        result = map_section(section)
        assert result.barcode is None
        assert result.text is None
        assert result.summary.contains_high_cost_drug is False
        assert result.summary.contains_desensitization_vaccine is True
        assert len(result.substance_administrations) == 1

    def test_map_section_missing_entry_attribute(self, section):
        section.entry = None
        with pytest.raises(TypeError):
            map_section(section)

    def test_map_section_missing_section_entry_second_item(self, section):
        section.entry = [section.entry[0]]
        result = map_section(section)
        assert result.barcode is None
        assert result.text is None
        assert result.summary.contains_high_cost_drug is False
        assert result.summary.contains_desensitization_vaccine is True
        assert len(result.substance_administrations) == 0

    def test_map_section_missing_section_entry_second_item_is_none(self, section):
        section.entry[1] = None
        result = map_section(section)
        assert result.barcode is None
        assert result.text is None
        assert result.summary.contains_high_cost_drug is False
        assert result.summary.contains_desensitization_vaccine is True
        assert len(result.substance_administrations) == 0
