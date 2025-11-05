import datetime

import pytest

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.pharmacist_unit import map_pharmacist_unit
from src.autoscription.idika_client.model.idika.pharmacist_units import Item, Pharmacy
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit


class TestMapPharmacistUnitsItem:
    def test_valid_item(self):
        item = Item(pharmacy=Pharmacy(id=1, name="Pharmacy A", tax_registry_no="012343243"))

        result: PharmacistUnit = map_pharmacist_unit(item)

        assert result.pharmacy_id == 1
        assert result.pharmacy_name == "Pharmacy A"
        assert result.tax_registry_number == "012343243"
        assert result.start_date == datetime.datetime.min
        assert result.expiry_date == datetime.datetime.max

    def test_valid_item_with_start_and_expiry_dates(self):
        item = Item(
            pharmacy=Pharmacy(id=1, name="Pharmacy A", tax_registry_no="112343243"),
            expiry_date="2017-04-20 11:45:00",
            start_date="2015-04-20 11:45:00",
        )

        result: PharmacistUnit = map_pharmacist_unit(item)

        assert result.pharmacy_id == 1
        assert result.pharmacy_name == "Pharmacy A"
        assert result.tax_registry_number == "112343243"
        assert result.start_date == datetime.datetime(2015, 4, 20, 11, 45)
        assert result.expiry_date == datetime.datetime(2017, 4, 20, 11, 45)

    def test_invalid_item(self):
        item = Item()

        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_pharmacist_unit(item)

    def test_None_item(self):
        with pytest.raises(MappingIdikaResponseMissingRequiredValueException):
            map_pharmacist_unit(None)
