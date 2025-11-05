from dataclasses import dataclass, field
from typing import List, Optional, Union  # noqa: UNT001
from xml.etree.ElementTree import QName


@dataclass
class CapTypeCode:
    class Meta:
        name = "capTypeCode"
        namespace = "urn:epsos-org:ep:medication"

    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class CapacityQuantity:
    class Meta:
        name = "capacityQuantity"
        namespace = "urn:epsos-org:ep:medication"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Code2:
    class Meta:
        name = "code"
        namespace = "urn:epsos-org:ep:medication"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Denominator:
    class Meta:
        name = "denominator"
        namespace = "urn:epsos-org:ep:medication"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: Optional[QName] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": "http://www.w3.org/2001/XMLSchema-instance",
            "required": True,
        },
    )


@dataclass
class Numerator:
    class Meta:
        name = "numerator"
        namespace = "urn:epsos-org:ep:medication"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: Optional[QName] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": "http://www.w3.org/2001/XMLSchema-instance",
            "required": True,
        },
    )


@dataclass
class Translation:
    class Meta:
        name = "translation"
        namespace = "urn:epsos-org:ep:medication"

    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class State:
    class Meta:
        name = "state"
        namespace = "urn:hl7-org:v3"

    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Addr:
    class Meta:
        name = "addr"
        namespace = "urn:hl7-org:v3"

    street_address_line: Optional[str] = field(
        default=None,
        metadata={
            "name": "streetAddressLine",
            "type": "Element",
        },
    )
    city: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    postal_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "postalCode",
            "type": "Element",
        },
    )
    state: Optional[Union[State, str]] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    country: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class AdministrativeGenderCode:
    class Meta:
        name = "administrativeGenderCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class BirthTime:
    class Meta:
        name = "birthTime"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class ConfidentialityCode:
    class Meta:
        name = "confidentialityCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class EthnicGroupCode:
    class Meta:
        name = "ethnicGroupCode"
        namespace = "urn:hl7-org:v3"

    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
            "required": True,
        },
    )


# Follows ISCO to define the occupation of the author more on the codes in the following link
# https://ilostat.ilo.org/resources/concepts-and-definitions/classification-occupation/
@dataclass
class FunctionCode:
    class Meta:
        name = "functionCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class High:
    class Meta:
        name = "high"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class Id:
    class Meta:
        name = "id"
        namespace = "urn:hl7-org:v3"

    extension: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    root: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class IndependentInd:
    class Meta:
        name = "independentInd"
        namespace = "urn:hl7-org:v3"

    value: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Item:
    class Meta:
        name = "item"
        namespace = "urn:hl7-org:v3"

    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Attribute",
            "required": True,
        },
    )
    value: Optional[str] = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class LanguageCode:
    class Meta:
        name = "languageCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Low:
    class Meta:
        name = "low"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class Name:
    class Meta:
        name = "name"
        namespace = "urn:hl7-org:v3"

    given: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    family: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class Period:
    class Meta:
        name = "period"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Quantity1:
    class Meta:
        name = "quantity"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    unit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class RaceCode:
    class Meta:
        name = "raceCode"
        namespace = "urn:hl7-org:v3"

    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class RealmCode:
    class Meta:
        name = "realmCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Reference:
    class Meta:
        name = "reference"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class SignatureCode:
    class Meta:
        name = "signatureCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class StatusCode:
    class Meta:
        name = "statusCode"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class StructuredBody:
    class Meta:
        name = "structuredBody"
        namespace = "urn:hl7-org:v3"

    component: Optional["Component"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Telecom:
    class Meta:
        name = "telecom"
        namespace = "urn:hl7-org:v3"

    use: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class TemplateId:
    class Meta:
        name = "templateId"
        namespace = "urn:hl7-org:v3"

    root: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Time:
    class Meta:
        name = "time"
        namespace = "urn:hl7-org:v3"

    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class TypeId:
    class Meta:
        name = "typeId"
        namespace = "urn:hl7-org:v3"

    extension: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    root: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Value:
    class Meta:
        name = "value"
        namespace = "urn:hl7-org:v3"

    type_value: Optional[QName] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": "http://www.w3.org/2001/XMLSchema-instance",
            "required": True,
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class FormCode:
    class Meta:
        name = "formCode"
        namespace = "urn:epsos-org:ep:medication"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
            "required": True,
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
            "required": True,
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
            "required": True,
        },
    )
    translation: Optional[Translation] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Quantity2:
    class Meta:
        name = "quantity"
        namespace = "urn:epsos-org:ep:medication"

    numerator: Optional[Numerator] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    denominator: Optional[Denominator] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class AssignedPerson:
    class Meta:
        name = "assignedPerson"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    determiner_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "determinerCode",
            "type": "Attribute",
            "required": True,
        },
    )
    name: Optional[Name] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class DoseQuantity:
    class Meta:
        name = "doseQuantity"
        namespace = "urn:hl7-org:v3"

    low: Optional[Low] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    high: Optional[High] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class EffectiveTime:
    class Meta:
        name = "effectiveTime"
        namespace = "urn:hl7-org:v3"

    type_value: Optional[QName] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": "http://www.w3.org/2001/XMLSchema-instance",
        },
    )
    operator: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    period: Optional[Period] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    low: Optional[Low] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    high: Optional[High] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class LanguageCommunication:
    class Meta:
        name = "languageCommunication"
        namespace = "urn:hl7-org:v3"

    template_id: Optional[TemplateId] = field(
        default=None,
        metadata={
            "name": "templateId",
            "type": "Element",
            "required": True,
        },
    )
    language_code: Optional[LanguageCode] = field(
        default=None,
        metadata={
            "name": "languageCode",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class ListType:
    class Meta:
        name = "list"
        namespace = "urn:hl7-org:v3"

    item: List[Item] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class OriginalText:
    class Meta:
        name = "originalText"
        namespace = "urn:hl7-org:v3"

    reference: Optional[Reference] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class RateQuantity:
    class Meta:
        name = "rateQuantity"
        namespace = "urn:hl7-org:v3"

    low: Optional[Low] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    high: Optional[High] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class RepresentedCustodianOrganization:
    class Meta:
        name = "representedCustodianOrganization"
        namespace = "urn:hl7-org:v3"

    id: Optional[Id] = field(
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
    telecom: Optional[Telecom] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    addr: Optional[Addr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class RepresentedOrganization:
    class Meta:
        name = "representedOrganization"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    determiner_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "determinerCode",
            "type": "Attribute",
        },
    )
    id: Optional[Id] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[Name] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    telecom: Optional[Telecom] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    addr: Optional[Addr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Supply:
    class Meta:
        name = "supply"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    mood_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "moodCode",
            "type": "Attribute",
            "required": True,
        },
    )
    independent_ind: Optional[IndependentInd] = field(
        default=None,
        metadata={
            "name": "independentInd",
            "type": "Element",
            "required": True,
        },
    )
    quantity: Optional[Quantity1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class ContainerPackagedMedicine:
    class Meta:
        name = "containerPackagedMedicine"
        namespace = "urn:epsos-org:ep:medication"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    determiner_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "determinerCode",
            "type": "Attribute",
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
    form_code: Optional[FormCode] = field(
        default=None,
        metadata={
            "name": "formCode",
            "type": "Element",
            "required": True,
        },
    )
    capacity_quantity: Optional[CapacityQuantity] = field(
        default=None,
        metadata={
            "name": "capacityQuantity",
            "type": "Element",
            "required": True,
        },
    )
    cap_type_code: Optional[CapTypeCode] = field(
        default=None,
        metadata={
            "name": "capTypeCode",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Ingredient:
    class Meta:
        name = "ingredient"
        namespace = "urn:epsos-org:ep:medication"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    determiner_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "determinerCode",
            "type": "Attribute",
        },
    )
    code: Optional[Code2] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    quantity: Optional[Quantity2] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    ingredient: Optional["Ingredient"] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class AssignedAuthor:
    class Meta:
        name = "assignedAuthor"
        namespace = "urn:hl7-org:v3"

    id: List[Id] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    telecom: List[Telecom] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    assigned_person: Optional[AssignedPerson] = field(
        default=None,
        metadata={
            "name": "assignedPerson",
            "type": "Element",
            "required": True,
        },
    )
    represented_organization: Optional[RepresentedOrganization] = field(
        default=None,
        metadata={
            "name": "representedOrganization",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class AssignedCustodian:
    class Meta:
        name = "assignedCustodian"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    represented_custodian_organization: Optional[RepresentedCustodianOrganization] = field(
        default=None,
        metadata={
            "name": "representedCustodianOrganization",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class AssignedEntity:
    class Meta:
        name = "assignedEntity"
        namespace = "urn:hl7-org:v3"

    id: Optional[Id] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    telecom: List[Telecom] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    assigned_person: Optional[AssignedPerson] = field(
        default=None,
        metadata={
            "name": "assignedPerson",
            "type": "Element",
            "required": True,
        },
    )
    represented_organization: Optional[RepresentedOrganization] = field(
        default=None,
        metadata={
            "name": "representedOrganization",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Code1:
    class Meta:
        name = "code"
        namespace = "urn:hl7-org:v3"

    code: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    code_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystem",
            "type": "Attribute",
        },
    )
    code_system_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "codeSystemName",
            "type": "Attribute",
        },
    )
    display_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "displayName",
            "type": "Attribute",
        },
    )
    original_text: Optional[OriginalText] = field(
        default=None,
        metadata={
            "name": "originalText",
            "type": "Element",
        },
    )
    null_flavor: Optional[str] = field(
        default=None,
        metadata={
            "name": "nullFlavor",
            "type": "Attribute",
        },
    )


@dataclass
class Patient:
    class Meta:
        name = "patient"
        namespace = "urn:hl7-org:v3"

    name: Optional[Name] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    administrative_gender_code: Optional[AdministrativeGenderCode] = field(
        default=None,
        metadata={
            "name": "administrativeGenderCode",
            "type": "Element",
            "required": True,
        },
    )
    birth_time: Optional[BirthTime] = field(
        default=None,
        metadata={
            "name": "birthTime",
            "type": "Element",
            "required": True,
        },
    )
    race_code: Optional[RaceCode] = field(
        default=None,
        metadata={
            "name": "raceCode",
            "type": "Element",
            "required": True,
        },
    )
    ethnic_group_code: Optional[EthnicGroupCode] = field(
        default=None,
        metadata={
            "name": "ethnicGroupCode",
            "type": "Element",
            "required": True,
        },
    )
    language_communication: Optional[LanguageCommunication] = field(
        default=None,
        metadata={
            "name": "languageCommunication",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Text:
    class Meta:
        name = "text"
        namespace = "urn:hl7-org:v3"

    soci_info_hndgs: Optional[str] = field(
        default=None,
        metadata={
            "name": "sociInfoHNDGS",
            "type": "Element",
        },
    )
    list_value: Optional[ListType] = field(
        default=None,
        metadata={
            "name": "list",
            "type": "Element",
        },
    )
    reference: Optional[Reference] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class AsContent:
    class Meta:
        name = "asContent"
        namespace = "urn:epsos-org:ep:medication"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    container_packaged_medicine: Optional[ContainerPackagedMedicine] = field(
        default=None,
        metadata={
            "name": "containerPackagedMedicine",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Act:
    class Meta:
        name = "act"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    mood_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "moodCode",
            "type": "Attribute",
            "required": True,
        },
    )
    id: List[Id] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    template_id: List[TemplateId] = field(
        default_factory=list,
        metadata={
            "name": "templateId",
            "type": "Element",
            "sequence": 1,
        },
    )
    code: Optional[Code1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    text: Optional[Text] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    status_code: Optional[StatusCode] = field(
        default=None,
        metadata={
            "name": "statusCode",
            "type": "Element",
        },
    )
    effective_time: Optional[EffectiveTime] = field(
        default=None,
        metadata={
            "name": "effectiveTime",
            "type": "Element",
        },
    )
    entry_relationship: List["EntryRelationship"] = field(
        default_factory=list,
        metadata={
            "name": "entryRelationship",
            "type": "Element",
        },
    )


@dataclass
class Author:
    class Meta:
        name = "author"
        namespace = "urn:hl7-org:v3"

    function_code: Optional[FunctionCode] = field(
        default=None,
        metadata={
            "name": "functionCode",
            "type": "Element",
            "required": True,
        },
    )
    time: Optional[Time] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    assigned_author: Optional[AssignedAuthor] = field(
        default=None,
        metadata={
            "name": "assignedAuthor",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Custodian:
    class Meta:
        name = "custodian"
        namespace = "urn:hl7-org:v3"

    type_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeCode",
            "type": "Attribute",
            "required": True,
        },
    )
    assigned_custodian: Optional[AssignedCustodian] = field(
        default=None,
        metadata={
            "name": "assignedCustodian",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class EncompassingEncounter:
    class Meta:
        name = "encompassingEncounter"
        namespace = "urn:hl7-org:v3"

    id: List[Id] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    code: Optional[Code1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    effective_time: Optional[EffectiveTime] = field(
        default=None,
        metadata={
            "name": "effectiveTime",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class LegalAuthenticator:
    class Meta:
        name = "legalAuthenticator"
        namespace = "urn:hl7-org:v3"

    time: Optional[Time] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    signature_code: Optional[SignatureCode] = field(
        default=None,
        metadata={
            "name": "signatureCode",
            "type": "Element",
            "required": True,
        },
    )
    assigned_entity: Optional[AssignedEntity] = field(
        default=None,
        metadata={
            "name": "assignedEntity",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Observation:
    class Meta:
        name = "observation"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    mood_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "moodCode",
            "type": "Attribute",
            "required": True,
        },
    )
    template_id: List[TemplateId] = field(
        default_factory=list,
        metadata={
            "name": "templateId",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    code: Optional[Code1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    status_code: Optional[StatusCode] = field(
        default=None,
        metadata={
            "name": "statusCode",
            "type": "Element",
            "required": True,
        },
    )
    value: Optional[Value] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PatientRole:
    class Meta:
        name = "patientRole"
        namespace = "urn:hl7-org:v3"

    id: List[Id] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    addr: Optional[Addr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    telecom: List[Telecom] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    patient: Optional[Patient] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class ComponentOf:
    class Meta:
        name = "componentOf"
        namespace = "urn:hl7-org:v3"

    encompassing_encounter: Optional[EncompassingEncounter] = field(
        default=None,
        metadata={
            "name": "encompassingEncounter",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class EntryRelationship:
    class Meta:
        name = "entryRelationship"
        namespace = "urn:hl7-org:v3"

    type_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeCode",
            "type": "Attribute",
            "required": True,
        },
    )
    inversion_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "inversionInd",
            "type": "Attribute",
        },
    )
    act: Optional[Act] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    observation: Optional[Observation] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    supply: Optional[Supply] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class ManufacturedMaterial:
    class Meta:
        name = "manufacturedMaterial"
        namespace = "urn:hl7-org:v3"

    code: Optional[Code1] = field(
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
    form_code: Optional[FormCode] = field(
        default=None,
        metadata={
            "name": "formCode",
            "type": "Element",
            "namespace": "urn:epsos-org:ep:medication",
            "required": True,
        },
    )
    as_content: Optional[AsContent] = field(
        default=None,
        metadata={
            "name": "asContent",
            "type": "Element",
            "namespace": "urn:epsos-org:ep:medication",
            "required": True,
        },
    )
    ingredient: Optional[Ingredient] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:epsos-org:ep:medication",
            "required": True,
        },
    )


@dataclass
class RecordTarget:
    class Meta:
        name = "recordTarget"
        namespace = "urn:hl7-org:v3"

    context_control_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "contextControlCode",
            "type": "Attribute",
            "required": True,
        },
    )
    type_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeCode",
            "type": "Attribute",
            "required": True,
        },
    )
    patient_role: Optional[PatientRole] = field(
        default=None,
        metadata={
            "name": "patientRole",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class ManufacturedProduct:
    class Meta:
        name = "manufacturedProduct"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    template_id: List[TemplateId] = field(
        default_factory=list,
        metadata={
            "name": "templateId",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    manufactured_material: Optional[ManufacturedMaterial] = field(
        default=None,
        metadata={
            "name": "manufacturedMaterial",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Consumable:
    class Meta:
        name = "consumable"
        namespace = "urn:hl7-org:v3"

    manufactured_product: Optional[ManufacturedProduct] = field(
        default=None,
        metadata={
            "name": "manufacturedProduct",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SubstanceAdministration:
    class Meta:
        name = "substanceAdministration"
        namespace = "urn:hl7-org:v3"

    class_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "classCode",
            "type": "Attribute",
            "required": True,
        },
    )
    mood_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "moodCode",
            "type": "Attribute",
            "required": True,
        },
    )
    template_id: List[TemplateId] = field(
        default_factory=list,
        metadata={
            "name": "templateId",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    id: Optional[Id] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    status_code: Optional[StatusCode] = field(
        default=None,
        metadata={
            "name": "statusCode",
            "type": "Element",
            "required": True,
        },
    )
    effective_time: List[EffectiveTime] = field(
        default_factory=list,
        metadata={
            "name": "effectiveTime",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    dose_quantity: Optional[DoseQuantity] = field(
        default=None,
        metadata={
            "name": "doseQuantity",
            "type": "Element",
            "required": True,
        },
    )
    rate_quantity: Optional[RateQuantity] = field(
        default=None,
        metadata={
            "name": "rateQuantity",
            "type": "Element",
            "required": True,
        },
    )
    consumable: Optional[Consumable] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    entry_relationship: List[EntryRelationship] = field(
        default_factory=list,
        metadata={
            "name": "entryRelationship",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Entry:
    class Meta:
        name = "entry"
        namespace = "urn:hl7-org:v3"

    template_id: Optional[TemplateId] = field(
        default=None,
        metadata={
            "name": "templateId",
            "type": "Element",
        },
    )
    substance_administration: Optional[SubstanceAdministration] = field(
        default=None,
        metadata={
            "name": "substanceAdministration",
            "type": "Element",
        },
    )
    act: Optional[Act] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Section:
    class Meta:
        name = "section"
        namespace = "urn:hl7-org:v3"

    template_id: Optional[TemplateId] = field(
        default=None,
        metadata={
            "name": "templateId",
            "type": "Element",
            "required": True,
        },
    )
    id: Optional[Id] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    code: Optional[Code1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    title: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    text: Optional[Text] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    entry: List[Entry] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Component:
    class Meta:
        name = "component"
        namespace = "urn:hl7-org:v3"

    section: Optional[Section] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    structured_body: Optional[StructuredBody] = field(
        default=None,
        metadata={
            "name": "structuredBody",
            "type": "Element",
        },
    )


@dataclass
class ClinicalDocument:
    class Meta:
        namespace = "urn:hl7-org:v3"

    realm_code: Optional[RealmCode] = field(
        default=None,
        metadata={
            "name": "realmCode",
            "type": "Element",
            "required": True,
        },
    )
    type_id: Optional[TypeId] = field(
        default=None,
        metadata={
            "name": "typeId",
            "type": "Element",
            "required": True,
        },
    )
    template_id: List[TemplateId] = field(
        default_factory=list,
        metadata={
            "name": "templateId",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    id: Optional[Id] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    code: Optional[Code1] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    title: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    effective_time: Optional[EffectiveTime] = field(
        default=None,
        metadata={
            "name": "effectiveTime",
            "type": "Element",
            "required": True,
        },
    )
    confidentiality_code: Optional[ConfidentialityCode] = field(
        default=None,
        metadata={
            "name": "confidentialityCode",
            "type": "Element",
            "required": True,
        },
    )
    language_code: Optional[LanguageCode] = field(
        default=None,
        metadata={
            "name": "languageCode",
            "type": "Element",
            "required": True,
        },
    )
    record_target: Optional[RecordTarget] = field(
        default=None,
        metadata={
            "name": "recordTarget",
            "type": "Element",
            "required": True,
        },
    )
    author: Optional[Author] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    custodian: Optional[Custodian] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    legal_authenticator: Optional[LegalAuthenticator] = field(
        default=None,
        metadata={
            "name": "legalAuthenticator",
            "type": "Element",
            "required": True,
        },
    )
    component_of: Optional[ComponentOf] = field(
        default=None,
        metadata={
            "name": "componentOf",
            "type": "Element",
            "required": True,
        },
    )
    component: Optional[Component] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
