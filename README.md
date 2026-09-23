# Sports Betting QA: Single Bet Placement

My solution to the QA home assignment. I tested the Single Bet Placement feature of
https://qae-assignment-tau.vercel.app manually and wrote a small automation framework with
one UI test and one API test.

The assignment brief (`HQA_Take_Home_Task.pdf`) and the feature spec
(`Feature_Specification.pdf`) aren't included in this repo. I refer to them by name only.

## What's in here

| Part | Where |
|---|---|
| A1: Test plan (6 prioritised scenarios) | [docs/test-plan.md](docs/test-plan.md) |
| A2: Execution results and bug reports | [docs/execution-results.md](docs/execution-results.md) |
| B: Automation (1 UI + 1 API test) | [automation/](automation/) |
| C: Test strategy and recommendations | [docs/strategy-and-recommendations.md](docs/strategy-and-recommendations.md) |
| Screenshots and test run output | [docs/evidence/](docs/evidence/) |

## Short summary

I ran the top three scenarios plus a short exploratory session and found 7 bugs. The most
serious ones are on the API side: it accepts a stake above the balance (the balance goes
negative) and it accepts negative stakes. The receipt also shows the wrong payout and team
order, and the header balance doesn't update after a bet. Details are in
[execution-results.md](docs/execution-results.md).

## Running the tests

You need Python 3.10 or newer and Google Chrome. The matching ChromeDriver is downloaded
automatically.

```bash
cd automation
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then set USER_ID to your user id
```

Run these from the `automation/` folder:

| What | Command |
|---|---|
| All tests | `pytest` |
| All tests, no browser window | `HEADLESS=1 pytest` |
| UI test only | `pytest -m e2e` |
| API test only | `pytest -m api` |
| Allure report | `pytest --alluredir=allure-results`, then `allure serve allure-results` |

The Allure report is optional and needs the Allure command line tool installed separately.

### Expected result: both tests fail

This is on purpose. Both tests catch real bugs in the app:

- the UI test fails on BUG-06 (wrong payout), BUG-07 (team order) and BUG-01 (balance not refreshed)
- the API test fails on BUG-02 (stake above balance accepted)

Each failure message starts with the bug ID, so you can find it in the bug reports. Once
the bugs are fixed, the tests should pass. Example output:
[docs/evidence/pytest-run.txt](docs/evidence/pytest-run.txt).

## How the automation is organised

```
automation/
  config/settings.py   base URL, user id, timeouts
  pages/               page objects for the matches list and bet slip
  api/client.py        small wrapper around the betting API
  tests/               the two tests
  conftest.py          pytest fixtures
  pytest.ini           markers (e2e, api, critical) and default options
  requirements.txt     pinned dependencies
  .env.example         template for your user id
```

I kept three layers apart: configuration, the page objects and API client, and the tests.
If a locator or endpoint changes, only one file needs updating and the tests stay readable.

Fixtures in `conftest.py`:
- `driver` starts Chrome (headless if `HEADLESS=1`) and always closes it
- `api_client` returns an API client for your user id
- `reset_balance` resets the balance before and after each test, so tests don't depend on each other

Why these two tests were picked is explained in the docstring of each test and in the
[test strategy, section 11](docs/strategy-and-recommendations.md#11-automation-approach).

## Tools used

The brief asks for Python, Selenium, pytest and requests. I also added:

| Tool | Why |
|---|---|
| webdriver-manager | Downloads the right ChromeDriver so there's no manual setup |
| python-dotenv | Reads `USER_ID` from `.env`, so it stays out of the code |
| allure-pytest | Optional HTML report |

## Known limitations

- The app is a shared environment and the balance is stored per user id. Don't run the tests in parallel with the same user id.
- The UI test uses the first match card (Manchester Utd vs Chelsea, HOME 2.45). If the match list changes, update the test data at the top of the test file.
- The app is live and could change after this was written, so results may differ from the ones recorded here.
