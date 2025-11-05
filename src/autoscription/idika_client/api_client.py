from __future__ import annotations

import base64
from datetime import datetime
from typing import Optional

import requests
import xmltodict
from requests.adapters import HTTPAdapter, Retry
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

from src.autoscription.core.errors import (
    IdikaAuthenticationException,
    IdikaPharmacyNotSelectedException,
    IdikaWrongStatusCodeException,
    XmlParsingException,
)
from src.autoscription.idika_client.mapping.clinical_document_mt import (
    map_clinical_document,
)
from src.autoscription.idika_client.mapping.partial_clinical_document import (
    map_partial_clinical_document,
)
from src.autoscription.idika_client.mapping.pharmacist_unit import map_pharmacist_units
from src.autoscription.idika_client.model.idika.clinical_document import (
    ClinicalDocument as IdikaClinicalDocument,
)
from src.autoscription.idika_client.model.idika.partial_clinical_document import (
    PartialClinicalDocument as IdikaPartialClinicalDocument,
)
from src.autoscription.idika_client.model.idika.pharmacist_units import (
    PharmacistUnitsResponse,
)
from src.autoscription.idika_client.model.mt.clinical_document.clinical_document import (
    ClinicalDocument,
)
from src.autoscription.idika_client.model.mt.partial_clinical_document import (
    PartialClinicalDocument,
)
from src.autoscription.idika_client.model.mt.pharmacist_unit import PharmacistUnit


def _create_headers(api_token: str, password: str, username: str) -> dict[str, str]:
    credentials = f"{username.lower()}:{password}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {credentials_base64}",
        "api-key": api_token,
        "Accept": "application/x-hl7, application/xml",
        "Content-Type": "application/xml",
    }


class IdikaHttpClient:
    session: requests.Session
    headers: dict[str, str]

    def __init__(self, base_url: str, api_key: str, username: str, password: str):
        self.base_url = base_url
        self.headers = _create_headers(api_key, password, username)
        self.session = requests.Session()
        retry = Retry(total=5, backoff_factor=1, backoff_jitter=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount(self.base_url, HTTPAdapter(max_retries=retry, pool_connections=20))

    def get_clinical_document(self, pharmacy_id: int, barcode: str) -> requests.Response:
        url_end = f"pharmacistapi/api/v1/prescriptions/get/{barcode}"
        params = {"pharmacyId": pharmacy_id}
        return self.session.get(f"{self.base_url}/{url_end}", headers=self.headers, params=params)

    def get_partial_clinical_document(self, pharmacy_id: int, barcode: str, execution: int) -> requests.Response:
        url_end = f"pharmacistapi/api/v1/prescriptions/get/{barcode}/dispensation/{execution}"
        params = {"pharmacyId": pharmacy_id}
        return self.session.get(f"{self.base_url}/{url_end}", headers=self.headers, params=params)

    def get_pharmacist_units(self) -> requests.Response:
        url_end = "pharmacistapi/api/v1/user/me/units"
        return self.session.get(f"{self.base_url}/{url_end}", headers=self.headers)

    def authenticate(self) -> requests.Response:
        url_end = "pharmacistapi/api/v1/user/me"
        return self.session.get(f"{self.base_url}/{url_end}", headers=self.headers)


TOKEN_EXPIRED_OR_PERMISSIONS_MISSING = 403


class IdikaAPIClient:
    pharmacy_id: Optional[int] = None
    _xml_parser: XmlParser

    def __init__(self, idika_http_client: IdikaHttpClient) -> None:
        self.idika_http_client = idika_http_client
        self._xml_parser = XmlParser(
            config=ParserConfig(
                fail_on_converter_warnings=True,  # used to identify errors in conversion
                fail_on_unknown_properties=False,  # used in case a new element is introduced
            )
        )

    def get_clinical_document(self, barcode: str) -> ClinicalDocument:
        if self.pharmacy_id is None:  # no authentication took place
            raise IdikaPharmacyNotSelectedException()
        response = self.idika_http_client.get_clinical_document(
            pharmacy_id=self.pharmacy_id,  # type: ignore[arg-type]   # authenticate sets _pharmacy_id
            barcode=barcode,
        )
        if (
            response.status_code == TOKEN_EXPIRED_OR_PERMISSIONS_MISSING
        ):  # TODO: how is the token refreshed? by calling /user/me not by retrieving the new pharmacy_id
            self.authenticate()
            response = self.idika_http_client.get_clinical_document(
                pharmacy_id=self.pharmacy_id,  # type: ignore[arg-type]  # authenticate sets pharmacy_id
                barcode=barcode,
            )
        if response.status_code != 200:
            raise IdikaWrongStatusCodeException(
                expected_status=200,
                actual_status=response.status_code,
                arguments={"barcode": barcode},
                response=response.text,
            )
        try:
            clinical_document = self._xml_parser.from_string(response.text, IdikaClinicalDocument)
        except ParserError as e:
            raise XmlParsingException(e)
        return map_clinical_document(clinical_document)

    def get_partial_clinical_document(self, barcode: str, execution: int) -> PartialClinicalDocument:
        if self.pharmacy_id is None:  # no authentication took place
            raise IdikaPharmacyNotSelectedException()
        response = self.idika_http_client.get_partial_clinical_document(
            pharmacy_id=self.pharmacy_id,  # type: ignore[arg-type]   # authenticate sets _pharmacy_id
            barcode=barcode,
            execution=execution,
        )
        if (
            response.status_code == TOKEN_EXPIRED_OR_PERMISSIONS_MISSING
        ):  # TODO: how is the token refreshed? by calling /user/me not by retrieving the new pharmacy_id
            self.authenticate()
            response = self.idika_http_client.get_partial_clinical_document(
                pharmacy_id=self.pharmacy_id,  # type: ignore[arg-type]  # authenticate sets pharmacy_id
                barcode=barcode,
                execution=execution,
            )
        if response.status_code != 200:
            raise IdikaWrongStatusCodeException(
                expected_status=200,
                actual_status=response.status_code,
                arguments={"barcode": barcode, "execution": str(execution)},
                response=response.text,
            )
        try:
            idika_partial_clinical_document = self._xml_parser.from_string(response.text, IdikaPartialClinicalDocument)
        except ParserError as e:
            raise XmlParsingException(e)
        return map_partial_clinical_document(
            idika_partial_clinical_document=idika_partial_clinical_document, execution=execution
        )

    def authenticate(self) -> int:
        response = self.idika_http_client.authenticate()
        if response.status_code == 200:
            return int(xmltodict.parse(response.text)["User"]["pharmacy"]["id"])
        else:
            raise IdikaAuthenticationException

    def get_pharmacist_units(self) -> list[PharmacistUnit]:
        response = self.idika_http_client.get_pharmacist_units()
        pharmacist_units_response: PharmacistUnitsResponse = self._xml_parser.from_string(
            response.text, PharmacistUnitsResponse
        )
        if response.status_code == 200:
            return map_pharmacist_units(pharmacist_units_response=pharmacist_units_response)
        else:
            raise IdikaAuthenticationException

    def get_active_pharmacist_units(self) -> list[PharmacistUnit]:
        now = datetime.now()
        pharmacist_units: list[PharmacistUnit] = self.get_pharmacist_units()
        return [unit for unit in pharmacist_units if unit.expiry_date > now > unit.start_date]
