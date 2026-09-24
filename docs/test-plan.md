# Test Plan: Single Bet Placement

## Scope

This plan covers placing a single pre-match bet in the Sports Betting app
(https://qae-assignment-tau.vercel.app): picking odds, entering a stake, placing the bet,
the receipt, and the balance update. It is based on `Feature_Specification.pdf` and the
assignment brief (`HQA_Take_Home_Task.pdf`).

I prioritised by business risk. In a real-money product, anything that can move money
incorrectly (wrong stake, wrong balance, wrong payout) comes first. Cosmetic issues come last.

**Not covered here:**
- Date and odds filters. They matter less than the placement flow and are the next scenario I would add.
- Repeated Rebet retries after an error. The spec describes this differently for different error types, so it needs clarifying before a test can be written.

**Note on the minimum stake:** the spec gives the minimum as €1.00 in one place and €1.01
in another. The live app enforces €1.00 (see TC-02 results), so this plan uses €1.00.

## Scenarios

| ID | Title | Priority | Risk Rationale |
|---|---|---|---|
| TC-01 | Place a valid single bet | Critical | This is the core transaction. If it fails, or the receipt or balance is wrong, users lose money or trust. |
| TC-02 | Stake at the minimum boundary | Critical | If stakes under €1.00 get through, the business rule is broken and the API may accept junk values. |
| TC-03 | Stake at the maximum boundary | High | If stakes over €100.00 get through, liability is no longer capped. |
| TC-04 | Stake higher than the balance | Critical | If this is accepted, users can bet money they don't have and the balance goes negative. |
| TC-05 | Invalid stake format and type | Medium | Bad precision or types could be rounded silently or crash the service. |
| TC-06 | Changing and removing a selection | Medium | Stale bet slip data could lead to a bet on the wrong match or at the wrong odds. |
| TC-07 | Bet on a match that is not upcoming | Critical | A bet on a match that has already kicked off can be placed when the result is known, which is a direct financial loss. |

All tests start with the balance reset through `POST /api/reset-balance` and the app opened
at `/?user-id=<USER_ID>`.

## Test cases

### TC-01: Place a valid single bet

- **Priority:** Critical
- **Risk Rationale:** Core money flow. Covers the whole chain from selection to receipt to balance.
- **Automated:** yes, UI test (`automation/tests/test_e2e_bet_placement.py`)

**Preconditions**
1. Balance reset (the app currently persists €120.00, see BUG-05).
2. App open with the matches list visible.

**Test data:** Manchester Utd vs Chelsea, HOME at 2.45, stake €10.00.

**Steps**
1. Click the HOME odds (2.45) on the Manchester Utd vs Chelsea card.
2. Enter `10.00` as the stake.
3. Click **Place Bet**.
4. Wait for the bet to go through.
5. Check the receipt.
6. Check the balance in the header.
7. Close the receipt.

**Expected Result**
1. The bet slip shows the match, HOME and odds 2.45.
2. Potential payout shows €24.50 (10.00 x 2.45) and **Place Bet** is enabled.
3. The button changes to `Placing...`.
4. A success receipt opens.
5. The receipt shows a bet ID like `#B-12345`, "Manchester Utd vs Chelsea" (home team first), HOME, stake €10.00, odds 2.45, payout €24.50 and the time.
6. The header balance drops by €10.00 without reloading the page.
7. The receipt closes and the bet slip is empty.

### TC-02: Stake at the minimum boundary

- **Priority:** Critical
- **Risk Rationale:** The minimum is a business rule and was unclear in the spec, so both the UI and the API need checking.
- **Automated:** no (next candidate for automation)

**Preconditions**
1. Balance reset.
2. One selection added to the bet slip.

**Test data:** €0.99, €1.00, €1.01.

**Steps**
1. Enter `0.99` as the stake.
2. Enter `1.00` as the stake.
3. Enter `1.01` as the stake.
4. Send `POST /api/place-bet` with `stake: 0.99`.
5. Send `POST /api/place-bet` with `stake: 1.00`.

**Expected Result**
1. "Minimum stake is €1.00" is shown and **Place Bet** is disabled.
2. No message and **Place Bet** is enabled.
3. No message and **Place Bet** is enabled.
4. HTTP 422 with `invalid_stake_min`, and the balance does not change.
5. HTTP 200, and the balance drops by €1.00.

### TC-03: Stake at the maximum boundary

- **Priority:** High
- **Risk Rationale:** The maximum caps liability. It is ranked below TC-02 and TC-04 because the worst case is capped at €100.00 per bet.
- **Automated:** no

**Preconditions**
1. Balance reset.
2. One selection added to the bet slip.

**Test data:** €99.99, €100.00, €100.01.

**Steps**
1. Enter `99.99` as the stake.
2. Enter `100.00` as the stake.
3. Enter `100.01` as the stake.
4. Send `POST /api/place-bet` with `stake: 100.01`.
5. Send `POST /api/place-bet` with `stake: 100.00`.

**Expected Result**
1. No message and **Place Bet** is enabled.
2. No message and **Place Bet** is enabled.
3. "Maximum stake is €100.00" is shown and **Place Bet** is disabled.
4. HTTP 422 with `invalid_stake_max`, and the balance does not change.
5. HTTP 200, and the balance drops by €100.00.

### TC-04: Stake higher than the balance

- **Priority:** Critical
- **Risk Rationale:** Overdrawing an account is a direct financial loss. The rule has to hold on the server, because anyone can call the API without the UI.
- **Automated:** yes, API test (`automation/tests/test_api_stake_validation.py`)

**Preconditions**
1. Balance reset.
2. A €100.00 bet placed, which leaves €20.00.

**Test data:** stake €50.00. It is inside the €1.00 to €100.00 range but above the €20.00
balance, so only the balance rule can reject it.

**Steps**
1. Add a selection in the UI and enter `50.00`.
2. Send `POST /api/place-bet` with `stake: 50.00`.
3. Send `GET /api/balance`.

**Expected Result**
1. "Insufficient balance" is shown and **Place Bet** is disabled.
2. HTTP 422 and no bet is created.
3. The balance is still €20.00.

### TC-05: Invalid stake format and type

- **Priority:** Medium
- **Risk Rationale:** Silent rounding or unhandled types could create bets for amounts the user never entered.
- **Automated:** no

**Preconditions**
1. Balance reset.
2. One selection added to the bet slip.

**Steps**
1. Type `abc`, `1e5` and `1.2.3` into the stake field.
2. Type `10.999` into the stake field.
3. Send `POST /api/place-bet` with `stake: 10.999`.
4. Send `POST /api/place-bet` with `stake: "10"` (a string) and then with `stake: null`.
5. Send `POST /api/place-bet` with `stake: -5`.

**Expected Result**
1. Letters and a second decimal point cannot be entered.
2. Only 2 decimal places can be entered.
3. HTTP 422 with `invalid_stake_precision`.
4. HTTP 422 with `invalid_stake_type` for both.
5. HTTP 422, and the balance does not change.

### TC-06: Changing and removing a selection

- **Priority:** Medium
- **Risk Rationale:** If old data stays in the bet slip, the user could bet on the wrong match or at the wrong odds.
- **Automated:** no

**Preconditions**
1. App loaded with an empty bet slip.

**Steps**
1. Pick odds on match A and enter `10.00`.
2. Pick odds on match B without placing the bet.
3. Pick match A again and click the remove (`x`) button on the selection.
4. Pick match A again and click **Remove All**.

**Expected Result**
1. The bet slip shows match A, its odds and the payout for €10.00.
2. The bet slip shows only match B, with its own odds and payout. Nothing from match A is left.
3. The bet slip is empty.
4. The bet slip is empty, and the balance has not changed at any point.

### TC-07: Bet on a match that is not upcoming

- **Priority:** Critical
- **Risk Rationale:** The spec allows only upcoming (pre-match) bets. The rule has to hold in both the UI and the API, because a bet on a finished match can be placed when the outcome is already known.
- **Automated:** no (next candidate for the API suite)

**Preconditions**
1. Balance reset.
2. `GET /api/matches` returns at least one match whose `kickoffDate` is before today.

**Test data:** Manchester Utd vs Chelsea (`premier-league-manutd-chelsea`, kickoff 2026-02-27), HOME at 2.45, stake €1.00.

**Steps**
1. Open the match list and look for the Manchester Utd vs Chelsea card.
2. Inspect the odds buttons on that card.
3. Click the HOME odds, enter `1.00` and click **Place Bet**.
4. Send `POST /api/place-bet` with `matchId: premier-league-manutd-chelsea`, `selection: HOME`, `stake: 1.00`.
5. Send `GET /api/balance`.

**Expected Result**
1. Matches that have already kicked off are not offered under "Upcoming Football Matches".
2. If such a match is shown, its odds are disabled.
3. No selection is added and no bet is placed.
4. The API rejects the bet with a 4xx status and no bet is created. The spec gives no error code for this case, so only the rejection is asserted.
5. The balance has not changed.
