from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Summary:
    pass


@dataclass(frozen=True)
class ExecutionDetails:
    retail_price: Optional[float]
    authenticity_tape: Optional[List[str]]


@dataclass(frozen=True)
class ProductSupply:
    execution_details: ExecutionDetails


@dataclass(frozen=True)
class PartialClinicalDocument:
    barcode: str
    execution: int
    summary: Optional[Summary]
    product_supplies: List[ProductSupply]
