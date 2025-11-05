from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EffectiveTime:
    since: str
    until: str


@dataclass(frozen=True)
class Telecom:
    phone: Optional[str]
    email: Optional[str]


@dataclass(frozen=True)
class Addr:
    street_address_line: Optional[str]
    city: Optional[str]
    postal_code: Optional[int]
    country: Optional[str]


@dataclass(frozen=True)
class RepresentedOrganization:
    name: Optional[str]
    telecom: Optional[Telecom]
    addr: Optional[Addr]
