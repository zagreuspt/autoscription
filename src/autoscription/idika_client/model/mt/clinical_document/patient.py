from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.common import (
    Addr,
    Telecom,
)


@dataclass(frozen=True)
class Patient:
    given: Optional[str]
    family: Optional[str]
    gender_code: Optional[str]
    birth_time: Optional[str]
    race_code: Optional[str]
    ethnic_group_code: Optional[str]
    language_communication: Optional[str]


@dataclass(frozen=True)
class PatientRole:
    patient_amka: str
    prescribing_insurer_id: str
    prescribing_insurer_name: str
    prescribing_ama: str
    insured_type: str
    last_update_date_of_insurer: str
    insurance_capability_expiry_date: str
    indication_that_patient_has_declared_to_receive_prescriptions_electronically: str
    addr: Optional[Addr]
    telecom: Optional[Telecom]
    patient: Optional[Patient]
