import pytest

from src.autoscription.clinical_document_mappers.partial_prescriptions_summaries_dataframe_mapper import (
    contains_high_cost_drug_above_limit,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document.partial_clinical_document import (
    ExecutionDetails,
    PartialClinicalDocument,
    ProductSupply,
)


class TestContainsHighCostDrugAboveLimit:
    def test_returns_true_when_drug_price_exceeds_limit(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[
                ProductSupply(execution_details=ExecutionDetails(retail_price=5000)),
                ProductSupply(execution_details=ExecutionDetails(retail_price=2000)),
            ],
        )
        assert contains_high_cost_drug_above_limit(document, 3000) is True

    def test_returns_false_when_no_drug_price_exceeds_limit(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[
                ProductSupply(execution_details=ExecutionDetails(retail_price=2000)),
                ProductSupply(execution_details=ExecutionDetails(retail_price=1000)),
            ],
        )
        assert contains_high_cost_drug_above_limit(document, 3000) is False

    def test_returns_false_when_retail_price_is_none(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=None))],
        )
        assert contains_high_cost_drug_above_limit(document, 3000) is False

    def test_returns_false_when_product_supplies_is_empty(self):
        document = PartialClinicalDocument(barcode="123", execution=1, summary=None, product_supplies=[])
        assert contains_high_cost_drug_above_limit(document, 3000) is False
