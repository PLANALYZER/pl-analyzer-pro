import streamlit as st
import requests
import pandas as pd

# Configurazione Dashboard
st.set_page_config(page_title="PL Analyzer Pro", layout="wide")
st.title("⚽ PL Analyzer Pro")

# Sidebar per la tua Key
api_key = st.sidebar.text_input("Incolla la tua API Key", type="password")

# Data di oggi e ID Lega (Serie A = 55)
target_date = "20260307"
league_id = "55"

if not api_key:
    st.info("Inserisci la tua API Key a sinistra per vedere le partite.")
else:
    if st.button("Mostra Partite di Oggi"):
        headers = {
            "X-Rapidapi-Key": api_key,
            "X-Rapidapi-Host": "free-api-live-football-data.p.rapidapi.com"
        }
        
        # URL basato sul tuo Playground
        url = f"https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date-and-league?date={target_date}&leagueid={league_id}"
        
        with st.spinner("Caricamento..."):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Questa parte è adattata esattamente allo screen che hai mandato
                partite_list = []
                # Nel tuo screen la risposta ha una lista 'response' che contiene gli eventi
                if "response" in data:
                    for item in data["response"]:
                        if "matches" in item:
                            for m in item["matches"]:
                                partite_list.append({
                                    "Ora": m.get("time", "N/D"),
                                    "Casa": m.get("home", {}).get("name", "N/D"),
                                    "Ospiti": m.get("away", {}).get("name", "N/D"),
                                    "ID Partita": m.get("id", "N/D")
                                })
                
                if partite_list:
                    st.success(f"Trovate {len(partite_list)} partite per la Serie A!")
                    st.table(pd.DataFrame(partite_list))
                else:
                    st.warning("Nessuna partita trovata per questa data.")
                    # Debug: ci aiuta a vedere se la struttura è cambiata
                    st.write("Dati ricevuti dall'API:", data)
            else:
                st.error(f"Errore API: {response.status_code}")
