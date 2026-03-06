import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PL ANALYZER PRO - SERIE A", layout="wide")

# Configurazione API
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Parametri Serie A
ID_SERIE_A = 135 
STAGIONE = 2025 
DATA_TARGET = "2026-03-07" # Domani

st.title(f"🇮🇹 Analisi Serie A: Match del {DATA_TARGET}")

def get_pro_data():
    # 1. Recupera i match della Serie A per domani
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={ID_SERIE_A}&season={STAGIONE}&date={DATA_TARGET}&timezone=Europe/Rome"
    res = requests.get(url_fixtures, headers=HEADERS).json()
    fixtures = res.get('response', [])
    
    if not fixtures:
        return None, res

    data_rows = []
    for f in fixtures:
        f_id = f['fixture']['id']
        h_id = f['teams']['home']['id']
        a_id = f['teams']['away']['id']
        h_name = f['teams']['home']['name']
        a_name = f['teams']['away']['name']

        # 2. Statistiche Team Casa (Parametri: Media Gol in Casa e Forma Casa)
        h_res = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={ID_SERIE_A}&season={STAGIONE}&team={h_id}", headers=HEADERS).json()['response']
        # 3. Statistiche Team Ospite (Parametri: Media Gol Fuori e Forma Fuori)
        a_res = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={ID_SERIE_A}&season={STAGIONE}&team={a_id}", headers=HEADERS).json()['response']

        # Estrazione dati richiesti
        avg_h_scored = float(h_res['goals']['for']['average']['home'] or 0)
        avg_a_scored = float(a_res['goals']['for']['average']['away'] or 0)
        
        forma_h = h_res['form'][-5:] # Ultime 5 complessive (l'API le ordina bene)
        forma_a = a_res['form'][-5:]
        
        played_h = h_res['fixtures']['played']['home']
        played_a = a_res['fixtures']['played']['away']

        # Logica Asian Odds (Simulata su calo quota favorita in base alla forma)
        is_dropping = "📉 SI" if "W" in forma_h[:2] and avg_h_scored > 1.4 else "⚖️ NO"

        data_rows.append({
            "Ora": f['fixture']['date'][11:16],
            "Match": f"{h_name} - {a_name}",
            "P. Giocate (H-Casa/A-Fuori)": f"{played_h} / {played_a}",
            "Media Gol H (In Casa)": avg_h_scored,
            "Media Gol A (Fuori)": avg_a_scored,
            "Forma H": forma_h,
            "Forma A": forma_a,
            "Asian Drop": is_dropping,
            "Consiglio": "OVER 2.5" if (avg_h_scored + avg_a_scored) > 2.6 else "MULTIGOL 1-3"
        })
    
    return data_rows, res

if st.button("🔍 ANALIZZA SERIE A 7 MARZO"):
    with st.spinner("Accesso ai dati Serie A in corso..."):
        risultati, raw_json = get_pro_data()
        
        if risultati:
            st.success(f"Analisi completata per {len(risultati)} partite!")
            df = pd.DataFrame(risultati)
            st.table(df)
        else:
            st.error("Nessun match trovato.")
            st.write("Risposta API per controllo errori:", raw_json)
