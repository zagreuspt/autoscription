from dataclasses import dataclass
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.author import Author
from src.autoscription.idika_client.model.mt.clinical_document.common import (
    EffectiveTime,
)
from src.autoscription.idika_client.model.mt.clinical_document.custodian import (
    Custodian,
)
from src.autoscription.idika_client.model.mt.clinical_document.legal_authenticator import (
    LegalAuthenticator,
)
from src.autoscription.idika_client.model.mt.clinical_document.patient import (
    PatientRole,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Section,
)
from src.autoscription.idika_client.model.mt.clinical_document.visit import Visit


@dataclass(frozen=True)
class ClinicalDocument:
    barcode: str
    effective_time: EffectiveTime
    patient_role: Optional[PatientRole]
    author: Author
    custodian: Optional[Custodian]
    legal_authenticator: Optional[LegalAuthenticator]
    doctor_visit: Optional[Visit]
    section: Section
