from datetime import datetime
from pathlib import Path

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

from src.autoscription.idika_client.mapping.clinical_document_mt import (
    map_clinical_document,
)
from src.autoscription.idika_client.model.idika.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument as ClinicalDocumentMt,
)


def test_mapper_against_sample():
    xml_string = Path("test/autoscription/idika_client/clinical_document_sample.xml").read_text("UTF-8")
    config = ParserConfig(fail_on_unknown_properties=False, fail_on_converter_warnings=True)
    parser = XmlParser(config=config)
    clinical_document = parser.from_string(xml_string, ClinicalDocument)
    clinical_document_mt: ClinicalDocumentMt = map_clinical_document(clinical_document)

    # for troubleshooting
    # def datetime_serializer(obj):
    #     if isinstance(obj, datetime.datetime):
    #         return obj.isoformat()
    #     raise TypeError(f"Type {type(obj)} not serializable")
    # data: str = json.dumps(dataclasses.asdict(clinical_document_mt), ensure_ascii=False, default=datetime_serializer)
    # Path("test.json").write_text(data=data, encoding="utf-8")

    assert clinical_document_mt.barcode == "1111111111111"
    assert clinical_document_mt.section.substance_administrations[0].barcode == "21899392"
    assert clinical_document_mt.section.substance_administrations[0].status_code == "active"
    assert clinical_document_mt.section.substance_administrations[0].dose_quantity.low_value == "1"
    assert clinical_document_mt.section.substance_administrations[0].dose_quantity.low_unit == "ΟΦΘ.ΣΤΑΓΟΝΕΣ_ΔΟΣΕΙΣ"
    assert clinical_document_mt.section.substance_administrations[0].dose_quantity.high_value == "1"
    assert clinical_document_mt.section.substance_administrations[0].dose_quantity.high_unit == "ΟΦΘ.ΣΤΑΓΟΝΕΣ_ΔΟΣΕΙΣ"
    assert clinical_document_mt.section.substance_administrations[0].rate_quantity.value == "4"
    assert clinical_document_mt.section.substance_administrations[0].rate_quantity.unit == "d"
    assert clinical_document_mt.section.substance_administrations[0].prescribed_dose.value == "5"
    assert clinical_document_mt.section.substance_administrations[0].prescribed_dose.unit == "1"
    consumable = clinical_document_mt.section.substance_administrations[0].consumable
    assert consumable.barcode == "2802578001025"
    assert consumable.name == "URPEM EY.DR.S.SD 0,1mg/0,4ML BTX20X0,4ML"
    assert consumable.form_code.code == "EY.DR.S.SD"
    assert consumable.form_code.code_system == "1.3.6.1.4.1.12559.11.10.1.3.1.44.1"
    assert consumable.form_code.code_system_name == "EDQM"
    assert consumable.form_code.display_name == "EY.DR.S.SD"
    assert consumable.form_code.translation == "ΟΦΘ.ΣΤΑΓΟΝΕΣ_ΔΟΣΕΙΣ"
    ingredient = clinical_document_mt.section.substance_administrations[0].consumable.ingredient
    assert ingredient.code == "34580148"
    assert ingredient.code_system_name == "EOF"
    assert ingredient.display_name == "KETOTIFEN FUMARATE"
    assert ingredient.name == "KETOTIFEN FUMARATE"
    prescribed_dose = clinical_document_mt.section.substance_administrations[0].prescribed_dose
    assert prescribed_dose.value == "5"
    assert prescribed_dose.unit == "1"
