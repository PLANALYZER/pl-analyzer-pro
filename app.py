import streamlit as st
import requests

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO - 7 Punti", layout="wide")

# --- PROTEZIONE ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    if st.text_input("Inserisci Password:", type="password") == "BOMBER2026":
        if st.button("Sblocca Software"):
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - ALGORITMO 7 PUNTI")

league_map = {"soccer_italy_serie_a": "SA", "soccer_epl": "PL", "soccer_spain_la_liga": "PD", "soccer_germany_bundesliga": "BL1"}
camp_scelto = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI TOTALE"):
    with st.spinner("Calcolando medie e forma casa/trasferta..."):
        
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        # Chiamata alla classifica dettagliata (HOME/AWAY)
        url_stats = f"https://api.football-data.org/v4/competitions/{league_map[camp_scelto]}/standings"
        stats_res = requests.get(url_stats, headers=headers).json()

        # Chiamata alle quote
        url_odds = f"https://api.the-odds-api.com/v4/sports/{camp_scelto}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        odds_res = requests.get(url_odds).json()

        if "standings" in stats_res:
            # Estraiamo la classifica generale per trovare i dati casa/trasferta
            table = stats_res['standings'][0]['table']
            
            # --- PUNTO .5: MEDIE CAMPIONATO (CORRETTO) ---
            # Calcoliamo le medie gol casa/trasferta basandoci sulla colonna corretta dell'API
            total_matches = sum(t['playedGames'] for t in table) / 2
            avg_league_h = sum(t['home']['goalsFor'] if 'home' in t else 0 for t in table) / (total_matches if total_matches >
