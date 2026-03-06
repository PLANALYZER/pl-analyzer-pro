import streamlit as st
import requests

# Inserisci qui la tua key
headers = {
    "X-RapidAPI-Key": "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

st.title("⚽ Scanner Bombe 48H")

def test_connection():
    url = "https://api-football-v1.p.rapidapi.com/v3/timezone"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.success("Connessione API OK!")
    else:
        st.error(f"Errore API: {response.status_code} - Controlla il piano dell'abbonamento.")

test_connection()
