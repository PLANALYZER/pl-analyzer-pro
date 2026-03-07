import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# --- CONFIGURAZIONE API ---
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com/football-"

st.title("⚽ PL Analyzer Pro")

# Sidebar
api_key = st.sidebar.text_input("Inserisci la tua X-RapidAPI-Key", type="password")
menu = st.sidebar.radio("Menu", ["Fase 1: Selezione ID", "Fase 2: Calendario", "Fase 3: Pronostici"])

if menu == "Fase 1: Selezione ID":
    st.header("🎯 Selezione Campionati per ID")
    st.info("Esempio ID: 55 (Serie A), 42 (Champions), 73 (Europa League)")
    
    # Input per gli ID
    ids_input = st.text_input("Inserisci ID separati da virgola", "55, 42, 73")
    
    if st.button("Salva la mia lista"):
        st.session_state['active_ids'] = [x.strip() for x in ids_input.split(",")]
        st.success(f"Campionati ID {st.session_state['active_ids']} salvati!")

elif menu == "Fase 2: Calendario":
    st.header("📅 Partite del Giorno")
    
    if 'active_ids' not in st.session_state:
        st.warning("Torna alla Fase 1 e inserisci almeno un ID (es. 55)!")
    else:
        data_oggi = st.date_input("Seleziona Data", datetime.now()).strftime('%Y%m%d')
        
        if st.button("Mostra Partite"):
            headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
            partite_totali = []
            
            with st.spinner("Scansione campionati in corso..."):
                for league_id in st.session_state['active_ids']:
                    # Usiamo l'endpoint 'get-matches-by-date-and-league' visto nei tuoi screen
                    url = f"{BASE_URL}get-matches-by-date-and-league?date={data_oggi}&leagueid={league_id}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "response" in data and "matches" in data["response"]:
                            for m in data["response"]["matches"]:
                                partite_totali.append({
                                    "Ora": m['status']['utcTime'].split('T')[1][:5],
                                    "Campionato": m['leagueName'],
                                    "Home": m['home']['name'],
                                    "Away": m['away']['name'],
                                    "ID Partita": m['id']
                                })
            
            if partite_totali:
                df_partite = pd.DataFrame(partite_totali)
                st.table(df_partite)
                st.session_state['last_fixtures'] = partite_totali
            else:
                st.write("Nessuna partita trovata per questi ID nella data scelta.")

elif menu == "Fase 3: Pronostici":
    st.header("📈 Generatore Pronostici")
    if 'last_fixtures' in st.session_state:
        match_nomi = [f"{m['Home']} vs {m['Away']}" for m in st.session_state['last_fixtures']]
        scelta = st.selectbox("Seleziona partita da analizzare", match_nomi)
        st.write(f"Analisi in arrivo per: {scelta}")
    else:
        st.warning("Scarica prima le partite nella Fase 2.")
