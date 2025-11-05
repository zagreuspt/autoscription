import datetime
from pathlib import Path
from typing import List

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

from src.autoscription.idika_client.mapping.pharmacist_unit import map_pharmacist_units
from src.autoscription.idika_client.model.idika.pharmacist_units import (
    PharmacistUnitsResponse,
)
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit


def test_mapper_against_sample():
    xml_string = Path("test/autoscription/idika_client/pharmacist_units_sample.xml").read_text("UTF-8")
    config = ParserConfig(fail_on_unknown_properties=False, fail_on_converter_warnings=True)
    parser = XmlParser(config=config)
    pharmacist_units_response = parser.from_string(xml_string, PharmacistUnitsResponse)
    pharmacist_units: List[PharmacistUnit] = map_pharmacist_units(pharmacist_units_response)

    assert len(pharmacist_units) == 2
    assert pharmacist_units[0].pharmacy_id == 11073
    assert pharmacist_units[0].pharmacy_name == "ONOMA FARMAKEIOU 1"
    assert pharmacist_units[0].start_date == datetime.datetime(2015, 4, 20, 11, 45)
    assert pharmacist_units[0].expiry_date == datetime.datetime.max
    assert pharmacist_units[1].pharmacy_id == 11074
    assert pharmacist_units[1].pharmacy_name == "ONOMA FARMAKEIOU 2"
    assert pharmacist_units[1].start_date == datetime.datetime(2015, 4, 20, 11, 45)
    assert pharmacist_units[1].expiry_date == datetime.datetime(2017, 4, 20, 0, 0)
