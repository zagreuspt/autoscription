from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from seleniumpagefactory import PageFactory

from src.autoscription.core.errors import SignInException
from src.autoscription.core.logging import Monitoring


class Dashboard(PageFactory):  # type: ignore[misc]
    def __init__(self, driver: WebDriver) -> None:
        super().__init__()
        self.driver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 30)

    locators = {
        "select_button": ("ID", "pt1:cb2"),
        "search_prescription_button": ("XPATH", "//div[@id='pt1:searchPrescriptionBtn']/a"),
    }

    def select_pharmacy(self, monitoring: Monitoring) -> None:
        try:
            self.wait.until(ec.element_to_be_clickable(self.select_button))
            self.select_button.click()
        except Exception as e:
            monitoring.logger_adapter.exception(e)
            monitoring.logger_adapter.error(
                "Could not login. Either idika password is " + "wrong or expired. Please change the password."
            )
            raise SignInException()

    def select_search_prescription(self, monitoring: Monitoring) -> None:
        try:
            self.wait.until(ec.element_to_be_clickable(self.search_prescription_button))
            self.search_prescription_button.click()
        except Exception as e:
            monitoring.logger_adapter.exception(e)
            monitoring.logger_adapter.error(
                "Could not find prescription button. Select_search_prescription function failed"
            )
