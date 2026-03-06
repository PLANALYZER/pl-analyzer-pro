import streamlit as st
import requests
from datetime import datetime, timedelta

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

st.title("⚽ ANALYZER PRO - FIX FORMA REALE")

# --- 3. MAPPE ---
league_map = {"Serie A (IT)": "SA", "Premier League (UK)": "PL", "La Liga (ES)": "PD", "Bundesliga (DE)": "BL1"}
api_league_map = {"Serie A (IT)": "soccer_italy_serie_a", "Premier League (UK)": "soccer_epl", "La Liga (ES)": "soccer_spain_la_liga", "Bundesliga (DE)": "soccer_germany_bundesliga"}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI"):
    with st.spinner("Sincronizzazione dati in corso..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # Chiamata Classifica
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # Chiamata Risultati (Ultimi 45 giorni per essere sicuri di avere 5 partite)
        date_from = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        res_history = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/matches?dateFrom={date_from}&dateTo={date_to}", headers=headers).json()
        
        # Chiamata Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and "matches" in res_history and isinstance(res_odds, list):
            table = res_stats['standings'][0]['table']
            match_history = res_history['matches']
            
            # Media gol campionato
            total_g = sum(t.get('goalsFor', 0) for t in table)
            total_p = sum(t.get('playedGames', 0) for t in table) / 2
            avg_league = total_g / total_p if total_p > 0 else 2.5

            team_db = {t['team']['name']: t for t in table}
            ora_lim = datetime.utcnow() + timedelta(hours=48)

            for match in res_odds:
                m_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                
                if datetime.utcnow() <= m_time <= ora_lim:
                    h_n, a_n = match['home_team'], match['away_team']
                    
                    # --- TROVA TEAM CON SMART MATCH (Risolve il problema Juventus/Napoli) ---
                    h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        h_real_name = h_s['team']['name']
                        a_real_name = a_s['team']['name']

                        # --- FUNZIONE CALCOLO FORMA REALE ---
                        def calc_form_smart(t_name):
                            pts = 0
                            # Filtra i match cercando il nome nel database storico
                            t_m = [m for m in match_history if (t_name == m['homeTeam']['name'] or t_name == m['awayTeam']['name']) and m['status'] == 'FINISHED']
                            for m in t_m[-5:]: 
                                win = m['score']['winner']
                                if win == 'DRAW': pts += 1
                                elif (win == 'HOME_TEAM' and m['homeTeam']['name'] == t_name) or (win == 'AWAY_TEAM' and m['awayTeam']['name'] == t_name):
                                    pts += 3
                            return pts

                        f_h = calc_form_smart(h_real_name)
                        f_a = calc_form_smart(a_real_name)

                        # --- CALCOLO xG ---
                        h_p, h_gf, h_gs = h_s['playedGames'], h_s['goalsFor'], h_s['goalsAgainst']
                        a_p, a_gf, a_gs = a_s['playedGames'], a_s['goalsFor'], a_s['goalsAgainst']
                        
                        xh = ((h_gf/h_p)/avg_league) * ((a_gs/a_p)/avg_league) * avg_league
                        xa = ((a_gf/a_p)/avg_league) * ((h_gs/h_p)/avg_league) * avg_league
                        txg = xh + xa

                        with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric(f"FORMA {h_n.upper()}", f"{f_h}/15")
                                st.write(f"Potenziale Casa: {xh:.2f}")
                            with c2:
                                st.metric(f"FORMA {a_n.upper()}", f"{f_a}/15")
                                st.write(f"Potenziale Ospite: {xa:.2f}")
                            with c3:
                                try:
                                    q = match['bookmakers'][0]['markets'][0]['outcomes']
                                    o25 = next(o['price'] for o in q if o['name']=='Over' and o['point']==2.5)
                                    st.metric("QUOTA O2.5", o25)
                                except: st.write("Quota N/D")

                            st.divider()
                            # PRONOSTICO INTEGRATO
                            if txg > 2.5: st.success("🎯 CONSIGLIO: OVER 2.5")
                            elif txg < 2.1: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                            if f_h >= 10: st.info(f"🔥 {h_n} è in gran forma!")
