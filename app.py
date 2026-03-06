import streamlit as st
import requests

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

# LE TUE CHIAVI
RAPID_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"

@st.cache_data(ttl=3600) # Ridotta a 1 ora per testare i permessi in tempo reale
def get_league_stats(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    headers = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    # Proviamo 2025 o 2024
    for season in ["2025", "2024"]:
        try:
            res = requests.get(url, headers=headers, params={"league": league_id, "season": season}, timeout=10).json()
            if res.get('response') and len(res['response']) > 0:
                return res['response'][0]['league']['standings'][0]
        except: continue
    return None

st.title("⚽ ANALYZER PRO - FORMULA 5 MATCH")

# Mappa Campionati
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
        
        # Recupero Quote
        url_odds = f"https://api.the-odds-api.com/v4/sports/{api_odds_map[id_lega]}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
        res_odds = requests.get(url_odds).json()

    if standings and isinstance(res_odds, list):
        team_stats = {t['team']['name'].lower(): t for t in standings}
        avg_l = sum(t['all']['goals']['for'] for t in standings) / (sum(t['all']['played'] for t in standings) / 2)
        
        match_count = 0
        for match in res_odds:
            h_n, a_n = match['home_team'].lower(), match['away_team'].lower()
            
            # Ricerca flessibile del nome squadra
            h_s = next((v for k,v in team_stats.items() if k in h_n or h_n in k), None)
            a_s = next((v for k,v in team_stats.items() if k in a_n or a_n in k), None)

            if h_s and a_s:
                h_p, a_p = h_s['home']['played'], a_s['away']['played']
                
                # Se non hanno ancora 5 partite, mostriamo comunque il match ma con un avviso
                match_count += 1
                xh = ((h_s['home']['goals']['for']/max(h_p,1))/avg_l) * ((a_s['away']['goals']['against']/max(a_p,1))/avg_l) * avg_l
                xa = ((a_s['away']['goals']['for']/max(a_p,1))/avg_l) * ((h_s['home']['goals']['against']/max(h_p,1))/avg_l) * avg_l
                txg = xh + xa

                with st.expander(f"🏟️ {match['home_team']} vs {match['away_team']} | xG: {txg:.2f}"):
                    if h_p < 5 or a_p < 5:
                        st.warning(f"⚠️ Formula non definitiva: Solo {h_p} match in casa e {a_p} fuori.")
                    
                    st.write(f"📊 Media Gol Casa: {(h_s['home']['goals']['for']/max(h_p,1)):.2f} | Media Gol Fuori: {(a_s['away']['goals']['for']/max(a_p,1)):.2f}")
                    
                    if txg > 2.80: st.success("🎯 CONSIGLIO: OVER 2.5")
                    elif txg < 2.05: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                    else: st.info("⚖️ NO BET"
