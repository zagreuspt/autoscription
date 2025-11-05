import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.pharmacist_unit import map_pharmacist_units
from src.autoscription.idika_client.model.idika.pharmacist_units import (
    Contents,
    Item,
    PharmacistUnitsResponse,
    Pharmacy,
)
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit


class TestMapPharmacistUnitsItem:
    def test_valid_response(self):
        response = PharmacistUnitsResponse(
            contents=Contents(
                items=[
                    Item(pharmacy=Pharmacy(id=1, name="Pharmacy A", tax_registry_no="12312")),
                    Item(pharmacy=Pharmacy(id=2, name="Pharmacy B", tax_registry_no="23231")),
                ]
            )
        )

        result = map_pharmacist_units(response)

        # Assert that the result is a list of PharmacistUnit instances
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(unit, PharmacistUnit) for unit in result)
        assert result[0].pharmacy_id == 1
        assert result[0].pharmacy_name == "Pharmacy A"
        assert result[1].pharmacy_id == 2
        assert result[1].pharmacy_name == "Pharmacy B"

    def test_empty_response(self):
        # Create a mock PharmacistUnitsResponse with no items
        response = PharmacistUnitsResponse(contents=Contents(items=[]))

        # Ensure that function returns an empty list
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_pharmacist_units(response)

    def test_exception_thrown_on_map_unit(self):
        # Create a mock PharmacistUnitsResponse with an invalid item
        response = PharmacistUnitsResponse(contents=Contents(items=[None]))

        # Ensure that the function raises the appropriate exception
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_pharmacist_units(response)

    def test_exception_thrown_when_required_values_are_missing(self):
        # Create a mock PharmacistUnitsResponse with an invalid item
        response = PharmacistUnitsResponse(contents=None)

        # Ensure that the function raises the appropriate exception
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_pharmacist_units(response)
