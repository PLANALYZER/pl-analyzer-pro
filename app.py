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
    if password == "BOMBER2026":
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 2. CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - FORMA CASA/TRASFERTA")

# --- 3. MAPPE ---
league_map = {"Serie A (IT)": "SA", "Premier League (UK)": "PL", "La Liga (ES)": "PD", "Bundesliga (DE)": "BL1"}
api_league_map = {"Serie A (IT)": "soccer_italy_serie_a", "Premier League (UK)": "soccer_epl", "La Liga (ES)": "soccer_spain_la_liga", "Bundesliga (DE)": "soccer_germany_bundesliga"}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI"):
    with st.spinner("Analisi performance casa/trasferta..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Classifica
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # 2. Recupero Match finiti (Finestra temporale ampia per trovare 5 match specifici)
        date_from = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        res_history = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/matches?dateFrom={date_from}&dateTo={date_to}&status=FINISHED", headers=headers).json()
        
        # 3. Recupero Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and "matches" in res_history:
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
                    h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        h_id = h_s['team']['id']
                        a_id = a_s['team']['id']

                        # --- LOGICA FORMA SPECIFICA CASA/TRASFERTA ---
                        
                        # 1. Calcolo Forma CASA (Solo match giocati in casa)
                        def get_home_form(t_id):
                            pts = 0
                            h_matches = [m for m in match_history if m['homeTeam']['id'] == t_id]
                            for m in h_matches[-5:]:
                                if m['score']['winner'] == 'HOME_TEAM': pts += 3
                                elif m['score']['winner'] == 'DRAW': pts += 1
                            return pts

                        # 2. Calcolo Forma TRASFERTA (Solo match giocati fuori)
                        def get_away_form(t_id):
                            pts = 0
                            a_matches = [m for m in match_history if m['awayTeam']['id'] == t_id]
                            for m in a_matches[-5:]:
                                if m['score']['winner'] == 'AWAY_TEAM': pts += 3
                                elif m['score']['winner'] == 'DRAW': pts += 1
                            return pts

                        f_h = get_home_form(h_id)
                        f_a = get_away_form(a_id)

                        # --- CALCOLO xG ---
                        h_p, h_gf, h_gs = h_s['playedGames'], h_s['goalsFor'], h_s['goalsAgainst']
                        a_p, a_gf, a_gs = a_s['playedGames'], a_s['goalsFor'], a_s['goalsAgainst']
                        
                        xh = ((h_gf/h_p)/avg_league) * ((a_gs/a_p)/avg_league) * avg_league
                        xa = ((a_gf/a_p)/avg_league) * ((h_gs/h_p)/avg_league) * avg_league
                        txg = xh + xa

                        with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric("FORMA IN CASA", f"{f_h}/15")
                                st.caption("Ultime 5 tra le mura amiche")
                            with c2:
                                st.metric("FORMA FUORI", f"{f_a}/15")
                                st.caption("Ultime 5 in trasferta")
                            with c3:
                                try:
                                    q = match['bookmakers'][0]['markets'][0]['outcomes']
                                    o25 = next(o['price'] for o in q if o['name']=='Over' and o['point']==2.5)
                                    st.metric("QUOTA O2.5", o25)
                                except: st.write("Quota N/D")

                            st.divider()
                            # PRONOSTICO BASE
                            if txg > 2.5: st.success("🎯 CONSIGLIO: OVER 2.5")
                            if f_h >= 12: st.info(f"🏟️ {h_n} è un fortino in casa!")
                            if f_a >= 12: st.info(f"🚀 {a_n} corre forte fuori casa!")
