from typing import Dict, List

from src.autoscription.core.errors import (
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    Entry,
    EntryRelationship,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    PartialClinicalDocument as IdikaPartialClinicalDocument,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document import (
    ExecutionDetails,
    PartialClinicalDocument,
    ProductSupply,
)


def check_for_required_values(idika_partial_clinical_document: IdikaPartialClinicalDocument) -> None:
    if not (
        idika_partial_clinical_document
        and idika_partial_clinical_document.id
        and idika_partial_clinical_document.id.root
        and idika_partial_clinical_document.id.root == "1.21"
        and idika_partial_clinical_document.id.extension
        and idika_partial_clinical_document.component
        and idika_partial_clinical_document.component.structured_body
        and idika_partial_clinical_document.component.structured_body.component
        and idika_partial_clinical_document.component.structured_body.component.section
        and idika_partial_clinical_document.component.structured_body.component.section.entry
    ):
        raise MappingIdikaResponseMissingRequiredValueException()
    else:
        return None


def map_execution_details(entry_relationships: List[EntryRelationship], execution: int) -> ExecutionDetails:
    authenticity_tapes = []
    retail_price = None
    for entry_relationship in entry_relationships:
        if entry_relationship.act:
            ids: Dict[str, str] = {
                str(id_element.root): str(id_element.extension) for id_element in entry_relationship.act.id
            }
            if "2.10.11" in ids:
                retail_price = float(ids["2.10.11"])
            if "2.10.12" in ids and ids["2.10.8"] == str(execution):
                authenticity_tapes.append(ids["2.10.12"])
        else:
            raise MappingIdikaResponseMissingRequiredValueException()
    return ExecutionDetails(
        retail_price=retail_price,
        authenticity_tape=authenticity_tapes,
    )


def map_product_supply(product_supply_entry: Entry, execution: int) -> ProductSupply:
    if not (
        product_supply_entry
        and product_supply_entry.supply
        and product_supply_entry.supply.entry_relationship
        and len(product_supply_entry.supply.entry_relationship) > 0
    ):
        raise MappingIdikaResponseMissingRequiredValueException()
    sa_entry_relationship = product_supply_entry.supply.entry_relationship[-1]
    entry_relationships = [
        entry_relationship
        for entry_relationship in (
            sa_entry_relationship.substance_administration.entry_relationship  # type: ignore[union-attr]
        )
        if entry_relationship.type_code == "SPRT"
    ]
    return ProductSupply(
        execution_details=map_execution_details(entry_relationships=entry_relationships, execution=execution)
    )


def map_partial_clinical_document(
    idika_partial_clinical_document: IdikaPartialClinicalDocument, execution: int
) -> PartialClinicalDocument:
    check_for_required_values(idika_partial_clinical_document)
    structured_body = idika_partial_clinical_document.component.structured_body  # type: ignore[union-attr]
    # texts = idika_partial_clinical_document.component.structured_body.component.section.text
    entries = structured_body.component.section.entry  # type: ignore[arg-type, union-attr]
    # summary_entry = entries[0]
    product_supply_entries = entries[1:]
    product_supplies = [
        map_product_supply(product_supply_entry=ps, execution=execution) for ps in product_supply_entries
    ]

    return PartialClinicalDocument(
        barcode=str(idika_partial_clinical_document.id.extension),  # type: ignore[union-attr]
        execution=execution,
        summary=None,
        product_supplies=product_supplies,
    )
