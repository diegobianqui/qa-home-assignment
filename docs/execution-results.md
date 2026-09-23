# Execution Results: Single Bet Placement

## Environment

- App: https://qae-assignment-tau.vercel.app (API under `/api`)
- User ID: `candidate-AAaEVUy7qvRT`
- Browser: Google Chrome on macOS, Selenium 4.24.0, 1920x1080
- Before each test the balance was reset with `POST /api/reset-balance`

## Summary

I ran the three highest-priority scenarios from the [test plan](test-plan.md) (TC-01,
TC-02, TC-04), then did a 15-minute exploratory session. TC-04 was checked in both the UI
and the API because the two layers behave differently.

| TC | Title | Result | Bugs |
|---|---|---|---|
| TC-01 | Place a valid single bet | FAIL | BUG-01, BUG-06, BUG-07 |
| TC-02 | Stake at the minimum boundary | PASS | |
| TC-04 | Stake higher than the balance (UI) | PASS | |
| TC-04 | Stake higher than the balance (API) | FAIL | BUG-02 |

I found 7 bugs in total: 2 Critical, 2 High, 3 Medium.

## Test runs

### TC-01: Place a valid single bet (FAIL)

Steps 1 to 4 and step 7 worked as expected. The bet slip preview showed the correct payout
of €24.50.

- **Step 5 failed.** The receipt read: `Bet ID #B-50786, MATCH Chelsea vs Manchester Utd, STAKE €10.00, ODDS 2.45, Potential Payout €20.00`. The payout is wrong (BUG-06) and the teams are the wrong way round (BUG-07).
- **Step 6 failed.** The header still showed the old balance. `GET /api/balance` returned 110, and the header only updated after a page reload (BUG-01).

Evidence: [receipt](evidence/manual/BUG-01_receipt_balance_not_refreshed.png),
[after reload](evidence/manual/BUG-01_balance_after_reload.png), [pytest run](evidence/automated/pytest-run.txt)

### TC-02: Stake at the minimum boundary (PASS)

| Input | Expected | Actual |
|---|---|---|
| UI `0.99` | "Minimum stake is €1.00", button disabled | Same |
| UI `1.00` | No message, button enabled | Same |
| UI `1.01` | No message, button enabled | Same |
| API `0.99` | 422 `invalid_stake_min` | Same |
| API `1.00` | 200, balance down by €1.00 | Same |

This settles the spec conflict: the minimum stake is €1.00.
Evidence: [0.99 blocked](evidence/manual/TC-02_min_stake_0.99_blocked.png)

### TC-04: Stake higher than the balance (UI PASS, API FAIL)

After a €100.00 bet the balance was €20.00, as expected.

- **UI:** entering €50.00 showed "Insufficient balance" and disabled **Place Bet**. Pass.
- **API:** `POST /api/place-bet` with `stake: 50` returned HTTP 200 with `"balance": -30`. The balance went to -€30.00. Fail (BUG-02).

Evidence: [UI blocked](evidence/manual/TC-04_ui_insufficient_balance_blocked.png),
[pytest run](evidence/automated/pytest-run.txt)

### Extra check: TC-03 maximum stake

This is outside the top three, but I checked it quickly. The UI blocks €100.01 with "Maximum
stake is €100.00", and the API returns 422 `invalid_stake_max`. No bug found.
Evidence: [100.01 blocked](evidence/manual/TC-03_max_stake_100.01_blocked.png)

## Exploratory session

**Goal:** try to break validation, payout and balance handling, mostly by calling the API
directly and skipping the UI. Timebox: 15 minutes.

What I found:
- The receipt payout is always stake x 2, whatever the odds (BUG-06).
- The receipt swaps the home and away teams (BUG-07).
- The header balance doesn't refresh after a bet (BUG-01).
- The API accepts a stake above the balance (BUG-02).
- The API accepts a negative stake (BUG-03).
- The place-bet response says `USD`, but `/balance` says `EUR` (BUG-04).
- Reset reports 125.5, but the balance afterwards is 120 (BUG-05).

What worked: `10.999` is rejected with `invalid_stake_precision`, `"10"` and `null` with
`invalid_stake_type`, an unknown match with `invalid_match`, and `100.01` with
`invalid_stake_max`.

## Bug reports

### BUG-01: Header balance doesn't update after placing a bet

- **Severity:** High
- **Found in:** TC-01, step 6

**Reproduction Steps**
1. Reset the balance and open the app.
2. Pick Manchester Utd vs Chelsea, HOME (2.45).
3. Enter `10.00` and click **Place Bet**.
4. Look at the header balance.
5. Call `GET /api/balance`, then reload the page.

**Expected vs Actual**
- Expected: the header drops by €10.00 straight after the bet.
- Actual: the header keeps showing the old balance. The API has the new value (110), and the header only catches up after a reload.

**Business Impact:** Users see the wrong balance. They may place bets they think they can
afford, or contact support thinking the bet failed.

**Evidence:** [receipt](evidence/manual/BUG-01_receipt_balance_not_refreshed.png),
[after reload](evidence/manual/BUG-01_balance_after_reload.png)

### BUG-02: API lets a stake go above the balance (negative balance)

- **Severity:** Critical
- **Found in:** TC-04, API (caught by the automated test)

**Reproduction Steps**
1. Reset the balance.
2. Place a €100.00 bet, which leaves €20.00.
3. Send `POST /api/place-bet` with `stake: 50`.
4. Send `GET /api/balance`.

**Expected vs Actual**
- Expected: HTTP 422, no bet created, and the balance stays at €20.00.
- Actual: HTTP 200 "Bet placed successfully", and the balance is -€30.00.

**Business Impact:** The balance check only exists in the UI. Anyone calling the API
directly can bet money they don't have, which is a direct financial loss.

**Evidence:** [pytest run](evidence/automated/pytest-run.txt)

### BUG-03: API accepts a negative stake

- **Severity:** Critical
- **Found in:** exploratory session

**Reproduction Steps**
1. Reset the balance.
2. Send `POST /api/place-bet` with `matchId` set to the id of the first match returned by `GET /api/matches`, `selection: HOME`, `stake: -5`.
3. Send `GET /api/balance`.

**Expected vs Actual**
- Expected: HTTP 422 `invalid_stake_min`, and the balance doesn't change.
- Actual: HTTP 200 with `payout: -12.25`. The bet is accepted.

**Business Impact:** The minimum stake rule can be bypassed through the API, which opens the
door to balance manipulation.

**Evidence:** API response recorded during the exploratory session. No screenshot, because this is API only.

### BUG-04: Place-bet response uses the wrong currency

- **Severity:** Medium
- **Found in:** exploratory session

**Reproduction Steps**
1. Send `POST /api/place-bet` with a valid stake.
2. Send `GET /api/balance`.

**Expected vs Actual**
- Expected: both responses say `"currency": "EUR"`.
- Actual: place-bet says `"USD"`, while `/balance` says `"EUR"`.

**Business Impact:** Any client or report that reads the currency from the response will show
or reconcile amounts in the wrong currency.

**Evidence:** the response body is quoted in the BUG-02 failure in the [pytest run](evidence/automated/pytest-run.txt). No automated test asserts the currency.

### BUG-05: Reset gives a different balance than the one actually saved

- **Severity:** Medium
- **Found in:** exploratory session

**Reproduction Steps**
1. Send `POST /api/reset-balance`.
2. Send `GET /api/balance`.

**Expected vs Actual**
- Expected: the balance is €125.50 (the starting balance stated in the brief), and both calls agree.
- Actual: the reset response says 125.5, but `GET /api/balance` returns 120.

**Business Impact:** After a reset, users start with €5.50 less than they should. The reset
response also can't be trusted, so test setup has to read `/balance` instead.

**Evidence:** reproduced again on 2026-09-23 with the two calls above (reset returned
`"balance":125.5`, balance returned `"balance":120`).

### BUG-06: Receipt payout is stake x 2 instead of stake x odds

- **Severity:** High
- **Found in:** TC-01, step 5 (caught by the automated test)

**Reproduction Steps**
1. Place a €10.00 bet on HOME at 2.45.
2. Read "Potential Payout" on the receipt.

**Expected vs Actual**
- Expected: €24.50.
- Actual: €20.00. It happens with other values too: 20 at 2.45 shows €40.00 (should be €49.00), and 5 at 3.10 shows €10.00 (should be €15.50).

**Business Impact:** The receipt shows the wrong potential winnings. That is a customer trust
problem and possibly a regulatory one. The bet slip preview and the API `payout` field are correct, so only the receipt is wrong.

**Evidence:** [receipt](evidence/manual/BUG-01_receipt_balance_not_refreshed.png),
[pytest run](evidence/automated/pytest-run.txt)

### BUG-07: Receipt shows the teams in the wrong order

- **Severity:** Medium
- **Found in:** TC-01, step 5 (caught by the automated test)

**Reproduction Steps**
1. Place a bet on Manchester Utd vs Chelsea.
2. Read the MATCH field on the receipt.

**Expected vs Actual**
- Expected: "Manchester Utd vs Chelsea" (home team first, as on the match card).
- Actual: "Chelsea vs Manchester Utd".

**Business Impact:** Together with the selection "HOME", this makes it unclear which team the
user actually backed.

**Evidence:** [receipt](evidence/manual/BUG-01_receipt_balance_not_refreshed.png),
[pytest run](evidence/automated/pytest-run.txt)

## Automated run

Command: `HEADLESS=1 pytest` (from `automation/`). Allure results are written to
`automation/allure-results` on every run.

- Console output: [pytest-run.txt](evidence/automated/pytest-run.txt)
- Allure report (single HTML file, open in a browser): [allure-report/index.html](evidence/automated/allure-report/index.html).
  It includes steps, the receipt text, the place-bet response body and a screenshot taken
  automatically when the UI test fails.

| Test | Covers | Result | Why |
|---|---|---|---|
| `test_e2e_bet_placement.py` | TC-01 | FAIL | BUG-06, BUG-07, BUG-01 |
| `test_api_stake_validation.py` | TC-04 (API) | FAIL | BUG-02 |

Both failures are real bugs that match the manual results. The tests will pass once the bugs
are fixed.

## Evidence index

Evidence is split by how it was produced.

| File | Type | Test | Shows |
|---|---|---|---|
| [manual/BUG-01_receipt_balance_not_refreshed.png](evidence/manual/BUG-01_receipt_balance_not_refreshed.png) | Manual | TC-01 | BUG-01, BUG-06, BUG-07 |
| [manual/BUG-01_balance_after_reload.png](evidence/manual/BUG-01_balance_after_reload.png) | Manual | TC-01 | BUG-01 (balance correct only after reload) |
| [manual/TC-02_min_stake_0.99_blocked.png](evidence/manual/TC-02_min_stake_0.99_blocked.png) | Manual | TC-02 | PASS |
| [manual/TC-03_max_stake_100.01_blocked.png](evidence/manual/TC-03_max_stake_100.01_blocked.png) | Manual | TC-03 | PASS |
| [manual/TC-04_ui_insufficient_balance_blocked.png](evidence/manual/TC-04_ui_insufficient_balance_blocked.png) | Manual | TC-04 (UI) | PASS |
| [automated/pytest-run.txt](evidence/automated/pytest-run.txt) | Automated | TC-01, TC-04 (API) | BUG-01, BUG-02, BUG-06, BUG-07 (asserted); BUG-04 visible in the quoted response body, not asserted |
| [automated/allure-report/index.html](evidence/automated/allure-report/index.html) | Automated | TC-01, TC-04 (API) | Same run, with steps and attachments |

BUG-03 and BUG-05 were found in exploratory API checks. Their evidence is the request and
response quoted in the bug reports above.
