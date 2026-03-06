import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER - DEBUG", layout="wide")

API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Parametri fissi per domani
ID_SERIE_A = 135 
STAGIONE = 2025 
DATA_DOMANI = "2026-03-07"

st.title("🛠️ Debug Serie A - 7 Marzo")

if st.button("Lancia Ricerca Forzata"):
    # 1. Vediamo prima se la Lega 135 è disponibile per la stagione 2025
    st.write("Controllo disponibilità Serie A...")
    
    # Cerchiamo i match di domani con fuso orario Roma
    url = f"https://v3.football.api-sports.io/fixtures?league={ID_SERIE_A}&season={STAGIONE}&date={DATA_DOMANI}&timezone=Europe/Rome"
    
    response = requests.get(url, headers=HEADERS).json()
    
    if response.get('errors'):
        st.error(f"L'API ha restituito un errore: {response['errors']}")
    
    matches = response.get('response', [])
    
    if not matches:
        st.warning(f"L'API dice che non ci sono match per il {DATA_DOMANI} in Serie A.")
        st.write("Risposta completa dell'API per i tecnici:", response) # Questo ci dice TUTTO
    else:
        st.success(f"Trovati {len(matches)} match!")
        
        data_rows = []
        for m in matches:
            h_name = m['teams']['home']['name']
            a_name = m['teams']['away']['name']
            h_id = m['teams']['home']['id']
            a_id = m['teams']['away']['id']
            
            # Recupero Stats
            h_s = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={ID_SERIE_A}&season={STAGIONE}&team={h_id}", headers=HEADERS).json()['response']
            a_s = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={ID_SERIE_A}&season={STAGIONE}&team={a_id}", headers=HEADERS).json()['response']
            
            # Calcolo le tue medie (Fatti Casa / Fatti Fuori)
            avg_h = h_s['goals']['for']['average']['home']
            avg_a = a_s['goals']['for']['average']['away']
            forma_h = h_s['form'][-5:]
            forma_a = a_s['form'][-5:]

            data_rows.append({
                "Ora": m['fixture']['date'][11:16],
                "Partita": f"{h_name} - {a_name}",
                "Media Gol Casa": avg_h,
                "Media Gol Ospite": avg_a,
                "Forma H": forma_h,
                "Forma A": forma_a
            })
            
        st.table(pd.DataFrame(data_rows))
