import datetime
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple

from PyPDF2 import PdfReader
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from seleniumpagefactory import PageFactory

from src.autoscription.core.logging import Monitoring


def delete_mismatched_files(download_dir: Path, monitoring: Monitoring) -> None:
    # Define the regex pattern for the file name
    pattern = re.compile(r"^\d{13}_\d+\.pdf$")

    # Iterate through the files in the directory
    for filename in os.listdir(download_dir):
        # Check if the file name matches the pattern
        if not pattern.match(filename):
            # If the file name doesn't match the pattern, delete the file
            file_path = os.path.join(download_dir, filename)
            # Check if the file has a .pdf extension
            if file_path.lower().endswith(".pdf"):
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        monitoring.logger_adapter.warning(f"A file has been deleted : {file_path}")
                except Exception as e:
                    monitoring.logger_adapter.error(f"Failed to delete {file_path}. Reason: {e}")


def extract_ps_id(text: str) -> str:
    end = text.find("ΘΕΡΑΠΕΙΑ :")
    result = str(text[:end][-17:]).replace(" ", "_")
    if result.replace("_", "").isdigit():
        return result
    else:
        end = text.find("ΕΠΑΝΑΛΗΨΗ :")
        return str(text[:end][-17:]).replace(" ", "_")


def extract_text(file_name: str) -> Tuple[int, str]:
    reader = PdfReader(file_name)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return len(reader.pages), text


def wait_for_file_download(download_dir: Path, filename: str, timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(os.path.join(download_dir, filename)):
            # Check if the file is still being downloaded
            if not os.path.exists(os.path.join(download_dir, filename + ".crdownload")):
                return True
        time.sleep(3)
    return False


def move_ps_list(path: Path, date: str, monitoring: Monitoring) -> None:
    """Moves prescription to directory."""
    download_path = path / "executions" / date / "idika"
    if wait_for_file_download(download_path, "PrescriptionList.xls"):
        Path(download_path / "PrescriptionList.xls").replace(download_path / f"PL_{date}.xls")
    else:
        monitoring.logger_adapter.error(f'Could not rename the xls file to "PL_{date}.xls".')


def rename_ps(path: Path, ps_id: str, monitoring: Monitoring) -> None:
    """Renames prescription."""
    download_path = path
    if wait_for_file_download(download_path, "Prescription.pdf"):
        time.sleep(1)
        ps_id = extract_ps_id(extract_text((download_path / "Prescription.pdf").as_posix())[1])
        (ps_id.replace("/", "").replace("\n", "").replace("\\", ""))
        Path(download_path / "Prescription.pdf").replace(download_path / f"{ps_id}.pdf")
    else:
        time.sleep(3)
        delete_mismatched_files(download_path, monitoring=monitoring)  # noqa: F821
        monitoring.logger_adapter.warning(f"Could not rename the pdf prescription file to {ps_id}.pdf")


class SearchPage(PageFactory):  # type: ignore[misc]
    def __init__(self, driver: WebDriver, date: datetime.date) -> None:
        super().__init__()
        self.driver = driver

        self.driver.get(
            "https://www.e-prescription.gr/e-pre/faces"
            + "/mainPharmacistFlow/SearchPrescription"
            + f"?_adf.ctrl-state={self.get_control_state()}"
        )
        self.date = date.strftime("%d/%m/%Y")
        self.date_ = date.strftime("%d/%m/%Y").replace("/", "_")
        self.date_asc = date.strftime("%Y%m%d")
        self.wait: WebDriverWait = WebDriverWait(driver, 30)

    locators = {
        "search_button": ("ID", "pt1:cb1"),
        "export_to_excel_button": ("ID", "pt1:cb2"),
        "search_from": ("ID", "pt1:id3::content"),
        "search_to": ("ID", "pt1:id1::content"),
        "search_table_row": (
            "XPATH",
            '//*[@id="pt1:t1::db"]/table' + "/tbody/tr/td[1]",
        ),
        "search_id": ("ID", "pt1:it1::content"),
        "download_button": ("ID", "pt1:ctb1"),
        "download_button_multiple": ("ID", "pt1:ctb3"),
    }

    def return_to_search(self) -> None:
        self.driver.get(
            "https://www.e-prescription.gr/e-pre/faces/"
            + "mainPharmacistFlow/SearchPrescription"
            + f"?_adf.ctrl-state={self.get_control_state()}"
        )

    def get_control_state(self) -> str:
        return str(self.driver.current_url.split("state=")[-1].split("&")[0])

    def search(self, monitoring: Monitoring) -> None:
        if self.search_button.get_attribute("innerText") == "Αναζήτηση":
            self.wait.until(ec.element_to_be_clickable(self.search_button))
            self.search_button.click()
        else:
            monitoring.logger_adapter.error("Search button not available")
            raise Exception

    def export_to_excel(self, path: Path, monitoring: Monitoring) -> None:
        if self.export_to_excel_button.get_attribute("innerText") == "Εξαγωγή σε excel":
            self.wait.until(ec.element_to_be_clickable(self.export_to_excel_button))
            self.export_to_excel_button.click()
            move_ps_list(path, self.date_asc, monitoring=monitoring)
        else:
            monitoring.logger_adapter.error("Exception: could not download the excel summary file")
            raise Exception

    def set_search_from(self, v: str) -> None:
        # self.search_from.click()
        # Select all pre-existing text/input value
        self.search_from.send_keys(Keys.CONTROL, "a")
        self.search_from.send_keys(Keys.BACKSPACE)
        self.search_from.send_keys(v)

    def set_search_to(self, v: str) -> None:
        # Select all pre-existing text/input value
        self.search_to.send_keys(Keys.CONTROL, "a")
        self.search_to.send_keys(Keys.BACKSPACE)
        self.search_to.send_keys(v)

    def clear_search_to(self) -> None:
        self.search_to.send_keys(Keys.CONTROL, "a")
        self.search_to.send_keys(Keys.BACKSPACE)

    def set_prescription(self, ps_id: str) -> None:
        self.search_id.send_keys(Keys.CONTROL, "a")
        self.search_id.send_keys(Keys.BACKSPACE)
        self.search_id.send_keys(ps_id)

    def get_prescription_info(self) -> None:
        self.wait.until(ec.element_to_be_clickable(self.search_table_row))
        self.search_table_row.click()

    def download_prescription_pdf(self, path: Path, ps_id: str, monitoring: Monitoring) -> None:
        try:
            if self.download_button.get_attribute("innerText") == "Εκτύπωση Συνταγής":
                self.wait.until(ec.element_to_be_clickable(self.download_button))
                self.download_button.click()
                rename_ps(path, ps_id, monitoring=monitoring)
        except Exception as e:
            monitoring.logger_adapter.error("Εκτύπωση συνταγής button does not exist")
            monitoring.logger_adapter.exception(e)
            raise Exception

    def download_button_multiple_exists(self) -> bool:
        try:
            self.wait.until(ec.element_to_be_clickable(self.driver.find_element(By.ID, "pt1:ctb3")))
            self.driver.find_element(By.ID, "pt1:ctb3")
            return True
        except NoSuchElementException:
            return False

    # def download_multi_prescriptions(self, ps_id, date):
    #     row_id = 0
    #     attempts = 10
    #     while attempts > 0:
    #         attempts = self.download_prescription(ps_id, row_id, date)
    #         row_id += 1

    def download_multi_prescriptions(
        self, path: Path, ps_id: str, date: str, monitoring: Monitoring
    ) -> List[Dict[str, str]]:  # noqa: C901
        self.wait.until(ec.element_to_be_clickable(self.download_button_multiple))
        self.download_button_multiple.click()
        self.wait.until(ec.visibility_of_element_located((By.ID, "t1::db")))
        # TODO: move locators to locators section. Dont use driver
        table = self.driver.find_element(By.ID, "t1::db")
        rows = table.find_elements(By.TAG_NAME, "tr")
        execution_timestamps = []
        counter = 0
        for row in rows:
            timestamp = row.find_elements(By.TAG_NAME, "td")[1].text
            col_date = timestamp.split(" ")[0]
            if col_date == date:
                execution_timestamps.append(
                    {
                        "prescription": ps_id,
                        "multi_pr_timestamp": f"{timestamp[:6]}20{timestamp[6:]}",
                        "execution": row.find_elements(By.TAG_NAME, "td")[0].text,
                    }
                )
                counter += 1
        for row in rows:
            col_date = row.find_elements(By.TAG_NAME, "td")[1].text.split(" ")[0]
            if col_date == date:
                row.click()
                self.wait.until(ec.element_to_be_clickable((By.ID, "ctb5")))
                self.driver.find_element(By.ID, "ctb5").click()
                rename_ps(path, ps_id=ps_id, monitoring=monitoring)
        if counter == 2:
            self.wait.until(ec.element_to_be_clickable(self.download_button_multiple))
            self.download_button_multiple.click()
            self.wait.until(ec.visibility_of_element_located((By.ID, "t1::db")))
            table = self.driver.find_element(By.ID, "t1::db")
            rows = table.find_elements(By.TAG_NAME, "tr")
            rows.reverse()
            for row in rows:
                col_date = row.find_elements(By.TAG_NAME, "td")[1].text.split(" ")[0]
                if col_date == date:
                    row.click()
                    self.wait.until(ec.element_to_be_clickable((By.ID, "ctb5")))
                    self.driver.find_element(By.ID, "ctb5").click()
                    rename_ps(path, ps_id=ps_id, monitoring=monitoring)
        elif counter == 3:
            self.wait.until(ec.element_to_be_clickable(self.download_button_multiple))
            self.download_button_multiple.click()
            self.wait.until(ec.visibility_of_element_located((By.ID, "t1::db")))
            table = self.driver.find_element(By.ID, "t1::db")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:
                col_date = row.find_elements(By.TAG_NAME, "td")[1].text.split(" ")[0]
                if col_date == date:
                    row.click()
                    self.wait.until(ec.element_to_be_clickable((By.ID, "ctb5")))
                    self.driver.find_element(By.ID, "ctb5").click()
                    rename_ps(path, ps_id=ps_id, monitoring=monitoring)
        return execution_timestamps
