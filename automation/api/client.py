"""
API client for the betting service.

All the endpoints and headers live in this module, so if the API changes only this file
needs updating. Tests call methods
that describe business actions, and the client is shared by the API tests and by the
test data fixtures (for example the balance reset).
"""
import requests
from config.settings import API_BASE_URL, USER_ID


class BettingApiClient:
    def __init__(self, base_url: str = API_BASE_URL, user_id: str = USER_ID):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"x-user-id": user_id})

    def get_matches(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/matches")

    def get_balance(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/balance")

    def place_bet(self, match_id: str, selection: str, stake) -> requests.Response:
        """
        Submits a single bet. `selection` is "HOME", "DRAW" or "AWAY".
        `stake` has no type annotation so that negative tests can send invalid types.
        """
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self.session.post(f"{self.base_url}/place-bet", json=payload)

    def reset_balance(self) -> requests.Response:
        return self.session.post(f"{self.base_url}/reset-balance")
