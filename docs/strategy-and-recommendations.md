# Test Strategy: Single Bet Placement

| Item | Value |
|---|---|
| Document | Test Strategy and Recommendations |
| Product | Sports Betting QA app (https://qae-assignment-tau.vercel.app) |
| Feature | Single Bet Placement |
| Author | candidate-AAaEVUy7qvRT |
| Version | 1.2 |
| Date | 2026-09-24 |
| Status | Final for submission |

## 1. Purpose

This document sets out how the Single Bet Placement feature is tested. It defines the scope,
the test levels and types, the techniques, the entry and exit criteria, the environment and
data, how defects are classified, and where automation fits. The
[test plan](test-plan.md) and the [execution results](execution-results.md) follow this
strategy. Section 15 records the resulting recommendations, and section 16 traces every
requirement in R2 to its test cases, results and defects.

The structure follows the ISTQB Foundation Level syllabus and the test strategy content
described in ISO/IEC/IEEE 29119-3, scaled down to fit a single feature and a take-home
timebox.

## 2. References

| Ref | Document | Use |
|---|---|---|
| R1 | `HQA_Take_Home_Task.pdf` (assignment brief) | Deliverables, constraints, domain rules |
| R2 | `Feature_Specification.pdf` | Business rules, UI copy, API contract |
| R3 | [test-plan.md](test-plan.md) | Scenarios and test cases derived from this strategy |
| R4 | [execution-results.md](execution-results.md) | Results, bug reports, evidence |
| R5 | [automation/](../automation/) | Automated tests |
| R6 | [static-testing-review.md](static-testing-review.md) | Specification review findings (DEF-xx) |

## 3. Scope

### 3.1 Test items

- The web UI: matches list, odds buttons, bet slip, Place Bet, receipt modal, error modal and header balance.
- The REST API behind it: `GET /api/matches`, `GET /api/balance`, `POST /api/place-bet`, `POST /api/reset-balance`.

### 3.2 Features in scope

| Area | What is covered |
|---|---|
| Selection | Picking odds, changing selection, removing it (`x`, Remove All) |
| Stake validation | Min €1.00, max €100.00, 2 decimal places, positive values only, stake not above balance, UI and API |
| Placement | Loading state, success path, error modal |
| Receipt | Bet ID, match, selection, stake, odds, payout (stake x odds), timestamp |
| Balance | Deduction after a bet, shared value in header and bet slip, reset to €125.50 |
| API contract | Status codes (200 / 422), error codes, response fields, EUR currency |

### 3.3 Out of scope

| Item | Reason |
|---|---|
| Date and odds filters | Lower risk than placement. The next area to add. |
| Multiple bets / accumulators | Not part of the feature |
| Bet settlement and payouts after a match | Not part of the feature |
| Performance, load, security testing (beyond input validation), accessibility | Not requested by the brief. No suitable environment. |
| Cross-browser and mobile layout | Only Chrome on desktop is used |
| Unit and component testing | No access to the source code |

## 4. Test basis and assumptions

The test basis is R1 and R2. Where they differ from the live app, the documents are
treated as the expected behaviour and the difference is reported as a defect, unless the
documents contradict each other.

Known ambiguities are recorded rather than guessed:

- **Minimum stake.** Section 3 of R2 says €1.00. Section 4.1 says €1.01. The UI copy and the live app use €1.00, so tests use €1.00 and the conflict is raised as an open question.
- **Upcoming matches only.** R2 says only upcoming matches can be bet on. The live catalogue returns 103 matches, 78 of them with a kickoff date in the past, which the UI labels "PAST". The rule is not ambiguous, so it was turned into TC-07. The test failed in both the UI and the API and is reported as BUG-08 (REQ-01 in section 16).
- **Rebet behaviour.** Rebet behaves differently for different error types and is described unclearly, so it stays out of scope until clarified.

Assumptions:
- The environment is shared, and state is stored per user id. Each test resets the balance first.
- The live app may change during the assignment. Results are only valid for the date they were recorded.

## 5. Risk-based approach

Testing effort follows product risk. Risk is rated as likelihood x impact. Impact is
judged from the business point of view of a real-money product.

| Risk | Impact | Likelihood | Level | Covered by |
|---|---|---|---|---|
| Money moved incorrectly (stake above balance, negative stake, wrong deduction) | High | Medium | Critical | TC-01, TC-04, TC-05 |
| Bet accepted on a match that is not upcoming (result already known) | High | Medium | Critical | TC-07 |
| Stake limits bypassed (min/max) | High | Medium | Critical / High | TC-02, TC-03 |
| Wrong financial information shown to the user (payout, balance) | High | Medium | High | TC-01 |
| Bet placed on the wrong match or odds (stale slip) | Medium | Low | Medium | TC-06 |
| Inconsistent data between UI and API (currency, team order, reset) | Medium | Medium | Medium | TC-01, exploratory |

Prioritisation rules:
1. Critical risks are tested first, at both the UI and API layers.
2. Server-side rules are always checked directly at the API, because UI validation can hide server defects.
3. Lower risks are covered by exploratory testing when time allows.

## 6. Test levels

| Level | Applied | Focus |
|---|---|---|
| Component (unit) | No | No access to the source code |
| Integration (API) | Yes | Contract and business rules at `/api`, tested with `requests` and without the UI |
| System (end to end) | Yes | Full user journey in the browser, UI and API together |
| Acceptance | No | Owned by the product owner. This work supports it with evidence. |

Static testing is also used. The specification was reviewed before test design, and the
review found the minimum-stake conflict and the "upcoming only" gap described in section 4.

## 7. Test types

| Type | Applied | Notes |
|---|---|---|
| Functional | Yes | Main focus: validation, placement, receipt, balance |
| Contract (API) | Yes | Status codes, error codes, field names, currency |
| Confirmation (re-test) | Yes | Each defect is re-run before it is reported. BUG-01 to BUG-07 were independently re-verified on 2026-09-23 and BUG-08 on 2026-09-24. |
| Regression | Yes, automated | The two automated tests guard the highest-risk flows. See section 11. |
| Non-functional | No | Out of scope (section 3.3) |

## 8. Test design techniques

| Technique | Where it is used |
|---|---|
| Equivalence partitioning | Stake: valid, below min, above max, above balance, negative, non-numeric |
| Boundary value analysis (3-value) | 0.99 / 1.00 / 1.01 and 99.99 / 100.00 / 100.01 |
| State transition | Bet slip: empty, selected, stake entered, placing, receipt, cleared |
| Decision table | Stake validity combined with balance sufficiency |
| Error guessing | Precision (`10.999`), types (`"10"`, `null`), unknown match id, scientific notation |
| Session-based exploratory testing | A 15-minute charter on validation, payout and balance, run mainly through the API |

Each test case in the test plan has numbered steps, a numbered expected result for each
step, preconditions and test data.

## 9. Entry and exit criteria

**Entry criteria**
- The test basis (R1, R2) is available and has been reviewed.
- The environment is reachable, and `POST /api/reset-balance` works for the user id.
- The test plan scenarios have been prioritised by risk.

**Exit criteria**
- All Critical scenarios have been executed at both the UI and API layers.
- Every defect is reproduced at least twice, has evidence (a screenshot, response body or test output), and is classified by severity.
- The automated tests run and fail only on confirmed defects (no false positives).
- Residual risk is stated: scenarios that were not executed and open questions are listed in the execution results.

**Suspension and resumption**
- Testing is suspended if the environment is unavailable or the reset endpoint fails, because results would not be reliable.
- Testing resumes once the reset returns a consistent balance.

## 10. Environment, data and tools

| Item | Value |
|---|---|
| Environment | Shared live deployment. User id `candidate-AAaEVUy7qvRT` sent as the `x-user-id` header and the `user-id` query parameter. |
| Browser | Google Chrome on macOS, 1920x1080 |
| Test data | Manchester Utd vs Chelsea (HOME 2.45, DRAW 3.10, AWAY 2.80). Stakes are chosen by the technique in section 8. |
| Data reset | `POST /api/reset-balance` before and after each test |
| Tools | Python, Selenium, pytest, requests, webdriver-manager, python-dotenv, allure-pytest |

## 11. Automation approach

### 11.1 Principles

- **Test pyramid.** Business rules are automated at the API level, which is fast and stable. The UI is automated only for journeys that need a real browser.
- **Layered framework.** The framework keeps configuration, page objects / API client and tests in separate layers. A locator or endpoint change touches one file.
- **Independent tests.** Fixtures reset the balance before and after each test, so the order of tests doesn't matter.
- **Complete verdicts.** Tests collect all mismatches before failing, so one run reports every defect in a flow. Each failure message starts with its bug ID.
- **Evidence-based assertions.** Assertions are written against the spec (R1, R2), not against the current behaviour of the app.

### 11.2 Selection of automated tests

The brief allows one UI test and one API test. They were chosen by risk level and by which
test level suits each case.

**UI test: TC-01, place a valid bet.** This is the main flow of the feature and the only one
that needs a browser. It covers selection, bet slip, placement, receipt and header balance.
It currently fails on BUG-06, BUG-07 and BUG-01.

**API test: TC-04, stake above the balance.** This is the rule that protects real money. It has
to hold on the server regardless of the client. The UI blocks it, which hides the problem.
The API accepts the bet and the balance goes negative (BUG-02). The test is fast and
stable, so it can run on every change.

### 11.3 Manual coverage

| Scope | Reason it stays manual | Next step |
|---|---|---|
| Exploratory testing | It found BUG-03, BUG-04 and BUG-05, and relies on observation | Turn its findings into API assertions |
| TC-02, TC-03, TC-05 (stake validation) | Only because of the two-test limit | One parametrised API test for the boundaries, precision and types |
| TC-06 (changing selection) | A lot of UI state for a Medium risk. Scripts would be brittle. | Keep manual |
| Filters, layout | Out of scope | Filters are the next scenario to add |

## 12. Defect management

Each defect report has an ID, a title, severity, the environment, preconditions,
numbered steps, expected and actual results, the business impact and evidence. The
expected result must cite R1 or R2.

| Severity | Definition | Example |
|---|---|---|
| Critical | Money can be moved incorrectly, or a financial rule can be bypassed | BUG-02, BUG-03, BUG-08 |
| High | Wrong financial information is shown to the user, but no money moves incorrectly | BUG-01, BUG-06 |
| Medium | Data is inconsistent or wrong, with no direct financial effect | BUG-04, BUG-05, BUG-07 |
| Low | Cosmetic issue or wording | None found |

Observations that are not clearly defects, such as spec gaps or possible data artefacts,
are recorded separately as open questions and are not counted as bugs.

## 13. Metrics and reporting

- Scenarios planned, executed, passed and failed, by priority.
- Defects by severity and by layer (UI / API).
- Automated test results with an Allure report (optional).
- Residual risk: scenarios not executed and open questions.

The results are reported in [execution-results.md](execution-results.md). Evidence is stored
in [evidence/](evidence/), split into `manual/` (screenshots from manual execution) and
`automated/` (pytest output and the Allure report).

## 14. Project risks

| Risk | Mitigation |
|---|---|
| Shared environment. Other runs could change the balance. | Reset before and after each test. Don't run in parallel with the same user id. |
| The live app changes during testing | Record the date and evidence. Re-verify before reporting. |
| Spec ambiguity leads to wrong expectations | Raise open questions. Don't report ambiguous points as defects. |
| Limited time | Risk-based priorities. Critical scenarios first. |

## 15. Recommendations

1. **Enforce every betting rule on the server** (min, max, balance, no negatives, upcoming matches only), then add the parametrised API suite from section 11.3. This fixes the three Critical bugs (BUG-02, BUG-03, BUG-08) and stops them from coming back.
2. **Build the receipt and header balance from the API response.** The API already returns the correct payout and new balance. Using them fixes BUG-01, BUG-06 and BUG-07 in one area of the code.
3. **Run the suite in CI.** Run the API tests on every pull request and the headless UI test before merging, and publish the Allure report. Add response schema checks so that issues like the currency mismatch (BUG-04) and the reset value (BUG-05) are caught automatically.
4. **Resolve the spec questions** in section 4 (minimum stake, Rebet) with the product owner, and update the test basis.
5. **Close the coverage gaps** listed in section 16.3, starting with REQ-10 (error modal and Rebet), the highest-risk requirement without a test case.

## 16. Requirements traceability matrix

The matrix links each testable requirement in R2 to the risk level from section 5, the test
cases in R3, the latest result in R4 and the defects raised. Requirement IDs are assigned
here because R2 has no numbered requirements. Results are as recorded on 2026-09-23, except TC-07, which was run on 2026-09-24.

**Legend**
- **Layer:** UI = browser, API = direct HTTP call.
- **Execution:** Automated (pytest suite), Manual (scripted test case), Exploratory (session in R4), Not run (planned in R3 but not executed), Not covered (no test case), Out of scope (section 3.3).
- **Result:** PASS, FAIL, Partial (only part of the requirement was verified), or "-" when nothing was executed.
- **Defects / findings:** BUG-xx are defects in R4. DEF-xx are specification findings in R6.

### 16.1 Forward traceability (requirement to test)

| Req ID | R2 ref | Requirement | Risk | Test case(s) | Layer | Execution | Result | Defects / findings |
|---|---|---|---|---|---|---|---|---|
| REQ-01 | §1, §2.1, §3 | Only upcoming (pre-match) matches can be bet on | Critical | TC-07 | UI, API | Manual | FAIL | BUG-08 |
| REQ-02 | §2.1 | Match card shows home vs away, kickoff date/time and 1 / X / 2 odds | Medium | TC-01 (step 1) | UI | Manual, Automated | Partial | Teams and odds checked. Kickoff time not verified (DEF-03). |
| REQ-03 | §2.1, §3 | Single bet only: a new selection replaces the previous one | Medium | TC-06 (step 2) | UI | Not run | - | |
| REQ-04 | §2.2 | Bet slip shows the selection, stake, available balance and potential payout (stake x odds) | High | TC-01 (steps 1-2) | UI | Manual, Automated | PASS | |
| REQ-05 | §2.2 | Selection can be removed with `x` or Remove All | Medium | TC-06 (steps 3-4) | UI | Not run | - | DEF-07 |
| REQ-06 | §2.3 | Place Bet shows a loading state ("Placing...") | Low | TC-01 (step 3) | UI | Manual | PASS | |
| REQ-07 | §2.3 | On success the stake is deducted and the displayed balance updates | Critical | TC-01 (step 6) | UI, API | Manual, Automated | FAIL | BUG-01. API balance correct, header not refreshed. |
| REQ-08 | §2.4 | Receipt shows bet ID, match (home first), selection, stake, odds at placement, payout and timestamp | High | TC-01 (step 5) | UI | Manual, Automated | FAIL | BUG-06, BUG-07. DEF-02 resolved. |
| REQ-09 | §2.4 | Closing the receipt returns to the main flow with no active selection | Low | TC-01 (step 7) | UI | Manual | PASS | |
| REQ-10 | §2.3, §2.5 | On failure an error modal ("Something went wrong") opens. Rebet retries. Close and X clear the slip. | High | None | UI | Not covered | - | DEF-06 |
| REQ-11 | §2.6 | Date and odds filters, with inclusive ranges and rejection of invalid ranges | Low | None | UI | Out of scope | - | DEF-05 |
| REQ-12 | §3, §4.1, §4.4 | Minimum stake €1.00, with "Minimum stake is €1.00" | Critical | TC-02 | UI, API | Manual | PASS | DEF-01 resolved |
| REQ-13 | §3, §4.1, §4.4 | Maximum stake €100.00, with "Maximum stake is €100.00" | High | TC-03 | UI, API | Manual (extra check) | Partial | €100.01 rejected at both layers. €99.99 and €100.00 not run. |
| REQ-14 | §3, §4.1, §4.4 | Stake has at most 2 decimal places | Medium | TC-05 (steps 2-3) | UI, API | Exploratory | Partial | API rejects `10.999` (`invalid_stake_precision`). UI not run. |
| REQ-15 | §4.1, §4.4 | Stake is required and numeric, with one decimal separator | Medium | TC-05 (steps 1, 4) | UI, API | Exploratory | Partial | API rejects `"10"` and `null` (`invalid_stake_type`). UI not run. |
| REQ-16 | §4.1 | Stake must be positive | Critical | TC-05 (step 5) | API | Exploratory | FAIL | BUG-03 |
| REQ-17 | §4.1, §4.4 | Stake cannot exceed the balance ("Insufficient balance") | Critical | TC-04 | UI, API | Manual (UI), Automated (API) | FAIL | UI PASS, API FAIL (BUG-02) |
| REQ-18 | §4.2 | Selection is required (UI, API) and must be HOME, DRAW or AWAY (API) | Medium | None | UI, API | Not covered | - | |
| REQ-19 | §4.2 | Match ID is non-empty and exists in the catalogue | Medium | None (exploratory only) | API | Exploratory | Partial | Unknown ID rejected (`invalid_match`). Empty ID not run. |
| REQ-20 | §3 | Odds are between 1.01 and 1000.00 and static for the session | Medium | None | UI, API | Not covered | - | DEF-04 |
| REQ-21 | §3, §5.3 | Currency is EUR in the UI and all API responses | Medium | None (exploratory only) | API | Exploratory | FAIL | BUG-04 |
| REQ-22 | §5.3 | `POST /api/reset-balance` restores the initial balance | Medium | None (precondition of every test) | API | Exploratory | FAIL | BUG-05 |
| REQ-23 | §4.3, §5.1, §5.3 | Protocol errors: invalid JSON 400, missing or invalid `x-user-id` 401, unsupported method 405, bet in progress 409 | Medium | None | API | Not covered | - | DEF-08 |

### 16.2 Backward traceability (test and defect to requirement)

| Item | Traces to |
|---|---|
| TC-01 | REQ-02, REQ-04, REQ-06, REQ-07, REQ-08, REQ-09 |
| TC-02 | REQ-12 |
| TC-03 | REQ-13 |
| TC-04 | REQ-17 |
| TC-05 | REQ-14, REQ-15, REQ-16 |
| TC-06 | REQ-03, REQ-05 |
| TC-07 | REQ-01 |
| `test_e2e_bet_placement.py` | REQ-07, REQ-08 (via TC-01) |
| `test_api_stake_validation.py` | REQ-17 (via TC-04) |
| BUG-01 | REQ-07 |
| BUG-02 | REQ-17 |
| BUG-03 | REQ-16 |
| BUG-04 | REQ-21 |
| BUG-05 | REQ-22 |
| BUG-06, BUG-07 | REQ-08 |
| BUG-08 | REQ-01 |

Every test case and every reported defect traces to at least one requirement. No test
exists without a requirement behind it.

### 16.3 Coverage summary

| Status | Count | Requirements |
|---|---|---|
| Covered, PASS | 4 | REQ-04, REQ-06, REQ-09, REQ-12 |
| Covered, Partial (passing so far) | 5 | REQ-02, REQ-13, REQ-14, REQ-15, REQ-19 |
| Covered, FAIL | 7 | REQ-01, REQ-07, REQ-08, REQ-16, REQ-17, REQ-21, REQ-22 |
| Planned, not run | 2 | REQ-03, REQ-05 |
| Not covered | 4 | REQ-10, REQ-18, REQ-20, REQ-23 |
| Out of scope | 1 | REQ-11 |
| **Total** | **23** | |

By risk, all 5 Critical requirements were executed and 4 of them failed (REQ-01, REQ-07,
REQ-16, REQ-17). Every Critical requirement now has a test case.

**Gaps and next actions, in priority order**
1. REQ-01 (Critical): automate TC-07 at the API level so that BUG-08 is caught on every run.
2. REQ-10 (High): add an error-modal test once the Rebet behaviour is clarified (DEF-06).
3. REQ-13, REQ-14, REQ-15, REQ-19: complete the remaining boundaries and UI checks in the parametrised API suite (section 11.3).
4. REQ-18, REQ-23: add negative API tests for the selection enum, protocol errors and concurrent placement.
5. REQ-03, REQ-05: execute TC-06.
6. REQ-20: add once "session" is defined (DEF-04).
