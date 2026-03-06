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

st.title("⚽ ANALYZER PRO - FILTRO 48H & REALI xG")

# --- 3. MAPPE ---
league_map = {"Serie A (IT)": "SA", "Premier League (UK)": "PL", "La Liga (ES)": "PD", "Bundesliga (DE)": "BL1"}
api_league_map = {"Serie A (IT)": "soccer_italy_serie_a", "Premier League (UK)": "soccer_epl", "La Liga (ES)": "soccer_spain_la_liga", "Bundesliga (DE)": "soccer_germany_bundesliga"}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI"):
    with st.spinner("Filtrando partite prossime 48 ore..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Classifica
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # 2. Recupero Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in res_stats and isinstance(res_odds, list):
            table = res_stats['standings'][0]['table']
            
            # --- MEDIE CAMPIONATO CORRETTE ---
            total_goals = sum(t.get('goalsFor', 0) for t in table)
            total_matches = sum(t.get('playedGames', 0) for t in table) / 2
            avg_league = total_goals / total_matches if total_matches > 0 else 2.5
            
            team_db = {t['team']['name']: t for t in table}
            
            # --- FILTRO TEMPORALE (OGGI + DOMANI) ---
            ora_limite = datetime.utcnow() + timedelta(hours=48)
            
            count_matches = 0
            for match in res_odds:
                match_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                
                # Se la partita è entro le prossime 48 ore
                if datetime.utcnow() <= match_time <= ora_limite:
                    h_n, a_n = match['home_team'], match['away_team']
                    h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        count_matches += 1
                        # Dati totali (più stabili alla 27esima)
                        h_p, h_gf, h_gs = h_s['playedGames'], h_s['goalsFor'], h_s['goalsAgainst']
                        a_p, a_gf, a_gs = a_s['playedGames'], a_s['goalsFor'], a_s['goalsAgainst']

                        # --- CALCOLO FORMA ROBUSTO ---
                        def get_pts(form_str):
                            if not form_str: return 0
                            clean_form = form_str.replace(',', '')[-5:]
                            return (clean_form.count('W')*3) + (clean_form.count('D')*1)

                        pts_h = get_pts(h_s.get('form', ''))
                        pts_a = get_pts(a_s.get('form', ''))

                        # --- ALGORITMO xG POTENZIATO ---
                        # Attacco Casa / Media * Difesa Ospite / Media * Media
                        xh = ((h_gf/h_p)/avg_league) * ((a_gs/a_p)/avg_league) * avg_league
                        xa = ((a_gf/a_p)/avg_league) * ((h_gs/h_p)/avg_league) * avg_league
                        txg = xh + xa

                        with st.expander(f"📅 {match_time.strftime('%d/%m %H:%M')} | {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.write("**HOME**")
                                st.metric("Forma (5 p.)", f"{pts_h}/15")
                                st.metric("Potenziale Gol", f"{xh:.2f}")
                            with c2:
                                st.write("**AWAY**")
                                st.metric("Forma (5 p.)", f"{pts_a}/15")
                                st.metric("Potenziale Gol", f"{xa:.2f}")
                            with c3:
                                try:
                                    q = match['bookmakers'][0]['markets'][0]['outcomes']
                                    o25 = next(o['price'] for o in q if o['name']=='Over' and o['point']==2.5)
                                    st.metric("Quota Over 2.5", o25)
                                except: st.write("Quota N/D")

                            st.divider()
                            # LOGICA PRONOSTICI
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                if txg > 2.5: st.success("🎯 CONSIGLIO: OVER 2.5")
                                elif txg < 2.1: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                                else: st.info("⚖️ MATCH EQUILIBRATO")
                            with res_col2:
                                if xh > 0.7 and xa > 0.7: st.success("⚽ SEGNA ENTRAMBE (GOAL)")
            
            if count_matches == 0:
                st.info("Nessuna partita in programma nelle prossime 48 ore per questo campionato.")
        else:
            st.error("Errore nel recupero dati. Verifica le API Keys.")
