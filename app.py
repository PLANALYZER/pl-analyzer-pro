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

st.title("⚽ ANALYZER PRO - ALGORITMO COMPLETO 7 PUNTI")

# --- 3. MAPPE ---
league_map = {"Serie A (IT)": "SA", "Premier League (UK)": "PL", "La Liga (ES)": "PD", "Bundesliga (DE)": "BL1"}
api_league_map = {"Serie A (IT)": "soccer_italy_serie_a", "Premier League (UK)": "soccer_epl", "La Liga (ES)": "soccer_spain_la_liga", "Bundesliga (DE)": "soccer_germany_bundesliga"}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI COMPLETA"):
    with st.spinner("Analisi dati e trend quote in corso..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Classifica
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # 2. Recupero Match finiti (Finestra 120gg per avere dati casa/fuori sufficienti)
        d_from = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
        d_to = datetime.now().strftime('%Y-%m-%d')
        res_history = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/matches?dateFrom={d_from}&dateTo={d_to}&status=FINISHED", headers=headers).json()
        
        # 3. Recupero Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and "matches" in res_history:
            table = res_stats['standings'][0]['table']
            match_history = res_history['matches']
            
            # Media gol campionato reale
            total_g = sum(t.get('goalsFor', 0) for t in table)
            total_p = sum(t.get('playedGames', 0) for t in table) / 2
            avg_league = total_g / total_p if total_p > 0 else 2.5

            team_db = {t['team']['name']: t for t in table}
            ora_lim = datetime.utcnow() + timedelta(hours=48)

            for match in res_odds:
                m_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                
                if datetime.utcnow() <= m_time <= ora_lim:
                    h_n, a_n = match['home_team'], match['away_team']
                    h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        h_id, a_id = h_s['team']['id'], a_s['team']['id']

                        # --- FORMA SPECIFICA (CASA/FUORI) ---
                        def get_h_form(tid):
                            pts = 0
                            ms = [m for m in match_history if m['homeTeam']['id'] == tid][-5:]
                            for m in ms:
                                if m['score']['winner'] == 'HOME_TEAM': pts += 3
                                elif m['score']['winner'] == 'DRAW': pts += 1
                            return pts

                        def get_a_form(tid):
                            pts = 0
                            ms = [m for m in match_history if m['awayTeam']['id'] == tid][-5:]
                            for m in ms:
                                if m['score']['winner'] == 'AWAY_TEAM': pts += 3
                                elif m['score']['winner'] == 'DRAW': pts += 1
                            return pts

                        f_h, f_a = get_h_form(h_id), get_a_form(a_id)

                        # --- CALCOLO xG (FIX VARIABILI) ---
                        h_p, h_gf, h_gs = h_s['playedGames'], h_s['goalsFor'], h_s['goalsAgainst']
                        a_p, a_gf, a_gs = a_s['playedGames'], a_s['goalsFor'], a_s['goalsAgainst']
                        
                        # Evita divisione per zero
                        h_p = h_p if h_p > 0 else 1
                        a_p = a_p if a_p > 0 else 1

                        xh = ((h_gf/h_p)/avg_league) * ((a_gs/a_p)/avg_league) * avg_league
                        xa = ((a_gf/a_p)/avg_league) * ((h_gs/h_p)/avg_league) * avg_league
                        txg = xh + xa

                        with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric("FORMA CASA (in Casa)", f"{f_h}/15")
                                st.write(f"xG Casa: {xh:.2f}")
                            with c2:
                                st.metric("FORMA OSPITE (Fuori)", f"{f_a}/15")
                                st.write(f"xG Ospite: {xa:.2f}")
                            with c3:
                                try:
                                    q_data = match['bookmakers'][0]['markets'][0]['outcomes']
                                    o25 = next(o['price'] for o in q_data if o['name']=='Over' and o['point']==2.5)
                                    st.metric("QUOTA O2.5", o25)
                                    if o25 < 1.75 and txg > 2.6: st.success("📉 TREND: DOWN (VALORE)")
                                except: st.write("Quota N/D")

                            st.divider()
                            # --- PRONOSTICI ---
                            p1, p2, p3 = st.columns(3)
                            with p1:
                                if txg > 2.6: st.success("🎯 OVER 2.5")
                                elif txg < 2.1: st.warning("🛡️ UNDER 2.5")
                                else: st.info("⚖️ NO BET")
                            with p2:
                                if xh > 0.85 and xa > 0.85: st.success("⚽ GOAL")
                                else: st.info("🚫 NO GOAL")
                            with p3:
                                if (f_h + f_a) > 18 and txg > 2.7: st.success("🔥 TOP COMBO")
                                elif f_h > 12: st.info("🏟️ FORTINO CASA")
