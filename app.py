import streamlit as st
import requests
from datetime import datetime, timedelta

# CONFIGURAZIONE CORRETTA
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
# Assicurati che l'host sia questo per api-football
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com" 
}

st.title("⚽ Scanner Bombe 48H")

# Lista Leghe (Serie A, B, C, Premier, etc.)
LEAGUES = {"Serie A": 135, "Serie B": 136, "Premier League": 39, "La Liga": 140}

def get_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    # Range 48 ore
    params = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "league": 135, # Esempio Serie A
        "season": 2025
    }
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

# ESECUZIONE
data = get_matches()
if "errors" in data and data["errors"]:
    st.error(f"Errore rilevato: {data['errors']}")
else:
    st.success("Dati caricati! Elaborazione parametri Multigol...")
