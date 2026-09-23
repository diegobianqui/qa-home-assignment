"""
TC-04 (API): the server rejects a stake that is above the current balance.

Rationale: the UI blocks this case on the client side ("Insufficient balance", with
Place Bet disabled). Any HTTP client can bypass the UI, though, so only an API-level
test shows whether the server itself enforces the rule.

Test data design: the stake has to be within the valid stake range (€1.00 to €100.00) and
above the balance at the same time. Otherwise a 422 would come from the maximum-stake
rule rather than the balance rule. The precondition therefore lowers the balance to
€20.00 with a valid €100.00 bet, and the test then submits a €50.00 stake.
"""
import pytest

PRECONDITION_STAKE = 100.00
OVER_BALANCE_STAKE = 50.00


@pytest.mark.api
@pytest.mark.critical
def test_stake_exceeding_balance_is_rejected(api_client, reset_balance):
    matches = api_client.get_matches().json()
    assert matches, "GET /api/matches returned no matches; precondition not met."
    match_id = matches[0]["id"]

    setup = api_client.place_bet(match_id=match_id, selection="HOME", stake=PRECONDITION_STAKE)
    assert setup.status_code == 200, f"Precondition bet failed: {setup.status_code} {setup.text}"
    balance_before = api_client.get_balance().json()["balance"]
    assert 0 < balance_before < OVER_BALANCE_STAKE, (
        f"Precondition not met: balance {balance_before} must be below the test stake."
    )

    response = api_client.place_bet(match_id=match_id, selection="HOME", stake=OVER_BALANCE_STAKE)
    balance_after = api_client.get_balance().json()["balance"]

    assert response.status_code == 422, (
        f"BUG-02: stake €{OVER_BALANCE_STAKE:.2f} exceeds balance €{balance_before:.2f} "
        f"but the API returned {response.status_code} (expected 422). "
        f"Balance is now €{balance_after:.2f}. Response: {response.text}"
    )
    assert response.json().get("error") != "invalid_stake_max", (
        "The request was rejected by the maximum-stake rule, not the balance rule."
    )
    assert balance_after == balance_before, (
        f"Balance changed from €{balance_before:.2f} to €{balance_after:.2f} after a rejected bet."
    )
