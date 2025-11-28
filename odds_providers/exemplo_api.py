# odds_providers/exemplo_api.py

import requests
from typing import List, Dict
from config import API_KEY, SPORTS, REGIONS, MARKETS

BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds/"

def get_odds() -> List[Dict]:
    """
    Puxa odds de TODAS as ligas listadas em SPORTS.
    """
    all_matches = []

    for sport in SPORTS:
        print(f"🔎 Buscando odds para: {sport}")

        url = BASE_URL.format(sport=sport)
        params = {
            "api_key": API_KEY,
            "regions": REGIONS,
            "markets": MARKETS,
        }

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            for event in data:
                match = {
                    "id": event["id"],
                    "home": event["home_team"],
                    "away": event["away_team"],
                    "league": sport,
                    "outcomes": []
                }

                for bookmaker in event.get("bookmakers", []):
                    bk_name = bookmaker["title"]

                    for market in bookmaker.get("markets", []):
                        if market["key"] != MARKETS:
                            continue

                        for outcome in market["outcomes"]:
                            match["outcomes"].append({
                                "name": outcome["name"],
                                "odd": float(outcome["price"]),
                                "bookmaker": bk_name
                            })

                all_matches.append(match)

        except Exception as e:
            print(f"⚠️ Erro ao puxar {sport}: {e}")

    return all_matches
