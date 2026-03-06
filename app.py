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
    st.stop()

# --- 2. CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - STATISTICHE CASA/FUORI REALI")

# --- 3. MAPPE CAMPIONATI ---
league_map = {
    "Eredivisie (NL) 🇳🇱": "DED",
    "Eerste Divisie (NL 2) 🇳🇱": "ED",
    "Super League (CH) 🇨🇭": "SL",
    "Challenge League (CH 2) 🇨🇭": "SCL",
    "Bundesliga (DE) 🇩🇪": "BL1",
    "Primeira Liga (PT) 🇵🇹": "PPL",
    "Premier League (UK) 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "PL",
    "Serie A (IT) 🇮🇹": "SA",
    "La Liga (ES) 🇪🇸": "PD",
    "Ligue 1 (FR) 🇫🇷": "FL1"
}

api_league_map = {
    "Eredivisie (NL) 🇳🇱": "soccer_netherlands_eredivisie",
    "Eerste Divisie (NL 2) 🇳🇱": "soccer_netherlands_leerste_divisie",
    "Super League (CH) 🇨🇭": "soccer_switzerland_superleague",
    "Challenge League (CH 2) 🇨🇭": "soccer_switzerland_challenge_league",
    "Bundesliga (DE) 🇩🇪": "soccer_germany_bundesliga",
    "Primeira Liga (PT) 🇵🇹": "soccer_portugal_primeira_liga",
    "Premier League (UK) 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "soccer_epl",
    "Serie A (IT) 🇮🇹": "soccer_italy_serie_a",
    "La Liga (ES) 🇪🇸": "soccer_spain_la_liga",
    "Ligue 1 (FR) 🇫🇷": "soccer_france_ligue_one"
}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI"):
    with st.spinner("Calcolo medie Casa/Fuori in corso..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Classifica Dettagliata (Home/Away separati)
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # 2. Recupero Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals").json()

        if "standings" in res_stats:
            # Estraiamo le tabelle specifiche Casa e Fuori
            standings = res_stats['standings']
            home_table = {t['team']['name']: t for t in standings[1]['table']} # Classifica Casa
            away_table = {t['team']['name']: t for t in standings[2]['table']} # Classifica Fuori
            
            # Media gol campionato per normalizzare xG
            total_g = sum(t['goalsFor'] for t in standings[0]['table'])
            total_p = sum(t['playedGames'] for t in standings[0]['table']) / 2
            avg_l = total_g / total_p if total_p > 0 else 2.5

            for match in res_odds:
                m_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                if datetime.utcnow() <= m_time <= (datetime.utcnow() + timedelta(hours=48)):
                    h_n, a_n = match['home_team'], match['away_team']
                    
                    # Troviamo i dati specifici
                    h_data = next((v for k,v in home_table.items() if h_n in k or k in h_n), None)
                    a_data = next((v for k,v in away_table.items() if a_n in k or k in a_n), None)

                    if h_data and a_data:
                        # GOL FATTI E SUBITI SPECIFICI
                        h_gf = h_data['goalsFor']
                        h_gs = h_data['goalsAgainst']
                        h_p = max(1, h_data['playedGames'])
                        
                        a_gf = a_data['goalsFor']
                        a_gs = a_data['goalsAgainst']
                        a_p = max(1, a_data['playedGames'])

                        # CALCOLO xG BASATO SOLO SU CASA/FUORI
                        xh = ((h_gf/h_p)/avg_l) * ((a_gs/a_p)/avg_l) * avg_l
                        xa = ((a_gf/a_p)/avg_l) * ((h_gs/h_p)/avg_l) * avg_l
                        txg = xh + xa

                        # Recupero Quote
                        try:
                            m_h2h = next(m for m in match['bookmakers'][0]['markets'] if m['key'] == 'h2h')['outcomes']
                            q1 = next(o['price'] for o in m_h2h if o['name'] == h_n)
                            q2 = next(o['price'] for o in m_h2h if o['name'] == a_n)
                            m_tot = next(m for m in match['bookmakers'][0]['markets'] if m['key'] == 'totals')['outcomes']
                            qo25 = next(o['price'] for o in m_tot if o['name'] == 'Over' and o['point'] == 2.5)
                        except: continue

                        with st.expander(f"📊 {h_n} vs {a_n} | xG Totale: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.write(f"🏠 **{h_n} in Casa**")
                                st.metric("Gol Fatti", h_gf)
                                st.metric("Gol Subiti", h_gs)
                                st.caption(f"Media: {(h_gf/h_p):.2f} a partita")
                            with c2:
                                st.write(f"🚀 **{a_n} Fuori**")
                                st.metric("Gol Fatti", a_gf)
                                st.metric("Gol Subiti", a_gs)
                                st.caption(f"Media: {(a_gf/a_p):.2f} a partita")
                            with c3:
                                st.metric("QUOTA OVER 2.5", qo25)
                                if qo25 < 1.75 and txg > 2.75: st.success("📉 TREND: VALORE OVER")
                                if q1 < q2 and q1 < 1.60: st.info("🏆 Favorito: Casa")
                                elif q2 < q1 and q2 < 1.60: st.info("🏆 Favorito: Ospite")

                            st.divider()
                            # PRONOSTICO DEFINITIVO
                            p1, p2 = st.columns(2)
                            with p1:
                                if txg > 2.85: st.success("🎯 CONSIGLIO: OVER 2.5")
                                elif txg < 2.00: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                                else: st.info("⚖️ NO BET (Equilibrio)")
                            with p2:
                                if (h_gf/h_p) > 1.2 and (a_gf/a_p) > 1.2: st.success("⚽ CONSIGLIO: GOAL")
                                if (h_gs/h_p) > 1.5 and txg > 2.7: st.warning("⚠️ Difesa Casa Debole")
