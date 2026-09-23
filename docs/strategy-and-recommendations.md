# Test Strategy: Single Bet Placement

| Item | Value |
|---|---|
| Document | Test Strategy and Recommendations |
| Product | Sports Betting QA app (https://qae-assignment-tau.vercel.app) |
| Feature | Single Bet Placement |
| Author | candidate-AAaEVUy7qvRT |
| Version | 1.1 |
| Date | 2026-09-23 |
| Status | Final for submission |

## 1. Purpose

This document sets out how the Single Bet Placement feature is tested. It defines the scope,
the test levels and types, the techniques, the entry and exit criteria, the environment and
data, how defects are classified, and where automation fits. The
[test plan](test-plan.md) and the [execution results](execution-results.md) follow this
strategy. Section 15 records the resulting recommendations.

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
- **Upcoming matches only.** R2 says only upcoming matches can be bet on. The live data labels every match "PAST" but still allows bets. This is recorded as an observation. It may be a test data artefact, so it is not reported as a defect.
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
| Confirmation (re-test) | Yes | Each defect is re-run before it is reported. All 7 were independently re-verified on 2026-09-23. |
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
| Critical | Money can be moved incorrectly, or a financial rule can be bypassed | BUG-02, BUG-03 |
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
in [evidence/](evidence/).

## 14. Project risks

| Risk | Mitigation |
|---|---|
| Shared environment. Other runs could change the balance. | Reset before and after each test. Don't run in parallel with the same user id. |
| The live app changes during testing | Record the date and evidence. Re-verify before reporting. |
| Spec ambiguity leads to wrong expectations | Raise open questions. Don't report ambiguous points as defects. |
| Limited time | Risk-based priorities. Critical scenarios first. |

## 15. Recommendations

1. **Enforce every stake rule on the server** (min, max, balance, no negatives), then add the parametrised API suite from section 11.3. This fixes the two Critical bugs (BUG-02, BUG-03) and stops them from coming back.
2. **Build the receipt and header balance from the API response.** The API already returns the correct payout and new balance. Using them fixes BUG-01, BUG-06 and BUG-07 in one area of the code.
3. **Run the suite in CI.** Run the API tests on every pull request and the headless UI test before merging, and publish the Allure report. Add response schema checks so that issues like the currency mismatch (BUG-04) and the reset value (BUG-05) are caught automatically.
4. **Resolve the spec questions** in section 4 (minimum stake, betting on past matches, Rebet) with the product owner, and update the test basis.
