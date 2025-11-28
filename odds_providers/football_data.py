# odds_providers/football_data.py

import requests
import os

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")

BASE_URL = "http://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": FOOTBALL_DATA_KEY
}

def get_matches_from_league(league_code):
    """
    Pega jogos de uma competição específica da Football-Data:
    Ex: PL = Premier League, CL = Champions League, etc.
    """
    url = f"{BASE_URL}/competitions/{league_code}/matches"
    r = requests.get(url, headers=HEADERS)
    return r.json()
