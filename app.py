import streamlit as st
import requests

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    password = st.text_input("Inserisci Licenza:", type="password")
    if st.button("Attiva Software"):
        if password == "BOMBER2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Licenza non valida.")
    st.stop()

# --- 2. CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - ALGORITMO INTEGRATO 7 PUNTI")

# --- 3. MAPPE CORRETTE (RIGA 38 SISTEMATA) ---
league_map = {
    "Serie A (IT)": "SA", 
    "Premier League (UK)": "PL", 
    "La Liga (ES)": "PD", 
    "Bundesliga (DE)": "BL1"
}

api_league_map = {
    "Serie A (IT)": "soccer_italy_serie_a",
    "Premier League (UK)": "soccer_epl",
    "La Liga (ES)": "soccer_spain_la_liga",
    "Bundesliga (DE)": "soccer_germany_bundesliga"
}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("AVVIA ANALISI"):
    with st.spinner("Calcolo xG e Analisi Forma..."):
        # Recupero Statistiche
        h_stats = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=h_stats).json()
        
        # Recupero Quote
        url_odds = f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        res_odds = requests.get(url_odds).json()

        if "standings" in res_stats and isinstance(res_odds, list):
            table = res_stats['standings'][0]['table']
            
            # PUNTO 5: MEDIE CAMPIONATO
            tot_h_g = sum(t.get('home', {}).get('goalsFor', 0) for t in table)
            tot_h_p = sum(t.get('home', {}).get('playedGames', 0
