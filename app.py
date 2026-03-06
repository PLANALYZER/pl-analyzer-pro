import streamlit as st
import requests
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

RAPID_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
ODDS_KEYS = [
    "bec8a75021e007e67ebc77b9b5c222be", 
    "c6a3eb71e7e203103715c6ee7dc932cd"
]

@st.cache_data(ttl=3600) # Salvataggio dati per 1 ora per non finire i 500 crediti
def get_data_all(sport_key, league_id):
    # Prova a recuperare le quote con rotazione chiavi
    odds = None
    for key in ODDS_KEYS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        try:
            res = requests.get(url, params={"apiKey": key, "regions": "eu", "markets": "totals"}, timeout=10)
            if res.status_code == 200:
                odds = res.json()
                break
        except: continue
    
    # Recupera statistiche
    stats = None
    url_s = "https://api-football-v1.p.rapidapi.com/v3/standings"
    headers = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    try:
        res_s = requests.get(url_s, headers=headers, params={"league": league_id, "season": "2024"}).json()
        if not res_s.get('response'): # Prova 2025 se 2024 è vuota
             res_s = requests.get(url_s, headers=headers, params={"league": league_id, "season": "2025"}).json()
        stats = res_s['response'][0]['league']['standings'][0]
    except: pass
    
    return odds, stats

st.title("⚽ ANALYZER PRO - SISTEMATO")

leagues = {"Serie A 🇮🇹": "135", "Super League 🇨🇭": "207", "Eredivisie 🇳🇱": "88", "Primeira Liga 🇵🇹": "94"}
api_map = {"135": "soccer_italy_serie_a", "207": "soccer_switzerland_superleague", "88": "soccer_netherlands_eredivisie", "94": "soccer_portugal_primeira_liga"}

scelta = st.selectbox("Campionato:", list(leagues.keys()))

if st.button("AVVIA ANALISI"):
    res_odds, standings = get_data_all(api_map[leagues[scelta]], leagues[scelta])

    if res_odds and standings:
        team_stats = {t['team']['name'].lower(): t for t in standings}
        # Parametro Media Gol Campionato (Cibo Vero)
        avg_l = sum(t['all']['goals']['for'] for t in standings) / (sum(t['all']['played'] for t in standings) / 2)
        
        now = datetime.utcnow()
        limit = now + timedelta(hours=72) # Allargato a 72 ore per sicurezza
        found = 0

        for m in res_odds:
            m_time = datetime.strptime(m['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
            if now <= m_time <= limit:
                h_n, a_n = m['home_team'].lower(), m['away_team'].lower()
                
                # Matching "Contenimento": risolve il problema dei nomi diversi
                h_s = next((v for k,v in team_stats.items() if k in h_n or h_n in k), None)
                a_s = next((v for k,v in team_stats.items() if k in a_n or a_n in k), None)

                if h_s and a_s:
                    found += 1
                    # Parametri formula protetti contro lo zero
                    h_p = max(h_s['home']['played'], 1)
                    a_p = max(a_s['away']['played'], 1)
                    
                    xh = ((h_s['home']['goals']['for']/h_p)/avg_l) * ((a_s['away']['goals']['against']/a_p)/avg_l) * avg_l
                    xa = ((a_s['away']['goals']['for']/a_p)/avg_l) * ((h_s['home']['goals']['against']/h_p)/avg_l) * avg_l
                    txg = xh + xa

                    with st.expander(f"🏟️ {m['home_team']} - {m['away_team']} | xG: {txg:.2f}"):
                        if txg > 2.80: st.success("🎯 CONSIGLIO: OVER 2.5")
                        elif txg < 2.05: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                        else: st.info("⚖️ NO BET")
                else:
                    st.write(f"⚠️ Saltato: `{m['home_team']}` o `{m['away_team']}` non trovati in classifica.")
