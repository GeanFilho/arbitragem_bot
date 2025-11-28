# main_logic.py

from odds_providers.exemplo_api import get_odds
from arbitrage.calculator import check_surebet, calculate_stakes
from utils import calcular_lucro
from config import BANKROLL, MIN_MARGIN
import json, os
from datetime import datetime

def salvar_log(resultados):
    os.makedirs("logs", exist_ok=True)
    with open("logs/results.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)


def buscar_arbitragem():
    matches = get_odds()
    resultados = []

    for match in matches:
        best = {}

        for o in match["outcomes"]:
            name = o["name"]
            if name not in best or o["odd"] > best[name]["odd"]:
                best[name] = o

        if len(best) < 2:
            continue

        outcomes_list = list(best.values())
        has, margin = check_surebet(outcomes_list)

        if has and margin >= MIN_MARGIN:
            stakes = calculate_stakes(outcomes_list, BANKROLL)
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

    # salva log
    salvar_log(resultados)

    # ordenar por maior lucro
    resultados.sort(key=lambda x: x["lucro"], reverse=True)

    return resultados
