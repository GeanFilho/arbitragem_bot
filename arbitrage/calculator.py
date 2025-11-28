# arbitrage/calculator.py

from typing import List, Dict, Tuple


def implied_probability(odd: float) -> float:
    """
    Probabilidade implícita da odd (modelo decimal).
    """
    return 1.0 / odd


def check_surebet(outcomes: List[Dict]) -> Tuple[bool, float]:
    """
    Verifica se há arbitragem em qualquer mercado,
    dado uma lista de resultados (outcomes) daquele mercado.

    Cada outcome deve ter:
      - "odd": float

    Retorna:
      (has_surebet: bool, margin_percent: float)
    """
    if len(outcomes) < 2:
        return False, 0.0

    inv_sum = sum(implied_probability(o["odd"]) for o in outcomes)

    if inv_sum < 1:
        margin = (1 - inv_sum) * 100
        return True, margin

    return False, 0.0


def calculate_stakes(outcomes: List[Dict], bankroll: float) -> List[Dict]:
    """
    Calcula quanto apostar em cada resultado para garantir retorno,
    dado um bankroll total.

    outcomes: lista de dicts com:
      - "name": nome do resultado (Home / Away / Over 2.5 / etc.)
      - "bookmaker": casa
      - "odd": odd decimal

    Retorna lista com:
      - name
      - bookmaker
      - odd
      - stake
      - return_if_win
    """
    inv_sum = sum(implied_probability(o["odd"]) for o in outcomes)

    if inv_sum <= 0:
        return []

    stakes = []

    for o in outcomes:
        p = implied_probability(o["odd"])
        stake = bankroll * (p / inv_sum)
        potential_return = stake * o["odd"]

        stakes.append({
            "name": o["name"],
            "bookmaker": o["bookmaker"],
            "odd": o["odd"],
            "stake": round(stake, 2),
            "return_if_win": round(potential_return, 2),
        })

    return stakes
