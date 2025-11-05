import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from cryptography import x509


def __get_valid_certificates(certifi_pem_content: str) -> str:
    certificates = __split_certificates(certifi_pem_content)
    valid_certificates = [cert for cert in certificates if __is_certificate_valid(cert)]
    return "\n".join(valid_certificates)


def __split_certificates(cert_data: str) -> List[str]:
    # Split certificates based on the delimiter "-----END CERTIFICATE-----"
    delimiter = "-----END CERTIFICATE-----"
    certificates_without_delimiter = cert_data.strip().split(delimiter)
    certificates = [str(cert + delimiter) for cert in certificates_without_delimiter if cert != ""]
    return certificates


def __is_certificate_valid(certificate: str) -> bool:
    cert = x509.load_pem_x509_certificate(certificate.encode())
    expiration_date = cert.not_valid_after
    days_remaining = (expiration_date - datetime.now()).days
    if days_remaining > 0:
        return True
    else:
        return False


def __save_file(data: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        file.write(data)


def use_combined_certs(root_directory: Path) -> None:
    if sys.platform == "win32":
        combined_certs_path = root_directory / "certs" / "combined_certs.pem"
        import certifi_win32

        certifi_win32.generate_pem()
        certifi_pem = certifi_win32.wincerts.where()
        requests_certs = requests.certs.where()  # type: ignore[attr-defined]
        with open(requests_certs, "r") as requests_certs_file:
            requests_certs_content = requests_certs_file.read()
            with open(certifi_pem, "r") as certifi_pem_file:
                certifi_pem_content = certifi_pem_file.read()
                valid_certifi_pem_content = __get_valid_certificates(certifi_pem_content)
                combined_certs = valid_certifi_pem_content + requests_certs_content
                __save_file(combined_certs, combined_certs_path)
        os.environ["REQUESTS_CA_BUNDLE"] = combined_certs_path.as_posix()
