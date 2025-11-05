from test.autoscription.idika_client.mapping.clinical_document.fixtures import *

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.clinical_document_mt import (
    map_substance_administration,
)


class TestMappingSubstanceAdministration:
    def test_map_substance_administration(self, substance_administration):
        references = {"ref_id": "barcode_value"}
        result = map_substance_administration(substance_administration, references)
        assert result.barcode == "barcode_value"
        assert result.status_code == "status"
        assert result.dose_quantity.low_value == "1"
        assert result.rate_quantity.value == "1"
        assert result.consumable.name == "material_name"
        assert result.consumable.form_code.code == "form_code"
        assert result.consumable.ingredient.code == "121"
        assert result.prescribed_dose.value == "5"
        assert result.prescribed_dose.unit == "4"
        assert result.consumable.container_packaged_medicine.name == "test_name"
        assert result.consumable.container_packaged_medicine.package_code == "1234"
        assert result.consumable.container_packaged_medicine.package_display_name == "BTX200"

    def test_map_substance_administration_invalid_id(self, substance_administration):
        substance_administration.id.root = "123123"
        references = {"ref_id": "barcode_value"}
        result = map_substance_administration(substance_administration, references)
        assert result.barcode == "missing"
        assert result.status_code == "status"
        assert result.dose_quantity.low_value == "1"
        assert result.rate_quantity.value == "1"
        assert result.consumable.name == "material_name"
        assert result.consumable.form_code.code == "form_code"
        assert result.consumable.ingredient.code == "121"
        assert result.prescribed_dose.value == "5"
        assert result.prescribed_dose.unit == "4"

    def test_map_substance_administration_missing_id_attribute(self, substance_administration):
        substance_administration.id = None
        references = {"ref_id": "barcode_value"}
        result = map_substance_administration(substance_administration, references)
        assert result.barcode == "missing"
        assert result.status_code == "status"
        assert result.dose_quantity.low_value == "1"
        assert result.rate_quantity.value == "1"
        assert result.consumable.name == "material_name"
        assert result.consumable.form_code.code == "form_code"
        assert result.consumable.ingredient.code == "121"
        assert result.prescribed_dose.value == "5"
        assert result.prescribed_dose.unit == "4"

    def test_map_substance_administration_entry_relationship_is_empty(self, substance_administration):
        substance_administration.entry_relationship = []
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_substance_administration(substance_administration, {})

    def test_map_substance_administration_entry_relationship_is_none(self, substance_administration):
        substance_administration.entry_relationship = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_substance_administration(substance_administration, {})

    def test_map_substance_administration_consumable_is_none(self, substance_administration):
        substance_administration.consumable = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_substance_administration(substance_administration, {})

    def test_map_substance_administration_consumable_manufactured_product_is_none(self, substance_administration):
        substance_administration.consumable.manufactured_product = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_substance_administration(substance_administration, {})

    def test_map_substance_administration_consumable_manufactured_product_manufactured_material_is_none(
        self, substance_administration
    ):
        substance_administration.consumable.manufactured_product.manufactured_material = None
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_substance_administration(substance_administration, {})
