# main_logic.py

import os
import json
from typing import List, Dict

from arbitrage.calculator import check_surebet, calculate_stakes
from utils import calcular_lucro
from config import BANKROLL, MIN_MARGIN
from odds_providers.api_football import get_matches_with_odds


LOG_PATH = "logs/results.json"


def salvar_log(resultados: List[Dict]) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)


def buscar_arbitragem() -> List[Dict]:
    """
    Scanner global usando API-Football, em múltiplos mercados:
    - 1x2
    - Over/Under
    - Handicap
    - BTTS
    - Double Chance
    - Draw No Bet
    """

    matches = get_matches_with_odds()
    resultados: List[Dict] = []

    for match in matches:
        outcomes = match.get("outcomes", [])
        if len(outcomes) < 2:
            continue

        # pegar a melhor odd por nome de resultado (Home / Away / Over 2.5 / etc.)
        best: Dict[str, Dict] = {}
        for o in outcomes:
            name = o["name"]
            if name not in best or o["odd"] > best[name]["odd"]:
                best[name] = o

        best_list = list(best.values())
        if len(best_list) < 2:
            continue

        has_surebet, margin = check_surebet(best_list)

        if not has_surebet or margin < MIN_MARGIN:
            continue

        stakes = calculate_stakes(best_list, BANKROLL)
        if not stakes:
            continue

        investido, retorno, lucro = calcular_lucro(stakes)

        resultados.append({
            "league": match["league"],
            "home": match["home"],
            "away": match["away"],
            "market": match.get("market", "desconhecido"),
            "margin": round(margin, 2),
            "investido": investido,
            "retorno": retorno,
            "lucro": lucro,
            "stakes": stakes,
        })

    # ordena pelo lucro líquido
    resultados.sort(key=lambda x: x["lucro"], reverse=True)

    # salva log
    salvar_log(resultados)

    return resultados
