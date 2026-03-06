import streamlit as st
import requests

st.title("🛡️ Verifica Stato API Key")

# La tua chiave
MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"

# PROVA 1: Connessione diretta API-Sports
headers_direct = {
    'x-rapidapi-key': MY_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# PROVA 2: Connessione tramite RapidAPI (molto probabile se la chiave ha quel formato)
headers_rapid = {
    'x-rapidapi-key': MY_KEY,
    'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
}

if st.button("VERIFICA ORA"):
    st.write("---")
    st.subheader("Test 1: Host Diretto (api-sports.io)")
    try:
        res1 = requests.get("https://v3.football.api-sports.io/status", headers=headers_direct).json()
        st.json(res1)
    except Exception as e:
        st.error(f"Errore Test 1: {e}")

    st.write("---")
    st.subheader("Test 2: Host RapidAPI (p.rapidapi.com)")
    try:
        res2 = requests.get("https://api-football-v1.p.rapidapi.com/v3/status", headers=headers_rapid).json()
        st.json(res2)
    except Exception as e:
        st.error(f"Errore Test 2: {e}")
