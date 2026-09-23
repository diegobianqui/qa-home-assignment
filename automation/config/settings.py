"""
Central configuration for the automation suite.

The base URL and user id are read here once, so they never get hardcoded in page
objects, the API client or the tests.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app").rstrip("/")
USER_ID = os.getenv("USER_ID")

if not USER_ID:
    raise RuntimeError(
        "USER_ID is not set. Copy .env.example to .env and set your assigned user-id."
    )

APP_URL = f"{BASE_URL}/?user-id={USER_ID}"
API_BASE_URL = f"{BASE_URL}/api"

# Business rules from the live application contract observed in execution.
STAKE_MIN = 1.00
STAKE_MAX = 100.00
INITIAL_BALANCE = 120.00

DEFAULT_TIMEOUT = 10  # seconds, for explicit Selenium waits
