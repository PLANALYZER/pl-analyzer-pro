import streamlit as st
import requests

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

# LE TUE CHIAVI
RAPID_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"

# Funzione per estrarre i dati
@st.cache_data(ttl=43200)
def get_league_stats(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    headers = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    for season in ["2025", "2024"]:
        res = requests.get(url, headers=headers, params={"league": league_id, "season": season}).json()
        if res.get('response'): return res['response'][0]['league']['standings'][0]
    return None

st.title("⚽ ANALYZER PRO - FORMULA 5 MATCH")

# Mappa Campionati
league_map = {
    "Serie A 🇮🇹": "135",
    "Super League 🇨🇭": "207",
    "Challenge League 🇨🇭": "208",
    "Eredivisie 🇳🇱": "88",
    "Eerste Divisie 🇳🇱": "89"
}

api_odds_map = {
    "135": "soccer_italy_serie_a", "207": "soccer_switzerland_superleague",
    "208": "soccer_switzerland_challenge_league", "88": "soccer_netherlands_eredivisie",
    "89": "soccer_netherlands_leerste_divisie"
}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ANALIZZA MATCH"):
    with st.spinner("Calcolo in corso..."):
        standings = get_league_stats(league_map[scelta])
        # Recupero Quote
        url_odds = f"https://api.the-odds-api.com/v4/sports/{api_odds_map[league_map[scelta]]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        res_odds = requests.get(url_odds).json()

    if standings and res_odds:
        team_stats = {t['team']['name']: t for t in standings}
        # Media Gol Campionato per normalizzazione
        avg_l = sum(t['all']['goals']['for'] for t in standings) / (sum(t['all']['played'] for t in standings) / 2)

        for match in res_odds:
            h_n, a_n = match['home_team'], match['away_team']
            h_s = next((v for k,v in team_stats.items() if h_n in k or k in h_n), None)
            a_s = next((v for k,v in team_stats.items() if a_n in k or k in a_n), None)

            if h_s and a_s:
                # FILTRO 5 PARTITE (Cibo vero!)
                h_p, a_p = h_s['home']['played'], a_s['away']['played']
                
                if h_p >= 5 and a_p >= 5:
                    # FORMULA xG REALE
                    xh = ((h_s['home']['goals']['for']/h_p)/avg_l) * ((a_s['away']['goals']['against']/a_p)/avg_l) * avg_l
                    xa = ((a_s['away']['goals']['for']/a_p)/avg_l) * ((h_s['home']['goals']['against']/h_p)/avg_l) * avg_l
                    txg = xh + xa

                    with st.expander(f"🏟️ {h_n} - {a_n} | xG Totale: {txg:.2f}"):
                        st.write(f"📊 Media Casa: {(h_s['home']['goals']['for']/h_p):.2f} gol | Media Fuori: {(a_s['away']['goals']['for']/a_p):.2f} gol")
                        if txg > 2.80: st.success("🎯 CONSIGLIO: OVER 2.5")
                        elif txg < 2.05: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
