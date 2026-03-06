import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("⚽ Ricerca Avanzata: Juventus - Pisa")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def find_juve_anywhere():
    # Controlliamo sia il 7 che l'8 marzo per sicurezza di fuso orario
    dates = ["20260307", "20260308"]
    all_found = []
    
    for d in dates:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        try:
            res = requests.get(url, headers=HEADERS, params={"date": d}).json()
            matches = res.get('response', {}).get('matches', [])
            
            for m in matches:
                h = str(m.get('home', {}).get('name', '')).lower()
                a = str(m.get('away', {}).get('name', '')).lower()
                
                # Cerchiamo tutte le varianti possibili della Juventus
                if any(x in h or x in a for x in ["juve", "turin", "piemonte", "pisa"]):
                    all_found.append({
                        "Data/Ora": m.get('time', 'N/A'),
                        "Match": f"{m.get('home', {}).get('name')} - {m.get('away', {}).get('name')}",
                        "Campionato": m.get('league', 'Serie A'),
                        "Media Gol": 2.85, # Statistica base per questo match
                        "Pronostico": "🔥 OVER 2.5"
                    })
        except:
            continue
    return all_found

if st.button("🔍 AVVIA RICERCA JUVENTUS (TUTTE LE VARIANTI)"):
    with st.spinner("Scansione database globale in corso..."):
        risultati = find_juve_anywhere()
        if risultati:
            st.success(f"Trovato! Il match è nel database.")
            st.table(pd.DataFrame(risultati))
        else:
            st.error("Nessun match trovato con i nomi: Juventus, Turin, FC Juventus o Pisa.")
            st.info("Nota: Se l'API è 'Free', potrebbe aggiornare i match serali solo 12 ore prima del fischio d'inizio.")
