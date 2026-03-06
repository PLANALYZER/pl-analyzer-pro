import streamlit as st
import requests

# --- 1. CONFIGURAZIONE E SICUREZZA ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    password = st.text_input("Inserisci Licenza:", type="password")
    if st.button("Attiva Software"):
        if password == "BOMBER2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Licenza non valida.")
    st.stop()

# --- 2. CHIAVI E DATI ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - 7 PUNTI INTEGRATI")
st.sidebar.info("Versione 2026 - Intelligence Goal")

league_map = {
    "Serie A (IT)": "SA", 
    "Premier League (UK)": "PL", 
    "La Liga (ES)": "PD", 
    "Bundesliga (DE)": "BL1"
}
api_league_map = {
    "Serie A (IT)": "soccer_italy_serie_a",
    "Premier League (UK)": "soccer_epl",
    "La Liga (ES)": "soccer_spain_la_liga",
    "Bundesliga (DE)": "soccer_germany_
