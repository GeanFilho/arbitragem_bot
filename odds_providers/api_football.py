# odds_providers/api_football.py

import requests
import os
import time
import json

API_KEY_FOOTBALL = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

CACHE_PATH = "cache/api_football_matches.json"
CACHE_TIME = 60 * 10  # 10 minutos de cache

HEADERS = {
    "x-apisports-key": API_KEY_FOOTBALL
}

def get_all_leagues():
    url = f"{BASE_URL}/leagues"
    r = requests.get(url, headers=HEADERS)
    return r.json()


def get_fixtures():
    """
    Retorna TODOS os jogos do dia, de todas as ligas.
    """
    # USAR CACHE
    if os.path.exists(CACHE_PATH):
        mod_time = os.path.getmtime(CACHE_PATH)
        if time.time() - mod_time < CACHE_TIME:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)

    url = f"{BASE_URL}/fixtures?date=today"
    r = requests.get(url, headers=HEADERS)
    data = r.json()

    # salvar cache
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return data


def get_odds_for_fixture(fixture_id):
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    r = requests.get(url, headers=HEADERS)
    return r.json()
