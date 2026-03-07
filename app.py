import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# --- CONFIGURAZIONE API ---
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com/football-"

st.title("⚽ PL Analyzer Pro")

# Sidebar - Manteniamo la Key e il Menu che già funzionano
api_key = st.sidebar.text_input("Inserisci la tua X-RapidAPI-Key", type="password")
menu = st.sidebar.radio("Menu", ["Fase 1: Selezione ID", "Fase 2: Calendario", "Fase 3: Pronostici"])

# --- FASE 1: Manteniamo la selezione per ID che hai già fatto ---
if menu == "Fase 1: Selezione ID":
    st.header("🎯 Selezione Campionati per ID")
    st.info("ID Serie A confermato: 55")
    
    ids_input = st.text_input("Inserisci ID separati da virgola", "55, 42, 73")
    
    if st.button("Salva la mia lista"):
        st.session_state['active_ids'] = [x.strip() for x in ids_input.split(",")]
        st.success(f"Campionati ID {st.session_state['active_ids']} salvati!")

# --- FASE 2: Nuovo codice per trovare le partite di OGGI ---
elif menu == "Fase 2: Calendario":
    st.header("📅 Partite di Oggi: 07/03/2026")
    
    if 'active_ids' not in st.session_state:
        st.warning("Torna alla Fase 1 e salva gli ID (es. 55)!")
    else:
        # Fissiamo la data come richiesto
        data_target = "20260307" 
        
        if st.button("Scarica Partite di Oggi"):
            headers = {
                "X-Rapidapi-Key": api_key,
                "X-Rapidapi-Host": API_HOST
            }
            partite_oggi = []
            
            with st.spinner("Ricerca match in corso..."):
                for league_id in st.session_state['active_ids']:
                    # Usiamo l'endpoint 'get-all-matches-from-league' per avere tutto il calendario
                    url = f"{BASE_URL}get-all-matches-from-league?leagueid={league_id}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "response" in data and "matches" in data["response"]:
                            for m in data["response"]["matches"]:
                                data_match = m['status']['utcTime'].split('T')[0].replace("-", "")
                                
                                # Filtriamo solo per la data di oggi
                                if data_match == data_target:
                                    partite_oggi.append({
                                        "Ora": m['status']['utcTime'].split('T')[1][:5],
                                        "Campionato": m['leagueName'],
                                        "Home": m['home']['name'],
                                        "Away": m['away']['name'],
                                        "MatchID": m['id']
                                    })
            
            if partite_oggi:
                st.success(f"Trovate {len(partite_oggi)} partite per oggi!")
                df_oggi = pd.DataFrame(partite_oggi)
                st.table(df_oggi)
                st.session_state['last_fixtures'] = partite_oggi
            else:
                st.info("Nessuna partita in programma per oggi negli ID selezionati.")

# --- FASE 3: Pronta per l'algoritmo ---
elif menu == "Fase 3: Pronostici":
    st.header("📈 Generatore Pronostici")
    if 'last_fixtures' in st.session_state:
        partite = st.session_state['last_fixtures']
        scelta = st.selectbox("Seleziona una partita di oggi:", 
                             [f"{p['Home']} vs {p['Away']}" for p in partite])
        st.write(f"Analisi per: **{scelta}**")
        st.button("Genera Pronostico AI")
    else:
        st.warning("Scarica le partite nella Fase 2 prima di procedere.")
