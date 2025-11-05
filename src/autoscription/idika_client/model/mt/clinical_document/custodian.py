from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.common import (
    RepresentedOrganization,
)


@dataclass(frozen=True)
class Custodian:
    type_code: Optional[str]
    assigned_custodian: Optional[RepresentedOrganization]
