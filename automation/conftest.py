"""
Shared pytest fixtures.

They handle the browser, the API client and the balance reset, so the tests themselves
only contain test steps and checks.

Set HEADLESS=1 to run the browser without a visible window, for example in CI.
"""
import json
import os

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from api.client import BettingApiClient


ALLURE_CATEGORIES = [
    {
        "name": "Product defects (deviation from specification)",
        "matchedStatuses": ["failed"],
        "messageRegex": "(?s).*expected.*",
    },
    {
        "name": "Test or environment errors",
        "matchedStatuses": ["broken"],
    },
]


def pytest_sessionfinish(session):
    """Write categories.json so Allure groups failures by type, without knowing any defect IDs."""
    results_dir = session.config.getoption("allure_report_dir", None)
    if results_dir and os.path.isdir(results_dir):
        with open(os.path.join(results_dir, "categories.json"), "w", encoding="utf-8") as f:
            json.dump(ALLURE_CATEGORIES, f, indent=2)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    drv = item.funcargs.get("driver")
    if report.when == "call" and report.failed and drv is not None:
        allure.attach(
            drv.get_screenshot_as_png(),
            name="screenshot-on-failure",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "").lower() in ("1", "true"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    yield drv
    drv.quit()


@pytest.fixture
def api_client():
    return BettingApiClient()


@pytest.fixture
def reset_balance(api_client):
    """
    Resets the balance with POST /api/reset-balance before and after each test
    (the live app currently resets it to €120.00). This way the tests don't depend
    on each other or on the order they run in.
    """
    api_client.reset_balance()
    yield
    api_client.reset_balance()
