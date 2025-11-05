from dataclasses import dataclass
from datetime import datetime


@dataclass
class PharmacistUnit:
    pharmacy_id: int
    pharmacy_name: str
    expiry_date: datetime
    start_date: datetime
    tax_registry_number: str
