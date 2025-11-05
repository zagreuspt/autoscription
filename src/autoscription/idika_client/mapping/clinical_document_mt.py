from __future__ import annotations

from typing import List  # noqa: PEA001

from src.autoscription.core.errors import (
    MappingIdikaResponseException,
    MappingIdikaResponseMissingRequiredValueException,
)
from src.autoscription.idika_client.mapping.utils import get_boolean_from_id_value
from src.autoscription.idika_client.model.idika.clinical_document import (
    Author,
    ClinicalDocument,
    Entry,
    EntryRelationship,
    Item,
    ManufacturedMaterial,
    Section,
    SubstanceAdministration,
)
from src.autoscription.idika_client.model.mt.clinical_document.author import (
    AssignedAuthor as AssignedAuthorMt,
)
from src.autoscription.idika_client.model.mt.clinical_document.author import (
    Author as AuthorMt,
)
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument as ClinicalDocumentMt,
)
from src.autoscription.idika_client.model.mt.clinical_document.common import (
    EffectiveTime,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Section as SectionMt,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Summary,
)
from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    Consumable,
    ContainerPackagedMedicine,
    DoseQuantity,
    ExecutionDetails,
    FormCode,
    Ingredient,
    Period,
    PrescribedDose,
    RateQuantity,
)
from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    SubstanceAdministration as SubstanceAdministrationMt,
)


# TODO: write tests for each mapper
def map_consumable(manufactured_material: ManufacturedMaterial, references: dict[str, str]) -> Consumable:
    if (
        manufactured_material.name
        and manufactured_material.form_code
        and manufactured_material.form_code.translation
        and manufactured_material.form_code.translation.display_name
    ):
        reference_value = (
            manufactured_material.code.original_text.reference.value
            if manufactured_material.code
            and manufactured_material.code.original_text
            and manufactured_material.code.original_text.reference
            else None
        )
        return Consumable(
            barcode=str(references.get(reference_value.split("#")[1], "missing") if reference_value else "missing"),
            name=manufactured_material.name,
            form_code=FormCode(
                code=manufactured_material.form_code.code,
                code_system=manufactured_material.form_code.code_system,
                code_system_name=manufactured_material.form_code.code_system_name,
                display_name=manufactured_material.form_code.display_name,
                translation=manufactured_material.form_code.translation.display_name,
            ),
            ingredient=(
                Ingredient(
                    code=(
                        str(manufactured_material.ingredient.ingredient.code.code)
                        if manufactured_material.ingredient.ingredient.code
                        else None
                    ),
                    code_system_name=(
                        manufactured_material.ingredient.ingredient.code.code_system_name
                        if manufactured_material.ingredient.ingredient.code
                        else None
                    ),
                    display_name=(
                        manufactured_material.ingredient.ingredient.code.display_name
                        if manufactured_material.ingredient.ingredient.code
                        else None
                    ),
                    name=manufactured_material.ingredient.ingredient.name,
                )
                if manufactured_material.ingredient and manufactured_material.ingredient.ingredient
                else None
            ),
            container_packaged_medicine=(
                ContainerPackagedMedicine(
                    name=manufactured_material.as_content.container_packaged_medicine.name,
                    package_code=(
                        manufactured_material.as_content.container_packaged_medicine.form_code.code
                        if manufactured_material.as_content.container_packaged_medicine.form_code
                        and manufactured_material.as_content.container_packaged_medicine.form_code.code
                        else None
                    ),
                    package_display_name=(
                        manufactured_material.as_content.container_packaged_medicine.form_code.display_name
                        if manufactured_material.as_content.container_packaged_medicine.form_code
                        and manufactured_material.as_content.container_packaged_medicine.form_code.display_name
                        else None
                    ),
                    capacity=(
                        str(manufactured_material.as_content.container_packaged_medicine.capacity_quantity.value)
                        if manufactured_material.as_content.container_packaged_medicine.capacity_quantity
                        and manufactured_material.as_content.container_packaged_medicine.capacity_quantity.value
                        else None
                    ),
                )
                if manufactured_material.as_content and manufactured_material.as_content.container_packaged_medicine
                else None
            ),
        )
    else:
        raise MappingIdikaResponseMissingRequiredValueException()


def map_execution_details(entry_relationships: List[EntryRelationship]) -> ExecutionDetails:
    required_ids = {"2.10.12"}
    # "2.10.6", "2.10.8", "2.10.9", "2.10.11", "2.10.10", "2.10.12", "1.4.21.2"}
    authenticity_tapes = []
    for entry_relationship in entry_relationships:
        if entry_relationship.act:
            act_ids: dict[str, str] = {
                str(id_element.root): str(id_element.extension) for id_element in entry_relationship.act.id
            }
            effective_time = entry_relationship.act.effective_time
            if required_ids.issubset(act_ids.keys()) and effective_time and effective_time.value:
                authenticity_tapes.append(act_ids["2.10.12"])

        else:
            raise MappingIdikaResponseMissingRequiredValueException()
    if authenticity_tapes:
        return ExecutionDetails(
            # patient_consent=get_boolean_from_id_value(act_ids["2.10.6"]),
            # execution_quantity=int(act_ids["2.10.8"]),
            # execution_price=float(act_ids["2.10.9"]),
            # reference_price=float(act_ids["2.10.11"]),
            # retail_price=float(act_ids["2.10.10"]),
            authenticity_tape=authenticity_tapes,
            # insurer_difference_per_execution_quantity=float(act_ids["1.4.21.2"]),
            # execution_datetime=datetime.strptime(effective_time.value, "%Y%m%d%H%M%S"),
        )
    else:
        return ExecutionDetails(authenticity_tape=None)


def map_substance_administration(
    substance_administration: SubstanceAdministration, references: dict[str, str]
) -> SubstanceAdministrationMt:
    if (
        substance_administration
        and substance_administration.entry_relationship
        and len(substance_administration.entry_relationship) > 0
        and substance_administration.consumable
        and substance_administration.consumable.manufactured_product
        and substance_administration.consumable.manufactured_product.manufactured_material
    ):
        prescribed_dose_entry = substance_administration.entry_relationship[0]

        prescribed_dose = (
            PrescribedDose(
                value=prescribed_dose_entry.supply.quantity.value,
                unit=prescribed_dose_entry.supply.quantity.unit,
            )
            if prescribed_dose_entry and prescribed_dose_entry.supply and prescribed_dose_entry.supply.quantity
            else None
        )
        entry_relationships = [
            entry_relationship
            for entry_relationship in substance_administration.entry_relationship
            if entry_relationship.type_code == "SPRT"
        ]
        return SubstanceAdministrationMt(
            barcode=str(  # todo: use the generic mapping method once in place
                substance_administration.id.extension
                if substance_administration.id
                and substance_administration.id.root
                and substance_administration.id.root == "1.21.1"
                else "missing"
            ),
            status_code=(
                substance_administration.status_code.code
                if substance_administration.status_code and substance_administration.status_code.code
                else None
            ),
            period=(
                Period(
                    value=substance_administration.effective_time[1].period.value,
                    unit=substance_administration.effective_time[1].period.unit,
                )
                if substance_administration.effective_time[1].period
                else None
            ),
            dose_quantity=(
                DoseQuantity(
                    low_value=(
                        substance_administration.dose_quantity.low.value
                        if substance_administration.dose_quantity.low
                        and substance_administration.dose_quantity.low.value
                        else None
                    ),
                    low_unit=(
                        substance_administration.dose_quantity.low.unit
                        if substance_administration.dose_quantity.low
                        and substance_administration.dose_quantity.low.unit
                        else None
                    ),
                    high_value=(
                        substance_administration.dose_quantity.high.value
                        if substance_administration.dose_quantity.high
                        and substance_administration.dose_quantity.high.value
                        else None
                    ),
                    high_unit=(
                        substance_administration.dose_quantity.high.unit
                        if substance_administration.dose_quantity.high
                        and substance_administration.dose_quantity.high.unit
                        else None
                    ),
                )
                if substance_administration.dose_quantity
                else None
            ),
            rate_quantity=(
                RateQuantity(
                    value=substance_administration.rate_quantity.low.value,
                    unit=substance_administration.rate_quantity.low.unit,
                )
                if substance_administration.rate_quantity and substance_administration.rate_quantity.low
                else None
            ),
            consumable=map_consumable(
                substance_administration.consumable.manufactured_product.manufactured_material,
                references,
            ),
            prescribed_dose=prescribed_dose,
            execution_details=map_execution_details(entry_relationships),
        )
    else:
        raise MappingIdikaResponseMissingRequiredValueException()


def map_summary(summary_entry: Entry) -> Summary:
    required_ids = {"1.1.7", "1.1.8", "1.1.23"}
    if summary_entry.act:
        act_ids: dict[str, str] = {
            str(id_element.root): str(id_element.extension) for id_element in summary_entry.act.id
        }
        if required_ids.issubset(act_ids.keys()):
            return Summary(
                contains_high_cost_drug=get_boolean_from_id_value(act_ids["1.1.7"]),
                contains_desensitization_vaccine=get_boolean_from_id_value(act_ids["1.1.8"]),
                medical_report_required=get_boolean_from_id_value(act_ids["1.1.23"]),
            )
        else:
            raise MappingIdikaResponseMissingRequiredValueException()
    else:
        raise MappingIdikaResponseMissingRequiredValueException()


def map_section(section: Section) -> SectionMt:
    summary_entry = section.entry[0]

    e: Entry  # noqa: F842
    substance_administrations_idika = (
        [e.substance_administration for e in section.entry[1:] if e and e.substance_administration]
        if section and section.entry and len(section.entry) > 1
        else []
    )
    # todo: split based on entry content, if id has act or if it has substance administration
    i: Item  # noqa: F842
    references: dict[str, str] = (
        {str(i.id): str(i.value) for i in section.text.list_value.item}
        if section and section.text and section.text.list_value and section.text.list_value.item
        else {}
    )

    sa: SubstanceAdministration  # noqa: F842
    substance_administrations: list[SubstanceAdministrationMt] = [
        map_substance_administration(sa, references) for sa in substance_administrations_idika
    ]

    return SectionMt(
        barcode=None,
        text=None,
        summary=map_summary(summary_entry=summary_entry),
        substance_administrations=substance_administrations,
    )


def map_author(author: Author) -> AuthorMt:
    required_ids = {"1.19.1", "1.19.2"}
    if author and author.assigned_author and author.assigned_author.id:
        assigned_author_ids: dict[str, str] = {
            str(id_element.root): str(id_element.extension) for id_element in author.assigned_author.id
        }
        if required_ids.issubset(assigned_author_ids.keys()):
            return AuthorMt(
                time=None,
                assigned_author=AssignedAuthorMt(
                    doctor_id=None,
                    doctor_amka=None,
                    doctor_specialty_id=assigned_author_ids["1.19.1"],
                    doctor_specialty_name=assigned_author_ids["1.19.2"],
                    doctor_etee=None,
                    telecom=None,
                    given_name=None,
                    family_name=None,
                    represented_organization=None,
                ),
            )
        else:
            raise MappingIdikaResponseException()
    else:
        raise MappingIdikaResponseException()


def map_clinical_document(clinical_document: ClinicalDocument) -> ClinicalDocumentMt:
    check_for_required_values(clinical_document)
    try:
        return ClinicalDocumentMt(
            barcode=str(clinical_document.id.extension),  # type: ignore[arg-type, union-attr]
            effective_time=EffectiveTime(
                # checked in check_for_required_values
                since=str(clinical_document.effective_time.low.value),  # type: ignore[arg-type, union-attr]
                # checked in check_for_required_values
                until=str(clinical_document.effective_time.high.value),  # type: ignore[arg-type, union-attr]
            ),
            author=map_author(clinical_document.author),  # type: ignore[arg-type, union-attr]
            custodian=None,
            doctor_visit=None,
            patient_role=None,
            legal_authenticator=None,
            section=map_section(
                # checked in check_for_required_values
                clinical_document.component.structured_body.component.section  # type: ignore[arg-type, union-attr]
            ),
        )
    except Exception as e:
        raise MappingIdikaResponseException(e)


# TODO: improve on the design
def check_for_required_values(clinical_document: ClinicalDocument) -> None:
    if not (
        clinical_document
        and clinical_document.id
        and clinical_document.id.root
        and clinical_document.id.root == "1.21"
        and clinical_document.id.extension
        and clinical_document.component
        and clinical_document.component.structured_body
        and clinical_document.component.structured_body.component
        and clinical_document.component.structured_body.component.section
        and clinical_document.effective_time
        and clinical_document.effective_time.high
        and clinical_document.effective_time.high.value
        and clinical_document.effective_time.low
        and clinical_document.effective_time.low.value
        and clinical_document.author
    ):
        raise MappingIdikaResponseMissingRequiredValueException()
    else:
        return None
