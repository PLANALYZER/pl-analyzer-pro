import streamlit as st
import requests

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# --- PROTEZIONE ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    pwd_inserita = st.text_input("Inserisci la Password:", type="password")
    if st.button("Accedi"):
        if pwd_inserita == "BOMBER2026": # Questa è la tua password
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Password errata")
    st.stop()

# --- SOFTWARE ---
st.title("⚽ PL Analyzer Pro")
st.write("Benvenuto nel software automatico!")

# Sostituisci 'LA_TUA_CHIAVE' con quella ricevuta via mail
API_KEY = "LA_TUA_CHIAVE_QUI" 

camp = st.selectbox("Campionato", ["soccer_italy_serie_a", "soccer_epl"])
if st.button("Scarica Quote"):
    url = f"https://api.the-odds-api.com/v4/sports/{camp}/odds/?apiKey={API_KEY}&regions=eu"
    res = requests.get(url).json()
    st.write(res)
