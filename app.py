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
            st.error("Licenza Errata")
    st.stop()

# --- 2. CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - 7 PUNTI (RELOADED)")

# --- 3. MAPPE ---
league_map = {"Serie A (IT)": "SA", "Premier League (UK)": "PL", "La Liga (ES)": "PD", "Bundesliga (DE)": "BL1"}
api_league_map = {"Serie A (IT)": "soccer_italy_serie_a", "Premier League (UK)": "soccer_epl", "La Liga (ES)": "soccer_spain_la_liga", "Bundesliga (DE)": "soccer_germany_bundesliga"}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI"):
    with st.spinner("Caricamento dati reali..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # Chiamata alla classifica generale (Più sicura alla 27esima giornata)
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and isinstance(res_odds, list):
            # Prendiamo la classifica 'TOTAL' che è garantito contenga i dati alla 27°
            table = res_stats['standings'][0]['table']
            
            # --- PUNTO 5: MEDIE REALI CAMPIONATO ---
            total_goals = sum(t.get('goalsFor', 0) for t in table)
            total_games = sum(t.get('playedGames', 0) for t in table) / 2
            avg_league = total_goals / (total_games if total_games > 0 else 1)

            team_db = {t['team']['name']: t for t in table}

            for match in res_odds:
                h_n, a_n = match['home_team'], match['away_team']
                
                # Cerchiamo le squadre nel database con un match più flessibile
                h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                if h_s and a_s:
                    # --- PUNTO 6: ESTRAZIONE DATI (OVERALL SE HOME/AWAY MANCA) ---
                    # Se l'API non dà il dettaglio casa/trasferta, usiamo i totali per non bloccare il calcolo
                    h_p = h_s.get('playedGames', 1)
                    h_gf = h_s.get('goalsFor', 0)
                    h_gs = h_s.get('goalsAgainst', 0)
                    
                    a_p = a_s.get('playedGames', 1)
                    a_gf = a_s.get('goalsFor', 0)
                    a_gs = a_s.get('goalsAgainst', 0)

                    # --- PUNTO 7: CALCOLO FORMA (BASATO SU STRINGA FORM) ---
                    f_h_str = h_s.get('form', '') or ''
                    f_a_str = a_s.get('form', '') or ''
                    pts_h = (f_h_str.replace(',','')[-5:].count('W')*3) + (f_h_str.replace(',','')[-5:].count('D')*1)
                    pts_a = (f_a_str.replace(',','')[-5:].count('W')*3) + (f_a_str.replace(',','')[-5:].count('D')*1)

                    # --- CALCOLO xG (ALGORITMO 7 PUNTI) ---
                    xh = ((h_gf/h_p)/avg_league) * ((a_gs/a_p)/avg_league) * avg_league
                    xa = ((a_gf/a_p)/avg_league) * ((h_gs/h_p)/avg_league) * avg_league
                    txg = xh + xa

                    with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**CASA: {h_n}**")
                            st.metric("Punti Forma", f"{pts_h}/15")
                            st.metric("xG Squadra", f"{xh:.2f}")
                            st.write(f"Gol Fatti: {h_gf}")
                        with col2:
                            st.write(f"**OSPITE: {a_n}**")
                            st.metric("Punti Forma", f"{pts_a}/15")
                            st.metric("xG Squadra", f"{xa:.2f}")
                            st.write(f"Gol Fatti: {a_gf}")
                        with col3:
                            try:
                                q = match['bookmakers
