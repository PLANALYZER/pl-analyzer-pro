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

st.title("⚽ ANALYZER PRO - FIX ERRORI & MULTI-LEAGUE")

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
    with st.spinner("Sincronizzazione dati in corso..."):
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # 1. Recupero Classifica
        res_stats = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/standings", headers=headers).json()
        
        # 2. Recupero Match per Forma (120gg)
        d_from = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
        d_to = datetime.now().strftime('%Y-%m-%d')
        res_history = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[scelta]}/matches?dateFrom={d_from}&dateTo={d_to}&status=FINISHED", headers=headers).json()
        
        # 3. Recupero Quote
        res_odds = requests.get(f"https://api.the-odds-api.com/v4/sports/{api_league_map[scelta]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals").json()

        if "standings" in res_stats and "matches" in res_history:
            standings = res_stats['standings']
            
            # --- FIX INDEXERROR: Gestione Tabelle Casa/Fuori ---
            # Se l'API non dà tabelle separate, usiamo quella totale per tutto
            if len(standings) >= 3:
                home_db = {t['team']['name']: t for t in standings[1]['table']}
                away_db = {t['team']['name']: t for t in standings[2]['table']}
            else:
                home_db = {t['team']['name']: t for t in standings[0]['table']}
                away_db = {t['team']['name']: t for t in standings[0]['table']}
            
            total_db = {t['team']['name']: t for t in standings[0]['table']}
            match_history = res_history['matches']
            
            # Media gol campionato
            total_g = sum(t['goalsFor'] for t in standings[0]['table'])
            total_p = sum(t['playedGames'] for t in standings[0]['table']) / 2
            avg_l = total_g / total_p if total_p > 0 else 2.5

            for match in res_odds:
                m_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                if datetime.utcnow() <= m_time <= (datetime.utcnow() + timedelta(hours=48)):
                    h_n, a_n = match['home_team'], match['away_team']
                    
                    # Recupero dati con matching flessibile
                    h_s = next((v for k,v in home_db.items() if h_n in k or k in h_n), None)
                    a_s = next((v for k,v in away_db.items() if a_n in k or k in a_n), None)

                    if h_s and a_s:
                        # --- STATISTICHE REALI ---
                        h_gf, h_gs, h_p = h_s['goalsFor'], h_s['goalsAgainst'], max(1, h_s['playedGames'])
                        a_gf, a_gs, a_p = a_s['goalsFor'], a_s['goalsAgainst'], max(1, a_s['playedGames'])

                        # --- FIX NAMEERROR: Calcolo xG con variabili corrette ---
                        xh = ((h_gf/h_p)/avg_l) * ((a_gs/a_p)/avg_l) * avg_l
                        xa = ((a_gf/a_p)/avg_l) * ((h_gs/h_p)/avg_l) * avg_l
                        txg = xh + xa

                        # Recupero Forma Specifica (ID)
                        h_id, a_id = h_s['team']['id'], a_s['team']['id']
                        f_h = sum(3 if m['score']['winner']=='HOME_TEAM' else 1 if m['score']['winner']=='DRAW' else 0 for m in [m for m in match_history if m['homeTeam']['id']==h_id][-5:])
                        f_a = sum(3 if m['score']['winner']=='AWAY_TEAM' else 1 if m['score']['winner']=='DRAW' else 0 for m in [m for m in match_history if m['awayTeam']['id']==a_id][-5:])

                        # Quote
                        try:
                            m_h2h = next(m for m in match['bookmakers'][0]['markets'] if m['key'] == 'h2h')['outcomes']
                            q1 = next(o['price'] for o in m_h2h if o['name'] == h_n)
                            q2 = next(o['price'] for o in m_h2h if o['name'] == a_n)
                            m_tot = next(m for m in match['bookmakers'][0]['markets'] if m['key'] == 'totals')['outcomes']
                            qo25 = next(o['price'] for o in m_tot if o['name'] == 'Over' and o['point'] == 2.5)
                        except: continue

                        with st.expander(f"📊 {h_n} vs {a_n} | xG: {txg:.2f}"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric(f"FORMA {h_n}", f"{f_h}/15")
                                st.write(f"Gol Fatti (Casa): {h_gf}")
                            with c2:
                                st.metric(f"FORMA {a_n}", f"{f_a}/15")
                                st.write(f"Gol Fatti (Fuori): {a_gf}")
                            with c3:
                                st.metric("QUOTA O2.5", qo25)
                                if qo25 < 1.75 and txg > 2.70: st.success("📉 TREND: VALORE")

                            st.divider()
                            # PRONOSTICO
                            p1, p2 = st.columns(2)
                            with p1:
                                if txg > 2.80: st.success("🎯 OVER 2.5")
                                elif txg < 2.05: st.warning("🛡️ UNDER 2.5")
                                else: st.info("⚖️ NO BET")
                            with p2:
                                if q1 < 1.60 and f_h >= 10: st.success(f"🔥 TREND {h_n}")
                                elif q2 < 1.60 and f_a >= 10: st.success(f"🔥 TREND {a_n}")
