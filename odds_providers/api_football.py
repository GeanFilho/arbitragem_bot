# odds_providers/api_football.py

import os
import time
import json
from datetime import datetime
from typing import List, Dict

import requests

API_KEY_FOOTBALL = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY_FOOTBALL or ""
}

CACHE_PATH = "cache/api_football_odds.json"
CACHE_TTL = 60 * 10  # 10 minutos


def _fetch_odds_from_api(date_str: str) -> Dict:
    """
    Chama endpoint de odds da API-Football para uma data específica.
    """
    url = f"{BASE_URL}/odds"
    params = {
        "date": date_str,
        "timezone": "UTC",
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _load_cache() -> Dict | None:
    if not os.path.exists(CACHE_PATH):
        return None

    mod_time = os.path.getmtime(CACHE_PATH)
    if time.time() - mod_time > CACHE_TTL:
        return None

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return None


def _save_cache(data: Dict) -> None:
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_matches_with_odds(date_str: str | None = None) -> List[Dict]:
    """
    Retorna lista de partidas com odds normalizadas EM VÁRIOS MERCADOS.

    Cada item retornado é:
    {
      "fixture_id": int,
      "league": str,
      "home": str,
      "away": str,
      "market": str,   # "1x2", "ou", "handicap", "btts", "dc", "dnb"
      "outcomes": [
          {"name": str, "odd": float, "bookmaker": str},
          ...
      ]
    }
    """

    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # tenta cache
    cached = _load_cache()
    if cached and cached.get("date") == date_str:
        raw = cached.get("data", {})
    else:
        raw = _fetch_odds_from_api(date_str)
        _save_cache({"date": date_str, "data": raw})

    response = raw.get("response", [])
    if not response:
        return []

    # key: (fixture_id, market_type) → objeto de partida
    matches_map: Dict[tuple, Dict] = {}

    for item in response:
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})

        fixture_id = fixture.get("id")
        league_name = league.get("name", "Unknown League")
        home_team = teams.get("home", {}).get("name", "Home")
        away_team = teams.get("away", {}).get("name", "Away")

        bookmakers = item.get("bookmakers", [])
        if not bookmakers:
            continue

        for bk in bookmakers:
            bk_name = bk.get("name", "BK")
            bets = bk.get("bets", [])
            for bet in bets:
                bet_name = (bet.get("name") or "").lower()

                # Mapeia o nome do mercado
                if "match winner" in bet_name or "1x2" in bet_name:
                    market_type = "1x2"
                elif "total" in bet_name or "over/under" in bet_name:
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
                    # mercado que não vamos usar
                    continue

                key = (fixture_id, market_type)

                if key not in matches_map:
                    matches_map[key] = {
                        "fixture_id": fixture_id,
                        "league": league_name,
                        "home": home_team,
                        "away": away_team,
                        "market": market_type,
                        "outcomes": []
                    }

                values = bet.get("values", [])
                for v in values:
                    name = v.get("value", "N/A")
                    odd_str = v.get("odd")
                    if odd_str is None:
                        continue
                    try:
                        odd_val = float(odd_str)
                    except Exception:
                        continue

                    matches_map[key]["outcomes"].append({
                        "name": name,
                        "odd": odd_val,
                        "bookmaker": bk_name,
                    })

    # filtra partidas sem outcomes suficientes
    result = []
    for match in matches_map.values():
        if len(match["outcomes"]) >= 2:
            result.append(match)

    return result
