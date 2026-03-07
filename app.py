import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")
st.title("⚽ Dashboard Campionati Selezionati")

# Configurazione API
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"

# La tua lista ID definitiva
MY_LEAGUES = {
    "Serie A": "55", "Serie B": "56", "Champions League": "42",
    "Europa League": "73", "Conference League": "10216",
    "Premier League": "47", "Championship": "48", "League One": "108",
    "League Two": "109", "Bundesliga": "54", "La Liga": "87",
    "Ligue 1": "53", "Eredivisie": "57", "Eerste Divisie": "132",
    "Svizzera Super League": "130", "Svizzera Challenge": "131"
}

st.sidebar.header("Impostazioni")
data_scelta = st.sidebar.text_input("Data (YYYYMMDD)", "20260307")

if st.button("🔍 Scarica Partite di Oggi"):
    all_matches = []
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    
    progress_bar = st.progress(0)
    count = 0
    
    for name, lid in MY_LEAGUES.items():
        count += 1
        url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_scelta}&leagueid={lid}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Scaviamo nella struttura della tua API
                if "response" in data:
                    for item in data["response"]:
                        if "matches" in item:
                            for m in item["matches"]:
                                all_matches.append({
                                    "Campionato": name,
                                    "Ora": m.get("time", "N/D"),
                                    "Casa": m.get("home", {}).get("name", "N/D"),
                                    "Ospiti": m.get("away", {}).get("name", "N/D"),
                                    "ID Partita": m.get("id", "N/D")
                                })
        except:
            continue
        progress_bar.progress(count / len(MY_LEAGUES))

    if all_matches:
        st.success(f"Trovate {len(all_matches)} partite!")
        df = pd.DataFrame(all_matches)
        st.dataframe(df, use_container_width=True)
        st.session_state['today_matches'] = all_matches
    else:
        st.warning("Nessuna partita trovata per i campionati selezionati in questa data.")

st.divider()
st.info("La Web App ora monitora solo i 16 campionati che hai scelto.")
