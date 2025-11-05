from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDateTime


@dataclass
class CompanyType:
    class Meta:
        name = "companyType"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Country:
    class Meta:
        name = "country"

    id: Optional[int] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name_in_english: Optional[str] = field(
        default=None,
        metadata={
            "name": "nameInEnglish",
            "type": "Element",
            "required": True,
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class TaxOffice:
    class Meta:
        name = "taxOffice"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    code: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class UnitType:
    class Meta:
        name = "unitType"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class County:
    class Meta:
        name = "county"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    country: Optional[Country] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class HealthCareUnit:
    class Meta:
        name = "healthCareUnit"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    unit_type: Optional[UnitType] = field(
        default=None,
        metadata={
            "name": "unitType",
            "type": "Element",
            "required": True,
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    address: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    telephone: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class City:
    class Meta:
        name = "city"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    county: Optional[County] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PharmacistUnion:
    class Meta:
        name = "pharmacistUnion"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    address: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    postal_code: Optional[int] = field(
        default=None,
        metadata={
            "name": "postalCode",
            "type": "Element",
            "required": True,
        },
    )
    city: Optional[City] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    telephone: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fax: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    email: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Pharmacy:
    class Meta:
        name = "pharmacy"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pharmacy_type_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "pharmacyTypeID",
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    company_type: Optional[CompanyType] = field(
        default=None,
        metadata={
            "name": "companyType",
            "type": "Element",
            "required": True,
        },
    )
    tax_office: Optional[TaxOffice] = field(
        default=None,
        metadata={
            "name": "taxOffice",
            "type": "Element",
            "required": True,
        },
    )
    tax_registry_no: Optional[str] = field(
        default=None,
        metadata={
            "name": "taxRegistryNo",
            "type": "Element",
            "required": True,
        },
    )
    pharmacist_union: Optional[PharmacistUnion] = field(
        default=None,
        metadata={
            "name": "pharmacistUnion",
            "type": "Element",
            "required": True,
        },
    )
    pharmacist_union_reg_no: Optional[str] = field(
        default=None,
        metadata={
            "name": "pharmacistUnionRegNo",
            "type": "Element",
            "required": True,
        },
    )
    licence_no: Optional[str] = field(
        default=None,
        metadata={
            "name": "licenceNo",
            "type": "Element",
            "required": True,
        },
    )
    bank: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    iban: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    address: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    postal_code: Optional[int] = field(
        default=None,
        metadata={
            "name": "postalCode",
            "type": "Element",
            "required": True,
        },
    )
    city: Optional[City] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    telephone: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    adsl: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    is_ika: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isIka",
            "type": "Element",
            "required": True,
        },
    )
    is_hospital: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isHospital",
            "type": "Element",
            "required": True,
        },
    )
    pharmacy_identification: Optional[int] = field(
        default=None,
        metadata={
            "name": "pharmacyIdentification",
            "type": "Element",
            "required": True,
        },
    )
    pharmacy_type: Optional[object] = field(
        default=None,
        metadata={
            "name": "pharmacyType",
            "type": "Element",
        },
    )


@dataclass
class Item:
    class Meta:
        name = "item"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    health_care_unit: Optional[HealthCareUnit] = field(
        default=None,
        metadata={
            "name": "healthCareUnit",
            "type": "Element",
            "required": True,
        },
    )
    start_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "startDate",
            "type": "Element",
            "required": True,
        },
    )
    expiry_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "expiryDate",
            "type": "Element",
            "required": True,
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    can_prescribe_med: Optional[bool] = field(
        default=None,
        metadata={
            "name": "canPrescribeMed",
            "type": "Element",
            "required": True,
        },
    )
    can_prescribe_exam: Optional[bool] = field(
        default=None,
        metadata={
            "name": "canPrescribeExam",
            "type": "Element",
            "required": True,
        },
    )
    can_execute_exam: Optional[bool] = field(
        default=None,
        metadata={
            "name": "canExecuteExam",
            "type": "Element",
            "required": True,
        },
    )
    pharmacy: Optional[Pharmacy] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Contents:
    class Meta:
        name = "contents"

    items: List[Item] = field(
        default_factory=list,
        metadata={
            "name": "item",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class PharmacistUnitsResponse:
    class Meta:
        name = "List"

    timestamp: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    contents: Optional[Contents] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    count: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
