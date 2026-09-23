# Strategy and Recommendations

## Why these two tests

**UI test: TC-01, placing a valid bet.** This is the main thing the feature exists to do,
and the only flow that really needs a browser. It covers the full journey: selecting odds,
the bet slip, placing the bet, the receipt and the header balance. The test collects every
mismatch before failing, so one run reports all three receipt and balance bugs
(BUG-06, BUG-07, BUG-01) instead of stopping at the first one.

**API test: TC-04, stake higher than the balance.** This is the rule that protects real
money, and it has to hold on the server regardless of the client. The UI blocks it, which
hides the problem. Calling the API directly showed the server accepts the bet and leaves a
negative balance (BUG-02). An API test is also fast and stable, so it's cheap to run on
every change.

Together they follow the usual test pyramid: business rules are checked at the API level,
and the UI test is kept for the flow that needs a real page.

## What stays manual (for now)

- **Exploratory testing.** It found three of the seven bugs (BUG-03, BUG-04, BUG-05), and that kind of observation doesn't translate well into scripts.
- **TC-02, TC-03 and TC-05 (stake validation).** These are the next things I would automate, as one parametrised API test covering the min/max boundaries, precision and types. They're manual for now only because of the two-test limit.
- **TC-06 (changing the selection).** Lots of UI state to assert on, and it would break often for a Medium-risk scenario. Cheaper to check by hand.
- **Filters and visual layout.** Filters are the next scenario I would add. Layout is out of scope for this assignment.

## Top recommendations

1. **Enforce every stake rule on the server** (min, max, balance, no negatives), then add the parametrised API suite described above. This fixes the two Critical bugs (BUG-02, BUG-03) and stops them coming back.
2. **Build the receipt and header balance from the API response.** The API already returns the correct payout and new balance, so the UI should use those values. This fixes BUG-01, BUG-06 and BUG-07 in one area of the code.
3. **Run the suite in CI.** Run the API tests on every pull request and the headless UI test before merging, and publish the Allure report. Add simple response schema checks so issues like the currency mismatch (BUG-04) and the reset value (BUG-05) get caught automatically.
