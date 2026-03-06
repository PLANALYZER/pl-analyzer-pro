import streamlit as st
import requests

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

# LE TUE CHIAVI
RAPID_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"

@st.cache_data(ttl=3600)
def get_league_stats(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    headers = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    for season in ["2025", "2024"]:
        try:
            res = requests.get(url, headers=headers, params={"league": league_id, "season": season}, timeout=10).json()
            if res.get('response'): return res['response'][0]['league']['standings'][0]
        except: continue
    return None

st.title("⚽ ANALYZER PRO - FORMULA 5 MATCH")

league_map = {
    "Serie A 🇮🇹": "135",
    "Super League 🇨🇭": "207",
    "Eredivisie 🇳🇱": "88",
    "Primeira Liga 🇵🇹": "94"
}

api_odds_map = {
    "135": "soccer_italy_serie_a", 
    "207": "soccer_switzerland_superleague",
    "88": "soccer_netherlands_eredivisie",
    "94": "soccer_portugal_primeira_liga"
}

scelta = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ANALIZZA MATCH"):
    with st.spinner("Sincronizzazione database..."):
        id_lega = league_map[scelta]
        standings = get_league_stats(id_lega)
        url_odds = f"https://api.the-odds-api.com/v4/sports/{api_odds_map[id_lega]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        res_odds = requests.get(url_odds).json()

    if standings and isinstance(res_odds, list):
        team_stats = {t['team']['name'].lower(): t for t in standings}
        # Calcolo Media Gol
        total_g = sum(t['all']['goals']['for'] for t in standings)
        total_p = sum(t['all']['played'] for t in standings) / 2
        avg_l = total_g / total_p if total_p > 0 else 2.5
        
        st.write(f"✅ Dati caricati. Media Campionato: {avg_l:.2f}")
        
        match_count = 0
        for match in res_odds:
            h_n, a_n = match['home_team'].lower(), match['away_team'].lower()
            h_s = next((v for k,v in team_stats.items() if k in h_n or h_n in k), None)
            a_s = next((v for k,v in team_stats.items() if k in a_n or a_n in k), None)

            if h_s and a_s:
                match_count += 1
                h_p, a_p = max(h_s['home']['played'], 1), max(a_s['away']['played'], 1)
                
                # Formula xG
                xh = ((h_s['home']['goals']['for']/h_p)/avg_l) * ((a_s['away']['goals']['against']/a_p)/avg_l) * avg_l
                xa = ((a_s['away']['goals']['for']/a_p)/avg_l) * ((h_s['home']['goals']['against']/h_p)/avg_l) * avg_l
                txg = xh + xa

                with st.expander(f"🏟️ {match['home_team']} vs {match['away_team']} | xG: {txg:.2f}"):
                    st.write(f"📊 Casa: {h_p} match | Fuori: {a_p} match")
                    if txg > 2.80: st.success("🎯 CONSIGLIO: OVER 2.5")
                    elif txg < 2.05: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                    else: st.info("⚖️ NO BET")
        
        if match_count == 0:
            st.warning("Match trovati nelle quote, ma non corrispondono alle squadre in classifica. Ricontrolla i nomi.")
    else:
        st.error("Errore: Verifica che il piano Basic su RapidAPI sia attivo (clicca 'Subscribe').")
