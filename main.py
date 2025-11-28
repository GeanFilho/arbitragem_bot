# main.py

from odds_providers.exemplo_api import get_odds
from arbitrage.calculator import check_surebet, calculate_stakes
from config import BANKROLL, MIN_MARGIN

def main():
    matches = get_odds()
    print(f"\n📌 Total de partidas encontradas: {len(matches)}\n")

    found_any = False  # para saber se achou alguma arbitragem

    for match in matches:
        # Pega a melhor odd de cada resultado
        best = {}

        for o in match["outcomes"]:
            result_name = o["name"]  # "Home", "Away", "Draw"
            if result_name not in best or o["odd"] > best[result_name]["odd"]:
                best[result_name] = o

        if len(best) < 2:
            continue

        outcomes_list = list(best.values())
        has_surebet, margin = check_surebet(outcomes_list)

        if has_surebet and margin >= MIN_MARGIN:
            found_any = True
            print("===========================================")
            print(f"🏆 Arbitragem encontrada!")
            print(f"🏟️ Liga: {match['league']}")
            print(f"⚽ Jogo: {match['home']} x {match['away']}")
            print(f"💰 Margem de lucro: {margin:.2f}%\n")

            stakes = calculate_stakes(outcomes_list, BANKROLL)

            for s in stakes:
                print(
                    f"→ Apostar R$ {s['stake']} em '{s['name']}' "
                    f"na casa {s['bookmaker']} (odd {s['odd']})"
                )
                print(f"   Retorno se ganhar: R$ {s['return_if_win']}\n")

    if not found_any:
        print("❌ Nenhuma arbitragem encontrada nesta varredura.")

    print("\n✔️ Finalizado. Programa encerrado.\n")


if __name__ == "__main__":
    main()
