from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.common import (
    RepresentedOrganization,
    Telecom,
)


@dataclass(frozen=True)
class AssignedAuthor:
    doctor_id: Optional[str]
    doctor_amka: Optional[str]
    doctor_specialty_id: str
    doctor_specialty_name: str
    doctor_etee: Optional[str]
    telecom: Optional[Telecom]
    given_name: Optional[str]
    family_name: Optional[str]
    represented_organization: Optional[RepresentedOrganization]


@dataclass(frozen=True)
class Author:
    time: Optional[str]
    assigned_author: AssignedAuthor
