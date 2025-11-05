from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.common import (
    EffectiveTime,
)


@dataclass(frozen=True)
class Visit:
    visit_id: str
    unit_of_prescription_id: str
    insurance_carrier_id: str
    comments: str
    reason_for_visit: str
    visit_within_limit: str
    status: Optional[str]
    effective_time: Optional[EffectiveTime]
