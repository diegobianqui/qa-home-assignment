"""
Base Page Object: shared explicit-wait helpers so individual page objects stay
declarative (locators + actions) rather than repeating WebDriverWait boilerplate.

The page layer centralizes Selenium wait behavior so the tests can focus on the
business flow instead of timing and synchronization details.
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import DEFAULT_TIMEOUT


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def text_of(self, locator):
        return self.find(locator).text

    def is_visible(self, locator, timeout: int | None = None) -> bool:
        try:
            WebDriverWait(self.driver, timeout or DEFAULT_TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
