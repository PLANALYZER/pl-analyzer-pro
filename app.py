import requests
import math
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# ID Leghe richieste (Serie A, B, C, Premier, Championship, L1, L2, Bundesliga, LaLiga, Ligue1, Portogallo, Svizzera, Olanda, Bulgaria, Danimarca)
LEAGUE_IDS = [135, 136, 137, 39, 40, 41, 42, 78, 140, 61, 94, 207, 208, 88, 89, 172, 119]

def get_poisson_probability(lmbda, k_min, k_max):
    """Calcola la probabilità che i gol siano compresi nel range Multigol [k_min, k_max]"""
    prob = 0
    for k in range(k_min, k_max + 1):
        prob += (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)
    return prob * 100

def analyze_match(fixture_id):
    # 1. Recupero Statistiche (Filtrate Casa/Fuori)
    # Parametri: Goals Scored/Conceded, Corners, Fouls, Asian Odds Trend
    # 2. Calcolo xG (Expected Goals) basato su medie storiche stagionali
    xg_home = 1.75  # Esempio dato API
    xg_away = 1.15  # Esempio dato API
    
    # --- LOGICA PRONOSTICI BASATA SUI TUOI PARAMETRI ---
    results = {}
    
    # Multigol 1-3 Casa
    results['MG_1-3_C'] = get_poisson_probability(xg_home, 1, 3)
    # Multigol 1-2 Ospite
    results['MG_1-2_O'] = get_poisson_probability(xg_away, 1, 2)
    # Multigol 2-4 Casa
    results['MG_2-4_C'] = get_poisson_probability(xg_home, 2, 4)
    # Over 2.5
    results['Over_2.5'] = (1 - get_poisson_probability(xg_home + xg_away, 0, 2)) * 100
    
    return results

# Il loop principale scaricherà i match delle prossime 48H per ogni LEAGUE_ID
