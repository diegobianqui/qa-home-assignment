from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.settings import APP_URL


class MatchesPage(BasePage):
    """Live selectors for the real match list and odds buttons."""

    MATCHES_CONTAINER = (By.ID, "match-section")
    MATCH_CARD = (By.CSS_SELECTOR, ".matchCard")
    ODDS_BUTTONS = (By.CSS_SELECTOR, ".matchCard .oddsButton")

    def load(self):
        self.driver.get(APP_URL)
        self.wait.until(lambda d: len(d.find_elements(*self.MATCH_CARD)) >= 1)
        return self

    def select_first_match_home_odds(self):
        """Clicks the first available home odds button from the first visible match card."""
        card = self.find(self.MATCH_CARD)
        odds = card.find_elements(*self.ODDS_BUTTONS)
        if not odds:
            raise AssertionError("No odds buttons were found inside the first match card.")
        odds[0].click()
        return self
