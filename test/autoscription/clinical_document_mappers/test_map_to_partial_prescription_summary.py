import pytest

from src.autoscription.clinical_document_mappers.partial_prescriptions_summaries_dataframe_mapper import (
    __map_to_partial_prescription_summary as map_to_partial_prescription_summary,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document.partial_clinical_document import (
    ExecutionDetails,
    PartialClinicalDocument,
    ProductSupply,
)


class TestMapToPartialPrescriptionSummary:
    def test_should_map_to_summary_with_high_cost_drug_when_price_exceeds_limit(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=5000))],
        )
        summary = map_to_partial_prescription_summary(document, 3000.0)
        assert summary.contains_high_cost_drug_above_limit is True
        assert summary.retail_prices == "5000"

    def test_should_map_to_summary_without_high_cost_drug_when_price_does_not_exceed_limit(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=2000))],
        )
        summary = map_to_partial_prescription_summary(document, 3000.0)
        assert summary.contains_high_cost_drug_above_limit is False
        assert summary.retail_prices == "2000"

    def test_should_map_to_summary_without_high_cost_drug_when_price_does_not_exceed_limit_multiple_products(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[
                ProductSupply(execution_details=ExecutionDetails(retail_price=2000)),
                ProductSupply(execution_details=ExecutionDetails(retail_price=2000)),
            ],
        )
        summary = map_to_partial_prescription_summary(document, 3000.0)
        assert summary.contains_high_cost_drug_above_limit is False
        assert summary.retail_prices == "2000 2000"

    def test_should_map_to_summary_with_empty_retail_prices_when_product_supplies_is_empty(self):
        document = PartialClinicalDocument(barcode="123", execution=1, summary=None, product_supplies=[])
        summary = map_to_partial_prescription_summary(document, 3000.0)
        assert summary.contains_high_cost_drug_above_limit is False
        assert summary.retail_prices == ""
