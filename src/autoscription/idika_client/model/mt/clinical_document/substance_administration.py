from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Period:
    value: Optional[str]
    unit: Optional[str]


@dataclass(frozen=True)
class DoseQuantity:
    low_value: Optional[str]
    low_unit: Optional[str]
    high_value: Optional[str]
    high_unit: Optional[str]


@dataclass(frozen=True)
class RateQuantity:
    value: Optional[str]
    unit: Optional[str]


@dataclass(frozen=True)
class FormCode:
    code: Optional[str]
    code_system: Optional[str]
    code_system_name: Optional[str]
    display_name: Optional[str]
    translation: str


@dataclass(frozen=True)
class Ingredient:
    code: Optional[str]
    code_system_name: Optional[str]
    display_name: Optional[str]
    name: Optional[str]


@dataclass(frozen=True)
class ContainerPackagedMedicine:
    name: Optional[str]
    package_code: Optional[str]
    package_display_name: Optional[str]
    capacity: Optional[str]


@dataclass(frozen=True)
class Consumable:
    # <!-- To barcode του φαρμάκου, είναι τιμή αναφοράς σε γραμμή που
    # συμπεριλαμβάνει την τιμή του πεδίου "#med_barcode_1" -->
    barcode: Optional[str]
    name: str
    form_code: FormCode
    ingredient: Optional[Ingredient]
    container_packaged_medicine: Optional[ContainerPackagedMedicine]


@dataclass(frozen=True)
class PrescribedDose:
    value: Optional[str]
    unit: Optional[str]


@dataclass(frozen=True)
class ExecutionDetails:
    # patient_consent: bool
    # execution_quantity: int
    # execution_price: float
    # reference_price: float
    # retail_price: float
    authenticity_tape: Optional[List[str]]
    # insurer_difference_per_execution_quantity: float
    # execution_datetime: datetime.datetime


@dataclass(frozen=True)
class SubstanceAdministration:
    barcode: str
    status_code: Optional[str]
    period: Optional[Period]
    dose_quantity: Optional[DoseQuantity]
    rate_quantity: Optional[RateQuantity]
    consumable: Consumable
    prescribed_dose: Optional[PrescribedDose]
    execution_details: Optional[ExecutionDetails]
    # entry_relationship: List[EntryRelationship]
    # length 6 or 5
    # we should always get 5, but we need to check
    # 1 prescribed dosage, what is the difference between prescribed dose and dose quantity
    # 2 doctors comments/instructions
    # 3 special use case
    # 4 drug details
    # 5 execution details
    # 6 List of diagnoses
