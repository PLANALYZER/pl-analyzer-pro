import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL Analyzer Pro - Hub", layout="wide")
st.title("⚽ Dashboard Campionati Verificati")

# Configurazione API
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"

# La tua lista ID verificata al 100%
MY_LEAGUES = {
    "Premier League": "47", "Championship": "48", "League One": "108", 
    "League Two": "109", "National League": "117", "Serie A": "55", 
    "Serie B": "86", "Serie C": "147", "Bundesliga": "54", 
    "2. Bundesliga": "146", "La Liga": "87", "Ligue 1": "53", 
    "Eredivisie": "57", "Eerste Divisie": "111", "Super League (SUI)": "69", 
    "Challenge League (SUI)": "163", "First Division (BEL)": "40", 
    "Liga Portugal": "61", "Eliteserien (NOR)": "59", "Superligaen (DEN)": "46", 
    "1. Division (DEN)": "85", "Serie A (BUL)": "270", "Bundesliga (AUT)": "38", 
    "Ekstraklasa (POL)": "196", "Super Lig (TUR)": "71"
}

st.sidebar.header("Parametri di Ricerca")
data_scelta = st.sidebar.text_input("Data (YYYYMMDD)", "20260307")

if st.button("🔄 Aggiorna Palinsesto"):
    all_matches = []
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    
    # Barra di caricamento per monitorare i 25 campionati
    progress_bar = st.progress(0)
    count = 0
    
    for name, lid in MY_LEAGUES.items():
        count += 1
        url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_scelta}&leagueid={lid}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
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
        except Exception as e:
            continue
        progress_bar.progress(count / len(MY_LEAGUES))

    if all_matches:
        st.success(f"✅ Caricate {len(all_matches)} partite dai tuoi campionati preferiti!")
        df = pd.DataFrame(all_matches)
        st.dataframe(df, use_container_width=True)
        st.session_state['matches_data'] = all_matches
    else:
        st.warning("Nessuna partita trovata per questa data nei campionati selezionati.")

st.divider()
st.info("Tutti gli ID sono stati verificati manualmente tramite RapidAPI Playground.")
