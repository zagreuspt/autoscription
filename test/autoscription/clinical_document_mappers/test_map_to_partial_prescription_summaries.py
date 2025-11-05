import pandas as pd
import pytest

from src.autoscription.clinical_document_mappers.partial_prescriptions_summaries_dataframe_mapper import (
    map_to_partial_prescription_summaries_dataframe_from_list,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document.partial_clinical_document import (
    ExecutionDetails,
    PartialClinicalDocument,
    ProductSupply,
)


class TestMapToPartialPrescriptionSummariesDataframeFromList:
    def test_should_return_empty_dataframe_when_list_is_empty(self):
        documents = []
        result = map_to_partial_prescription_summaries_dataframe_from_list(documents, 3000.0)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_should_return_empty_dataframe_when_list_is_none(self):
        documents = None
        result = map_to_partial_prescription_summaries_dataframe_from_list(documents, 3000.0)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_should_return_dataframe_with_single_row_when_list_contains_single_document(self):
        document = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=2000))],
        )
        documents = [document]
        result = map_to_partial_prescription_summaries_dataframe_from_list(documents, 3000.0)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["prescription"] == "123"
        assert result.iloc[0]["execution"] == 1
        assert result.iloc[0]["contains_high_cost_drug_above_limit"] == False
        assert result.iloc[0]["retail_prices"] == "2000"

    def test_should_return_dataframe_with_multiple_rows_when_list_contains_multiple_documents(self):
        document1 = PartialClinicalDocument(
            barcode="123",
            execution=1,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=2000))],
        )
        document2 = PartialClinicalDocument(
            barcode="456",
            execution=2,
            summary=None,
            product_supplies=[ProductSupply(execution_details=ExecutionDetails(retail_price=3001))],
        )
        documents = [document1, document2]
        result = map_to_partial_prescription_summaries_dataframe_from_list(documents, 3000.0)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]["prescription"] == "123"
        assert result.iloc[0]["execution"] == 1
        assert result.iloc[0]["contains_high_cost_drug_above_limit"] == False
        assert result.iloc[0]["retail_prices"] == "2000"
        assert result.iloc[1]["prescription"] == "456"
        assert result.iloc[1]["execution"] == 2
        assert result.iloc[1]["contains_high_cost_drug_above_limit"] == True
        assert result.iloc[1]["retail_prices"] == "3001"
