# odds_providers/api_football.py

import os
import time
import json
import requests
from datetime import datetime

API_KEY_FOOTBALL = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY_FOOTBALL or ""
}

CACHE_FIXTURES = "cache/api_fixtures.json"
CACHE_ODDS = "cache/api_odds.json"
CACHE_TTL = 60 * 10  # 10 minutos


# =========================
# 1. PEGAR FIXTURES DO DIA
# =========================
def get_fixtures(date_str: str) -> dict:
    if os.path.exists(CACHE_FIXTURES):
        if time.time() - os.path.getmtime(CACHE_FIXTURES) < CACHE_TTL:
            return json.load(open(CACHE_FIXTURES, "r", encoding="utf-8"))

    url = f"{BASE_URL}/fixtures"
    params = {"date": date_str, "timezone": "UTC"}
    r = requests.get(url, headers=HEADERS, params=params)
    data = r.json()

    os.makedirs("cache", exist_ok=True)
    json.dump(data, open(CACHE_FIXTURES, "w", encoding="utf-8"), indent=2)

    return data


# =========================
# 2. PEGAR ODDS DO DIA
# =========================
def get_odds(date_str: str) -> dict:
    if os.path.exists(CACHE_ODDS):
        if time.time() - os.path.getmtime(CACHE_ODDS) < CACHE_TTL:
            return json.load(open(CACHE_ODDS, "r", encoding="utf-8"))

    url = f"{BASE_URL}/odds"
    params = {"date": date_str, "timezone": "UTC"}

    r = requests.get(url, headers=HEADERS, params=params)
    data = r.json()

    os.makedirs("cache", exist_ok=True)
    json.dump(data, open(CACHE_ODDS, "w", encoding="utf-8"), indent=2)

    return data


# =========================
# 3. UNIFICA ODDS + FIXTURES
# =========================
def get_matches_with_odds(date_str=None):
    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    fixtures = get_fixtures(date_str)
    odds_raw = get_odds(date_str)

    fixture_map = {}

    # montar mapa dos fixtures
    for f in fixtures.get("response", []):
        fixture_id = f["fixture"]["id"]
        fixture_map[fixture_id] = {
            "league": f["league"]["name"],
            "home": f["teams"]["home"]["name"],
            "away": f["teams"]["away"]["name"]
        }

    resultados = []

    for item in odds_raw.get("response", []):
        fixture_id = item["fixture"]["id"]

        if fixture_id not in fixture_map:
            continue

        base = fixture_map[fixture_id]

        for bookmaker in item.get("bookmakers", []):
            for bet in bookmaker.get("bets", []):

                bet_name = bet["name"].lower()

                # mapear mercado
                if "match winner" in bet_name:
                    market_type = "1x2"
                elif "total" in bet_name or "over" in bet_name:
                    market_type = "ou"
                elif "asian handicap" in bet_name or "handicap" in bet_name:
                    market_type = "handicap"
                elif "both teams to score" in bet_name:
                    market_type = "btts"
                elif "double chance" in bet_name:
                    market_type = "dc"
                elif "draw no bet" in bet_name:
                    market_type = "dnb"
                else:
                    continue

                outcomes = []
                for v in bet.get("values", []):
                    try:
                        odd_val = float(v["odd"])
                    except:
                        continue

                    outcomes.append({
                        "market": market_type,
                        "name": v.get("value", "N/A"),
                        "odd": odd_val,
                        "bookmaker": bookmaker["name"]
                    })

                if len(outcomes) >= 2:
                    resultados.append({
                        "fixture_id": fixture_id,
                        "league": base["league"],
                        "home": base["home"],
                        "away": base["away"],
                        "market": market_type,
                        "outcomes": outcomes
                    })

    return resultados
