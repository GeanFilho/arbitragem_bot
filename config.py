import os

API_KEY = os.getenv("API_KEY")  # Pega a chave pelo painel do Render

BANKROLL = 1000.0
MIN_MARGIN = 1.0

SPORTS = [
    "soccer_brazil_campeonato",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_germany_bundesliga",
    "soccer_uefa_champs_league",
    "soccer_argentina_primera_division",
    "soccer_usa_mls"
]

REGIONS = "eu"
MARKETS = "h2h"
