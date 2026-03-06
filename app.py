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

st.title("⚽ ANALYZER PRO - 7 PUNTI")

# --- 3. MAPPE CAMPIONATI ---
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

if st.button("ESEGUI ANALISI"):
    with st.spinner("Analisi dei dati in corso..."):
        
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        url_odds = f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        res_odds = requests.get(url_odds).json()

        if "standings" in res_stats and isinstance(res_odds, list):
            table = res_stats['standings'][0]['table']
            
            # --- PUNTO 5: MEDIE CAMPIONATO (CON PROTEZIONE) ---
            t_h_g, t_h_p, t_a_g, t_a_p = 0, 0, 0, 0
            for t in table:
                t_h_g += t.get('home', {}).get('goalsFor', 0)
                t_h_p += t.get('home', {}).get('playedGames', 0)
                t_a_g += t.get('away', {}).get('goalsFor', 0)
                t_a_p += t.get('away', {}).get('playedGames', 0)
            
            avg_h_l = t_h_g / t_h_p if t_h_p > 0 else 1.5
            avg_a_l = t_a_g / t_a_p if t_a_p > 0 else 1.2

            team_db = {t['team']['name']: t for t in table}

            for match in res_odds:
                h_n, a_n = match['home_team'], match['away_team']
                h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                if h_s and a_s:
                    # --- PUNTO 6: DATI CASA/TRASFERTA (CONTROLLO ZERO) ---
                    h_p = h_s.get('home', {}).get('playedGames', 0)
                    a_p = a_s.get('away', {}).get('playedGames', 0)
                    
                    if h_p > 0 and a_p > 0:
                        h_gf, h_gs = h_s['home']['goalsFor'], h_s['home']['goalsAgainst']
                        a_gf, a_gs = a_s['away']['goalsFor'], a_s['away']['goalsAgainst']

                        # --- PUNTO 7: FORMA ---
                        f_h_str = h_s.get('form', '') or ''
                        f_a_str = a_s.get('form', '') or ''
                        pts_h = (f_h_str.replace(',','')[-5:].count('W')*3) + (f_h_str.replace(',','')[-5:].count('D')*1)
                        pts_a = (f_a_str.replace(',','')[-5:].count('W')*3) + (f_a_str.replace(',','')[-5:].count('D')*1)

                        # --- CALCOLO XG (PROTEZIONE DIVISIONE) ---
                        xg_h = ((h_gf/h_p)/avg_h_l) * ((a_gs/a_p)/avg_h_l) * avg_h_l
                        xg_a = ((a_gf/a_p)/avg_a_l) * ((h_gs/h_p)/avg_a_l) * avg_a_l
                        txg = xg_h + xg_a

                        with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.write("**CASA**")
                                st.metric("Forma", f"{pts_h}/15")
                                st.metric("xG Pro", f"{xg_h:.2f}")
                            with c2:
                                st.write("**OSPITE**")
                                st.metric("Forma", f"{pts_a}/15")
                                st.metric("xG Pro", f"{xg_a:.2f}")
                            with c3:
                                try:
                                    q_list = match['bookmakers'][0]['markets'][0]['outcomes']
                                    quota = next(o['price'] for o in q_list if o['name']=='Over' and o['point']==2.5)
                                    st.write(f"Quota Over 2.5: {quota}")
                                    if quota < 1.75 and txg > 2.6: st.success("📉 TREND DOWN")
                                except: st.write("Quota N/D")

                            st.divider()
                            st.subheader("🎯 PRONOSTICO")
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                if txg > 2.6: st.success("OVER 2.5")
                                elif txg < 2.3: st.warning("UNDER 2.5")
                            with col_p2:
                                if xg_h > 0.9 and xg_a > 0.9: st.success("GOAL")
                                if (pts_h + pts_a) > 18: st.info("TOP FORM")
                    else:
                        st.info(f"Dati insufficienti per {h_n} o {a_n} (0 partite giocate).")
        else:
            st.error("Errore nel recupero dati. Riprova tra poco.")
