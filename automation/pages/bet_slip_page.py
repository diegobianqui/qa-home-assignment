import re
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class BetSlipPage(BasePage):
    """Page object for the bet slip, the header balance and the bet receipt."""

    RECEIPT_HEADING_TEXT = "Bet Placed Successfully!"

    BET_SLIP_TITLE = (By.ID, "bet-slip-title")
    BALANCE_DISPLAY = (By.ID, "header-balance")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    REMOVE_ALL_BUTTON = (By.ID, "bet-slip-selection-remove")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")

    def enter_stake(self, amount: str):
        el = self.find(self.STAKE_INPUT)
        el.clear()
        el.send_keys(amount)
        self.wait.until(lambda d: d.find_element(*self.STAKE_INPUT).get_attribute('value') == amount)
        self.wait.until(lambda d: not d.find_element(*self.PLACE_BET_BUTTON).get_attribute('disabled'))
        return self

    def current_balance(self) -> float:
        raw = self.text_of(self.BALANCE_DISPLAY)
        match = re.search(r"(\d+(?:\.\d+)?)", raw)
        if not match:
            raise ValueError(f"Could not parse balance from text: {raw!r}")
        return float(match.group(1))

    def place_bet(self):
        self.wait.until(lambda d: not d.find_element(*self.PLACE_BET_BUTTON).get_attribute('disabled'))
        button = self.find(self.PLACE_BET_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()
        return self

    def wait_for_receipt(self, timeout: int = 10) -> str:
        """Waits for the success receipt and returns its text."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.RECEIPT_HEADING_TEXT in d.find_element(By.TAG_NAME, "body").text
        )
        body = self.driver.find_element(By.TAG_NAME, "body").text
        return body[body.find(self.RECEIPT_HEADING_TEXT):]

    def wait_for_balance_change(self, balance_before: float, timeout: int = 10) -> float:
        """
        Waits up to `timeout` seconds for the header balance to differ from
        `balance_before` and returns the displayed balance. If it never changes, the
        unchanged value is returned so that the calling test's assertion decides the
        verdict, instead of the page object raising an error.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.current_balance() != balance_before
            )
        except TimeoutException:
            pass
        return self.current_balance()
