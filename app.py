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
    with st.spinner("Calcolo forma e xG reali..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Dati (Classifica + Match finiti + Quote)
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        res_matches = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/matches?status=FINISHED", headers=headers).json()
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and "matches" in res_matches and isinstance(res_odds, list):
            table = res_stats['standings'][0]['table']
            all_finished = res_matches['matches']
            
            # --- FUNZIONE LOGICA FORMA (PUNTO 7) ---
            def get_real_form(team_name, matches):
                pts = 0
                # Filtra solo i match di QUELLA squadra e prendi gli ultimi 5
                team_m = [m for m in matches if m['homeTeam']['name'] == team_name or m['awayTeam']['name'] == team_name]
                last_5 = team_m[-5:]
                for m in last_5:
                    win = m['score']['winner']
                    if win == 'DRAW': pts += 1
                    elif (win == 'HOME_TEAM' and m['homeTeam']['name'] == team_name) or \
                         (win == 'AWAY_TEAM' and m['awayTeam']['name'] == team_name):
                        pts += 3
                return pts

            # --- MEDIE CAMPIONATO ---
            total_g = sum(t.get('goalsFor', 0) for t in table)
            total_p = sum(t.get('playedGames', 0) for t in table) / 2
            avg_l = total_g / total_p if total_p > 0 else 2.5
            
            team_db = {t['team']['name']: t for t in table}
            ora_lim = datetime.utcnow() + timedelta(hours=48)

            for match in res_odds:
                m_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                
                if datetime.utcnow() <= m_time <= ora_lim:
                    h_n, a_n = match['home_team'], match['away_team']
                    # Match nomi flessibile
                    h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        # Dati Statistici
                        h_p, h_gf, h_gs = h_s['playedGames'], h_s['goalsFor'], h_s['goalsAgainst']
                        a_p, a_gf, a_gs = a_s['playedGames'], a_s['goalsFor'], a_s['goalsAgainst']

                        # CALCOLO FORMA REALE
                        f_h = get_real_form(h_s['team']['name'], all_finished)
                        f_a = get_real_form(a_s['team']['name'], all_finished)

                        # CALCOLO xG (PUNTO 6)
                        xh = ((h_gf/h_p)/avg_l) * ((a_gs/a_p)/avg_l) * avg_l
                        xa = ((a_gf/a_p)/avg_l) * ((h_gs/h_p)/avg_l) * avg_l
                        txg = xh + xa

                        with st.expander(f"📅 {m_time.strftime('%d/%m %H:%M')} | {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.write("**HOME**")
                                st.metric("Forma (5 p.)", f"{f_h}/15")
                                st.metric("xG", f"{xh:.2f}")
                            with c2:
                                st.write("**AWAY**")
                                st.metric("Forma (5 p.)", f"{f_a}/15")
                                st.metric("xG", f"{xa:.2f}")
                            with c3:
                                try:
                                    q_list = match['bookmakers'][0]['markets'][0]['outcomes']
                                    o25 = next(o['price'] for o in q_list if o['name']=='Over' and o['point']==2.5)
                                    st.metric("Quota Over", o25)
                                except: st.write("Quota N/D")
                            
                            st.divider()
                            if txg > 2.5: st.success("🎯 CONSIGLIO: OVER 2.5")
                            if f_h > 10 or f_a > 10: st.info("🔥 SQUADRA IN STRISCIA POSITIVA")

        else:
            st.error("Dati non disponibili. Controlla la connessione API.")
