# main_logic.py

from odds_providers.exemplo_api import get_odds
from arbitrage.calculator import check_surebet, calculate_stakes
from config import BANKROLL, MIN_MARGIN

def buscar_arbitragem():
    matches = get_odds()
    resultados = []

    for match in matches:
        best = {}

        for o in match["outcomes"]:
            result_name = o["name"]
            if result_name not in best or o["odd"] > best[result_name]["odd"]:
                best[result_name] = o

        if len(best) < 2:
            continue

        outcomes_list = list(best.values())
        has_surebet, margin = check_surebet(outcomes_list)

        if has_surebet and margin >= MIN_MARGIN:
            stakes = calculate_stakes(outcomes_list, BANKROLL)

            resultados.append({
                "league": match["league"],
                "home": match["home"],
                "away": match["away"],
                "margin": round(margin, 2),
                "stakes": stakes
            })

    return resultados
