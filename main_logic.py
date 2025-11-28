# main_logic.py (GLOBAL)

import os
import json
import time
from datetime import datetime
from arbitrage.calculator import check_surebet, calculate_stakes
from utils import calcular_lucro

from odds_providers.api_football import get_fixtures, get_odds_for_fixture
from odds_providers.football_data import get_matches_from_league

CACHE_GLOBAL = "cache/global_odds.json"
CACHE_TIME = 60 * 10  # 10 minutos

def salvar_cache(data):
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_GLOBAL, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def carregar_cache():
    if os.path.exists(CACHE_GLOBAL):
        mod = os.path.getmtime(CACHE_GLOBAL)
        if time.time() - mod < CACHE_TIME:
            with open(CACHE_GLOBAL, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def normalizar_api_football():
    """
    Puxa TODOS os jogos do dia em todas as ligas com odds disponíveis.
    """

    fixtures = get_fixtures()

    if fixtures.get("response") is None:
        return []

    normalizados = []

    for f in fixtures["response"]:
        fixture_id = f["fixture"]["id"]
        league = f["league"]["name"]
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]

        # pegar odds do fixture
        odds = get_odds_for_fixture(fixture_id)

        if odds.get("response") is None or len(odds["response"]) == 0:
            continue

        # pegar mercado 1x2
        for bkm in odds["response"]:
            for b in bkm["bookmakers"]:
                for mk in b["bets"]:
                    if mk["name"] == "Match Winner":
                        outcomes = []
                        for o in mk["values"]:
                            outcomes.append({
                                "name": o["value"],  # Home / Draw / Away
                                "odd": float(o["odd"]),
                                "bookmaker": b["name"]
                            })

                        normalizados.append({
                            "league": league,
                            "home": home,
                            "away": away,
                            "outcomes": outcomes
                        })
    return normalizados



def normalizar_football_data():
    """
    Puxa odds extras de ligas europeias importantes.
    """
    ligas = ["PL", "BL1", "SA", "PD", "FL1", "CL"]  # Premier League, Bundesliga, etc.

    normalizados = []

    for lg in ligas:
        data = get_matches_from_league(lg)

        if "matches" not in data:
            continue

        for m in data["matches"]:
            if "odds" not in m or not m["odds"]:
                continue

            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]
            league = m["competition"]["name"]

            if "1X2" not in m["odds"]:
                continue

            market = m["odds"]["1X2"]
            outcomes = []

            for res in market:
                outcomes.append({
                    "name": res["outcome"],
                    "odd": float(res["odd"]),
                    "bookmaker": res.get("company", "FD")
                })

            normalizados.append({
                "league": league,
                "home": home,
                "away": away,
                "outcomes": outcomes
            })

    return normalizados



def buscar_arbitragem():
    """
    Scanner global unificando API-Football + Football-Data
    """

    # usar cache
    cache = carregar_cache()
    if cache:
        jogos = cache
    else:
        jogos_apifootball = normalizar_api_football()
        jogos_fd = normalizar_football_data()
        jogos = jogos_apifootball + jogos_fd
        salvar_cache(jogos)

    resultados = []

    for match in jogos:
        if len(match["outcomes"]) < 2:
            continue

        # pegar melhores odds por resultado
        best = {}
        for o in match["outcomes"]:
            name = o["name"]
            if name not in best or o["odd"] > best[name]["odd"]:
                best[name] = o

        outcomes_list = list(best.values())

        if len(outcomes_list) < 2:
            continue

        has, margin = check_surebet(outcomes_list)

        if has:
            stakes = calculate_stakes(outcomes_list, 1000) # bankroll fixo
            investido, retorno, lucro = calcular_lucro(stakes)

            resultados.append({
                "league": match["league"],
                "home": match["home"],
                "away": match["away"],
                "margin": margin,
                "investido": investido,
                "retorno": retorno,
                "lucro": lucro,
                "stakes": stakes
            })

    # ranking por lucro líquido
    resultados.sort(key=lambda x: x["lucro"], reverse=True)

    return resultados
