import pytest

from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.clinical_document.common import (
    EffectiveTime,
)
from src.autoscription.idika_client.model.mt.clinical_document.prescription import (
    Section,
    Summary,
)
from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    Consumable,
    ContainerPackagedMedicine,
    DoseQuantity,
    FormCode,
    Ingredient,
    Period,
    PrescribedDose,
    RateQuantity,
    SubstanceAdministration,
)


@pytest.fixture
def substance_administration_1():
    return SubstanceAdministration(
        barcode="123456789",
        status_code="Active",
        period=Period(value="1", unit="wk"),
        dose_quantity=DoseQuantity(low_value="10", low_unit="mg", high_value="20", high_unit="mg"),
        rate_quantity=RateQuantity(value="5", unit="ml/hr"),
        consumable=Consumable(
            barcode="med_barcode_1",
            name="Sample Medicine",
            form_code=FormCode(
                code="123",
                code_system="ABC",
                code_system_name="Sample",
                display_name="Tablet",
                translation="abc",
            ),
            ingredient=Ingredient(
                code="456",
                code_system_name="XYZ",
                display_name="Sample Ingredient",
                name="Ingredient A",
            ),
            container_packaged_medicine=ContainerPackagedMedicine(
                name="Sample Container",
                package_code="789",
                package_display_name="Box",
                capacity="10",
            ),
        ),
        prescribed_dose=PrescribedDose(value="15", unit="2"),
    )


@pytest.fixture
def substance_administration_2():
    return SubstanceAdministration(
        barcode="987654321",
        status_code="Inactive",
        period=Period(value=1, unit="wk"),
        dose_quantity=DoseQuantity(low_value="5", low_unit="mg", high_value="10", high_unit="mg"),
        rate_quantity=RateQuantity(value="3", unit="ml/hr"),
        consumable=Consumable(
            barcode="med_barcode_2",
            name="Another Medicine",
            form_code=FormCode(
                code="456",
                code_system="DEF",
                code_system_name="AnotherSample",
                display_name="Capsule",
                translation="defg",
            ),
            ingredient=Ingredient(
                code="789",
                code_system_name="LMN",
                display_name="Another Ingredient",
                name="Ingredient B",
            ),
            container_packaged_medicine=ContainerPackagedMedicine(
                name="Another Container",
                package_code="321",
                package_display_name="Bottle",
                capacity="20 capsules",
            ),
        ),
        prescribed_dose=PrescribedDose(value="8", unit="3"),
    )


@pytest.fixture
def clinical_document(substance_administration_1: SubstanceAdministration) -> ClinicalDocument:
    return ClinicalDocument(
        barcode="987654321",
        effective_time=EffectiveTime(since="2020-01-01T00:00:00Z", until="2020-12-31T23:59:"),
        section=Section(
            barcode=None,
            text=None,
            summary=Summary(
                contains_high_cost_drug=False, contains_desensitization_vaccine=True, medical_report_required=False
            ),
            substance_administrations=[substance_administration_1],
        ),
        custodian=None,
        doctor_visit=None,
        patient_role=None,
        author=None,
        legal_authenticator=None,
    )
