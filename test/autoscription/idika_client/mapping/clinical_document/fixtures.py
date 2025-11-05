import pytest

from src.autoscription.idika_client.model.idika.clinical_document import (
    Act,
    AsContent,
    AssignedAuthor,
    Author,
    CapacityQuantity,
    ClinicalDocument,
    Code1,
    Code2,
    Component,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    Consumable as ConsumableIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    ContainerPackagedMedicine,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    DoseQuantity as DoseQuantityIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    EffectiveTime as EffectiveTimeIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    Entry,
    EntryRelationship,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    FormCode as FormCodeIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import High, Id
from src.autoscription.idika_client.model.idika.clinical_document import (
    Ingredient as IngredientIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    Item,
    ListType,
    Low,
    ManufacturedMaterial,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    ManufacturedProduct as ManufacturedProductIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import OriginalText
from src.autoscription.idika_client.model.idika.clinical_document import (
    Period as PeriodIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import Quantity1
from src.autoscription.idika_client.model.idika.clinical_document import (
    RateQuantity as RateQuantityIdika,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    Reference,
    Section,
    StatusCode,
    StructuredBody,
    SubstanceAdministration,
    Supply,
    Text,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    Translation as TranslationIdika,
)


@pytest.fixture
def manufactured_material():
    return ManufacturedMaterial(
        code=Code1("code", original_text=OriginalText(reference=Reference(value="#ref_id"))),
        name="material_name",
        form_code=FormCodeIdika(
            code="form_code",
            code_system="system",
            code_system_name="system_name",
            display_name="display",
            translation=TranslationIdika(display_name="translation"),
        ),
        ingredient=IngredientIdika(
            code=Code2(
                code="1111",
            ),
            ingredient=IngredientIdika(
                code=Code2(
                    code="121",
                    code_system_name="system_name",
                    display_name="display_name",
                ),
                name="ingredient_name",
            ),
        ),
        as_content=AsContent(
            container_packaged_medicine=ContainerPackagedMedicine(
                name="test_name",
                form_code=FormCodeIdika(code="1234", display_name="BTX200"),
                capacity_quantity=CapacityQuantity(value="12"),
            )
        ),
    )


@pytest.fixture
def substance_administration(manufactured_material):
    return SubstanceAdministration(
        id=Id(root="1.21.1", extension="barcode_value"),
        status_code=StatusCode("status"),
        dose_quantity=DoseQuantityIdika(low=Low(value="1", unit="mg"), high=High(value="1", unit="mg")),
        rate_quantity=RateQuantityIdika(low=Low(value="1", unit="mg"), high=High(value="1", unit="mg")),
        consumable=ConsumableIdika(
            manufactured_product=ManufacturedProductIdika(manufactured_material=manufactured_material)
        ),
        effective_time=[EffectiveTimeIdika(), EffectiveTimeIdika(period=PeriodIdika(value="1", unit="d"))],
        entry_relationship=[EntryRelationship(supply=Supply(quantity=Quantity1(value="5", unit="4")))],
    )


@pytest.fixture
def section(substance_administration):
    return Section(
        entry=[
            Entry(
                act=Act(
                    id=[
                        Id(root="1.1.7", extension="0"),
                        Id(root="1.1.8", extension="1"),
                        Id(root="1.1.23", extension="0"),
                    ]
                )
            ),
            Entry(substance_administration=substance_administration),
        ],
        text=Text(list_value=ListType(item=[Item(id="ref_id", value="")])),
    )


@pytest.fixture
def clinical_document(section):
    return ClinicalDocument(
        id=Id(root="1.21", extension="1233243"),
        effective_time=EffectiveTimeIdika(low=Low(value="10"), high=High(value="20")),
        author=Author(
            assigned_author=AssignedAuthor(
                id=[Id(root="1.19.1", extension="specialty_id"), Id(root="1.19.2", extension="specialty_name")]
            )
        ),
        component=Component(structured_body=StructuredBody(Component(section=section))),
    )
