# arbitrage/calculator.py

from typing import List, Dict, Tuple

def implied_probability(odd: float) -> float:
    """Retorna a probabilidade implícita da odd."""
    return 1.0 / odd


def check_surebet(outcomes: List[Dict]) -> Tuple[bool, float]:
    """
    Verifica se existe arbitragem.
    Retorna (True/False, margem_em_%)
    """
    S = sum(implied_probability(o["odd"]) for o in outcomes)
    if S < 1:
        margin = (1 - S) * 100
        return True, margin
    return False, 0.0


def calculate_stakes(outcomes: List[Dict], bankroll: float) -> List[Dict]:
    """
    Calcula quanto apostar em cada resultado da arbitragem.
    """
    inv_sum = sum(implied_probability(o["odd"]) for o in outcomes)
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
