from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.common import (
    RepresentedOrganization,
    Telecom,
)


@dataclass(frozen=True)
class AssignedEntity:
    doctor_id: Optional[str]
    telecom: Optional[Telecom]
    given_name: str
    family_name: str
    represented_organization: Optional[RepresentedOrganization]


@dataclass(frozen=True)
class LegalAuthenticator:
    time: Optional[str]
    signature_code: Optional[str]
    assigned_entity: Optional[AssignedEntity]
