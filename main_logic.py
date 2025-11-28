# main_logic.py

import os
import json
from typing import List, Dict

from arbitrage.calculator import check_surebet, calculate_stakes
from utils import calcular_lucro
from config import BANKROLL
from odds_providers.api_football import get_matches_with_odds


LOG_PATH = "logs/results.json"


def salvar_log(resultados: List[Dict]) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)


def calcular_s_margem(outcomes):
    S = sum(1/o["odd"] for o in outcomes)
    margem = (S - 1) * 100
    return S, margem


def calcular_stakes_quase_arbitragem(outcomes, bankroll):
    """
    Calcula stakes mesmo para S > 1.
    Mostra prejuízo de cada cenário.
    """
    S, _ = calcular_s_margem(outcomes)

    stakes = []
    for o in outcomes:
        weight = (1/o["odd"]) / S
        stake = bankroll * weight
        retorno = stake * o["odd"]
        stakes.append({
            "name": o["name"],
            "bookmaker": o["bookmaker"],
            "odd": o["odd"],
            "stake": round(stake, 2),
            "return_if_win": round(retorno, 2),
        })
    
    total = sum(s["stake"] for s in stakes)

    for s in stakes:
        s["loss_if_win"] = round(total - s["return_if_win"], 2)

    return stakes, total


def buscar_arbitragem() -> List[Dict]:
    matches = get_matches_with_odds()
    resultados = []

    for match in matches:
        outcomes = match.get("outcomes", [])
        if len(outcomes) < 2:
            continue

        # Pega a melhor odd de cada lado
        best = {}
        for o in outcomes:
            if o["name"] not in best or o["odd"] > best[o["name"]]["odd"]:
                best[o["name"]] = o
        
        best_list = list(best.values())
        if len(best_list) < 2:
            continue

        # Calcular S e margem da casa
        S, margem = calcular_s_margem(best_list)
        falta = S - 1

        # Checar arbitragem
        has_surebet, margin_sure = check_surebet(best_list)

        # Se é arbitragem real → stakes tradicionais
        if has_surebet:
            stakes = calculate_stakes(best_list, BANKROLL)
            investido, retorno, lucro = calcular_lucro(stakes)
        else:
            # stakes para estudo (quase arbitragem)
            stakes, investido = calcular_stakes_quase_arbitragem(best_list, BANKROLL)
            retorno = max(s["return_if_win"] for s in stakes)
            lucro = retorno - investido

        resultados.append({
            "league": match["league"],
            "home": match["home"],
            "away": match["away"],
            "market": match["market"],

            "S": round(S, 4),
            "margem_casa": round(margem, 2),
            "falta": round(falta, 4),

            "has_surebet": has_surebet,
            "margin_sure": round(margin_sure, 2),

            "stakes": stakes,
            "investido": round(investido, 2),
            "retorno": round(retorno, 2),
            "lucro": round(lucro, 2),
        })

    resultados.sort(key=lambda x: x["S"])

    top = resultados[:20]
    salvar_log(top)
    return top
