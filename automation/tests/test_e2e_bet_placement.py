"""
TC-01 (UI, end-to-end): a valid single bet is placed, the receipt shows the correct
details, and the displayed balance goes down by the stake.

Rationale: TC-01 is the highest-risk scenario in docs/test-plan.md because it is the
core business transaction. Only a browser journey covers the whole chain: selection,
stake entry, submission, receipt and balance side-effect.

The checks are collected first and asserted together at the end. One run therefore
reports every deviation found (BUG-01, BUG-06, BUG-07) instead of stopping at the
first failure.
"""
import re

import pytest

from pages.bet_slip_page import BetSlipPage
from pages.matches_page import MatchesPage

STAKE = "10.00"
HOME_TEAM = "Manchester Utd"
AWAY_TEAM = "Chelsea"
HOME_ODDS = 2.45


@pytest.mark.e2e
@pytest.mark.critical
def test_valid_bet_placement_succeeds_and_updates_balance(driver, reset_balance):
    matches_page = MatchesPage(driver)
    bet_slip = BetSlipPage(driver)
    expected_payout = f"€{float(STAKE) * HOME_ODDS:.2f}"

    matches_page.load().select_first_match_home_odds()
    balance_before = bet_slip.current_balance()

    bet_slip.enter_stake(STAKE).place_bet()
    receipt = bet_slip.wait_for_receipt()
    balance_after = bet_slip.wait_for_balance_change(balance_before)

    deviations = []
    if not re.search(r"#B-\d+", receipt):
        deviations.append("Receipt does not show a bet ID (#B-nnnnn).")
    if f"€{STAKE}" not in receipt:
        deviations.append(f"Receipt does not show the stake €{STAKE}.")
    if expected_payout not in receipt:
        deviations.append(
            f"BUG-06: receipt potential payout is not {expected_payout} "
            f"(stake x odds {HOME_ODDS})."
        )
    if f"{HOME_TEAM} vs {AWAY_TEAM}" not in receipt:
        deviations.append(f"BUG-07: receipt does not show '{HOME_TEAM} vs {AWAY_TEAM}'.")
    if round(balance_before - balance_after, 2) != float(STAKE):
        deviations.append(
            f"BUG-01: header balance went from €{balance_before:.2f} to "
            f"€{balance_after:.2f}; expected a reduction of €{STAKE}."
        )

    assert not deviations, (
        "TC-01 deviations:\n- " + "\n- ".join(deviations)
        + "\nReceipt text: " + receipt.replace("\n", " | ")
    )
