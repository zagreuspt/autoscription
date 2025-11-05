from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from seleniumpagefactory import PageFactory

from src.autoscription.core.logging import Monitoring


class SignInPage(PageFactory):  # type: ignore[misc]
    def __init__(self, driver: WebDriver) -> None:
        super().__init__()
        self.driver = driver
        self.driver.get("https://www.e-prescription.gr/e-pre/faces/welcome")
        self.wait: WebDriverWait = WebDriverWait(driver, 30)

    locators = {
        "close_cookies_button": ("CSS", "a.cc-dismiss"),
        "username_input": ("NAME", "username"),
        "password_input": ("NAME", "password"),
        "submitButton": ("ID", "buttonSubmit"),
    }

    # TODO: pass monitoring on init
    def close_cookies(self, monitoring: Monitoring) -> None:
        try:
            self.wait.until(ec.element_to_be_clickable(self.close_cookies_button))
            self.close_cookies_button.click()
        except Exception as e:
            monitoring.logger_adapter.warning("Timeout on cookies:")
            monitoring.logger_adapter.warning(e)

    def set_username(self, username: str) -> None:
        self.username_input.send_keys(username)

    def set_password(self, password: str) -> None:
        self.password_input.send_keys(password)

    def click_submit(self) -> None:
        self.wait.until(ec.element_to_be_clickable(self.submitButton))
        self.submitButton.click()
