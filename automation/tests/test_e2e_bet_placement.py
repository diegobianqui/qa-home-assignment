"""
TC-01 (UI, end-to-end): a valid single bet is placed, the receipt shows the correct
details, and the displayed balance goes down by the stake.

Rationale: TC-01 is the highest-risk scenario in docs/test-plan.md because it is the
core business transaction. Only a browser journey covers the whole chain: selection,
stake entry, submission, receipt and balance side-effect.

The checks are collected first and asserted together at the end. One run therefore
reports every deviation from the specification instead of stopping at the first failure.
"""
import re

import allure
import pytest

from pages.bet_slip_page import BetSlipPage
from pages.matches_page import MatchesPage

STAKE = "10.00"
HOME_TEAM = "Manchester Utd"
AWAY_TEAM = "Chelsea"
HOME_ODDS = 2.45


@allure.feature("Single Bet Placement")
@allure.story("TC-01 Valid bet placement (UI)")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.critical
def test_valid_bet_placement_succeeds_and_updates_balance(driver, reset_balance):
    matches_page = MatchesPage(driver)
    bet_slip = BetSlipPage(driver)
    expected_payout = f"€{float(STAKE) * HOME_ODDS:.2f}"

    with allure.step("Select HOME odds of the first match"):
        matches_page.load().select_first_match_home_odds()
        balance_before = bet_slip.current_balance()

    with allure.step(f"Enter stake €{STAKE} and place the bet"):
        bet_slip.enter_stake(STAKE).place_bet()
        receipt = bet_slip.wait_for_receipt()
        balance_after = bet_slip.wait_for_balance_change(balance_before)
    allure.attach(receipt, name="receipt-text", attachment_type=allure.attachment_type.TEXT)

    expected_match = f"{HOME_TEAM} vs {AWAY_TEAM}"
    expected_balance = round(balance_before - float(STAKE), 2)
    payout_found = re.search(r"Potential Payout\s*(€[\d.,]+)", receipt)
    match_found = re.search(r"MATCH\s*\n?\s*(.+)", receipt)

    deviations = []
    if not re.search(r"#B-\d+", receipt):
        deviations.append("Receipt bet ID: expected '#B-nnnnn', not found.")
    if f"€{STAKE}" not in receipt:
        deviations.append(f"Receipt stake: expected €{STAKE}, not found.")
    if expected_payout not in receipt:
        deviations.append(
            f"Receipt potential payout: expected {expected_payout} (stake €{STAKE} x odds "
            f"{HOME_ODDS}), actual {payout_found.group(1) if payout_found else 'not found'}."
        )
    if expected_match not in receipt:
        deviations.append(
            f"Receipt match: expected '{expected_match}' (home team first), "
            f"actual '{match_found.group(1).strip() if match_found else 'not found'}'."
        )
    if round(balance_after, 2) != expected_balance:
        deviations.append(
            f"Header balance after bet: expected €{expected_balance:.2f} "
            f"(€{balance_before:.2f} - €{STAKE}), actual €{balance_after:.2f}."
        )

    assert not deviations, (
        "TC-01 deviations:\n- " + "\n- ".join(deviations)
        + "\nReceipt text: " + receipt.replace("\n", " | ")
    )
