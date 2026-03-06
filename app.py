import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer - TOTAL", layout="wide")

RAPID_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
ODDS_KEYS = [
    "bec8a75021e007e67ebc77b9b5c222be", 
    "c6a3eb71e7e203103715c6ee7dc932cd"
]

def clean_name(n):
    """Pulisce i nomi per trovare corrispondenze anche se diverse"""
    n = n.lower()
    for word in ["fc", "ac", "as", "sc", "cf", "fk", "milan", "lisbon", "eindhoven", " "]:
        n = n.replace(word, "")
    return n.strip()

@st.cache_data(ttl=3600)
def get_all_data(sport_key, league_id):
    odds, stats = None, None
    # 1. Recupero Quote (Prova tutte le chiavi)
    for key in ODDS_KEYS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        try:
            res = requests.get(url, params={"apiKey": key, "regions": "eu", "markets": "totals"}, timeout=10)
            if res.status_code == 200:
                odds = res.json()
                break
        except: continue
    
    # 2. Recupero Classifica (Prova stagioni recenti)
    headers = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    for s in ["2024", "2025"]:
        try:
            res = requests.get("https://api-football-v1.p.rapidapi.com/v3/standings", 
                             headers=headers, params={"league": league_id, "season": s}).json()
            if res.get('response'):
                stats = res['response'][0]['league']['standings'][0]
                break
        except: continue
    return odds, stats

st.title("⚽ ANALYZER - TUTTI I MATCH")

leagues = {
    "Serie A 🇮🇹": {"id": "135", "api": "soccer_italy_serie_a"},
    "Super League 🇨🇭": {"id": "207", "api": "soccer_switzerland_superleague"},
    "Eredivisie 🇳🇱": {"id": "88", "api": "soccer_netherlands_eredivisie"},
    "Primeira Liga 🇵🇹": {"id": "94", "api": "soccer_portugal_primeira_liga"}
}

scelta = st.selectbox("Seleziona Campionato:", list(leagues.keys()))

if st.button("MOSTRA TUTTE LE PARTITE DISPONIBILI"):
    with st.spinner("Scansione completa in corso..."):
        res_odds, standings = get_all_data(leagues[scelta]["api"], leagues[scelta]["id"])

    if res_odds and standings:
        # Database statistico con nomi ultra-puliti
        team_stats = {clean_name(t['team']['name']): t for t in standings}
        
        # Media Gol Lega
        total_g = sum(t['all']['goals']['for'] for t in standings)
        total_p = (sum(t['all']['played'] for t in standings) / 2)
        avg_l = total_g / total_p if total_p > 0 else 2.5
        
        match_count = 0
        st.subheader(f"Partite trovate per {scelta}")

        for m in res_odds:
            h_raw, a_raw = m['home_team'], m['away_team']
            h_c, a_c = clean_name(h_raw), clean_name(a_raw)
            
            # Matching flessibile: controlla se il nome pulito è contenuto nell'altro
            h_s = next((v for k,v in team_stats.items() if k in h_c or h_c in k), None)
            a_s = next((v for k,v in team_stats.items() if k in a_c or a_c in k), None)

            if h_s and a_s:
                match_count += 1
                hp, ap = max(h_s['home']['played'], 1), max(a_s['away']['played'], 1)
                
                # Formula xG Casa/Fuori (Parametri reali)
                xh = ((h_s['home']['goals']['for']/hp)/avg_l) * ((a_s['away']['goals']['against']/ap)/avg_l) * avg_l
                xa = ((a_s['away']['goals']['for']/ap)/avg_l) * ((h_s['home']['goals']['against']/hp)/avg_l) * avg_l
                txg = xh + xa
                
                m_time = datetime.strptime(m['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime('%d/%m %H:%M')

                with st.expander(f"📅 {m_time} | {h_raw} - {a_raw} | xG: {txg:.2f}"):
                    if txg > 2.80: st.success("🎯 CONSIGLIO: OVER 2.5")
                    elif txg < 2.05: st.warning("🛡️ CONSIGLIO: UNDER 2.5")
                    else: st.info("⚖️ NO BET")
            else:
                # Debug per capire quali nomi falliscono
                st.write(f"⚠️ Match ignorato per nomi: {h_raw} vs {a_raw}")

        if match_count == 0:
            st.warning("Nessuna partita rilevata per questo campionato. Verifica i crediti API.")
    else:
        st.error("❌ Impossibile scaricare i dati. Controlla la tua connessione o le chiavi API.")
