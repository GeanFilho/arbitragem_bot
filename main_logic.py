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
    """Calcula soma S e margem da casa."""
    inv_probs = [1 / o["odd"] for o in outcomes]
    S = sum(inv_probs)
    margem = (S - 1) * 100
    return S, margem


def buscar_arbitragem() -> List[Dict]:
    """
    Agora retorna SEMPRE os 20 mercados mais favoráveis
    - Com arbitragem real (S < 1)
    - Ou quase arbitragem (S > 1 mas perto)
    """

    matches = get_matches_with_odds()
    resultados: List[Dict] = []

    for match in matches:
        outcomes = match.get("outcomes", [])
        if len(outcomes) < 2:
            continue

        # Pega a melhor odd de cada resultado (melhor por nome)
        best = {}
        for o in outcomes:
            name = o["name"]
            if name not in best or o["odd"] > best[name]["odd"]:
                best[name] = o

        best_list = list(best.values())
        if len(best_list) < 2:
            continue

        # calcular arbitragem e variáveis do mercado
        has_surebet, margin_sure = check_surebet(best_list)

        S, margem_casa = calcular_s_margem(best_list)
        falta = S - 1  # quanto falta pra virar arbitragem

        stakes = calculate_stakes(best_list, BANKROLL) if has_surebet else []

        investido = retorno = lucro = 0
        if stakes:
            investido, retorno, lucro = calcular_lucro(stakes)

        resultados.append({
            "league": match["league"],
            "home": match["home"],
            "away": match["away"],
            "market": match["market"],

            "S": round(S, 4),
            "margem_casa": round(margem_casa, 2),
            "falta": round(falta, 4),

            "has_surebet": has_surebet,
            "margin_sure": round(margin_sure, 2),

            "stakes": stakes,
            "investido": investido,
            "retorno": retorno,
            "lucro": lucro,
        })

    # ordenar pelas melhores oportunidades
    resultados.sort(key=lambda x: x["S"])

    # top 20
    top = resultados[:20]

    salvar_log(top)
    return top
