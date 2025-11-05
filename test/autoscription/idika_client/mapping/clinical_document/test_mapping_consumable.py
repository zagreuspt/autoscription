from test.autoscription.idika_client.mapping.clinical_document.fixtures import *

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.clinical_document_mt import map_consumable


class TestMappingConsumable:
    def test_map_consumable(self, manufactured_material):
        references = {"ref_id": "barcode_value"}
        result = map_consumable(manufactured_material, references)
        assert result.barcode == "barcode_value"
        assert result.name == "material_name"
        assert result.form_code.code == "form_code"
        assert result.ingredient.code == "121"
        assert result.ingredient.name == "ingredient_name"

    def test_map_consumable_ref_not_found(self, manufactured_material):
        manufactured_material.code.original_text.reference.value = "#ref_id_2"
        references = {"ref_id": "barcode_value"}
        result = map_consumable(manufactured_material, references)
        assert result.barcode == "missing"
        assert result.form_code.code == "form_code"
        assert result.ingredient.code == "121"
        assert result.ingredient.name == "ingredient_name"

    def test_map_consumable_ref_attribute_missing(self, manufactured_material):
        manufactured_material.as_content = None
        references = {"ref_id": "barcode_value"}

        result = map_consumable(manufactured_material, references)
        assert result.barcode == "barcode_value"
        assert result.form_code.code == "form_code"
        assert result.ingredient.code == "121"
        assert result.ingredient.name == "ingredient_name"

    def test_map_consumable_manufactured_material_name_is_none(self, manufactured_material):
        manufactured_material.name = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_consumable(manufactured_material, {})

    def test_map_consumable_manufactured_material_form_code_is_none(self, manufactured_material):
        manufactured_material.form_code = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_consumable(manufactured_material, {})

    def test_map_consumable_manufactured_material_form_code_translation_is_none(self, manufactured_material):
        manufactured_material.form_code.translation = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_consumable(manufactured_material, {})

    def test_map_consumable_manufactured_material_form_code_translation_display_name_is_none(
        self, manufactured_material
    ):
        manufactured_material.form_code.translation.display_name = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_consumable(manufactured_material, {})
