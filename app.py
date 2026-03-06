import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER - PRO", layout="wide")
st.title("⚽ PL Analyzer - Serie A (7 Marzo)")

# La tua chiave RapidAPI
MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"

# HEADERS specifici per l'API che hai acquistato: "Free API Live Football Data"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_matches():
    # Nota: Gli endpoint di questa API potrebbero differire da API-Football.
    # Proviamo a recuperare i match della Serie A (League ID per questa API va verificato)
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
    query = {"date": "20260307"} # Formato tipico per questa API: AAAAMMGG
    
    try:
        response = requests.get(url, headers=HEADERS, params=query).json()
        return response
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
        return None

if st.button("🔍 ANALIZZA MATCH DI DOMANI"):
    with st.spinner("Recupero dati dalla tua sottoscrizione PRO..."):
        data = get_matches()
        
        if data and 'response' in data:
            # Qui adattiamo la visualizzazione in base alla struttura della tua API
            st.success("Connessione riuscita!")
            st.json(data['response']) # Vediamo la struttura per poi creare la tabella
        else:
            st.error("L'API non ha restituito dati. Verifica se i parametri della tua API sono corretti.")
            st.write("Risposta API:", data)
