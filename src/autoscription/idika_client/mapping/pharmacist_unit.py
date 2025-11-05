from datetime import datetime
from typing import List

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.model.idika.pharmacist_units import (
    Item,
    PharmacistUnitsResponse,
)
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit


def map_pharmacist_unit(item: Item) -> PharmacistUnit:
    if item and item.pharmacy and item.pharmacy.id and item.pharmacy.name and item.pharmacy.tax_registry_no:
        # TODO: throws format error
        expiry_date = datetime.strptime(item.expiry_date, "%Y-%m-%d %H:%M:%S") if item.expiry_date else datetime.max
        start_date = datetime.strptime(item.start_date, "%Y-%m-%d %H:%M:%S") if item.start_date else datetime.min
        return PharmacistUnit(
            pharmacy_id=item.pharmacy.id,
            pharmacy_name=item.pharmacy.name,
            expiry_date=expiry_date,
            start_date=start_date,
            tax_registry_number=item.pharmacy.tax_registry_no,
        )
    else:
        raise MappingIdikaResponseMissingRequiredValueException()


def map_pharmacist_units(pharmacist_units_response: PharmacistUnitsResponse) -> List[PharmacistUnit]:
    if (
        pharmacist_units_response
        and pharmacist_units_response.contents
        and len(pharmacist_units_response.contents.items) > 0
    ):
        return [map_pharmacist_unit(i) for i in pharmacist_units_response.contents.items]
    else:
        raise MappingIdikaResponseMissingRequiredValueException()
