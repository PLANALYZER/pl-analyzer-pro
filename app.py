import streamlit as st
import requests
import pandas as pd

st.title("⚽ PL Analyzer Pro")
st.write("Benvenuto! Configura la tua API nella barra laterale.")

menu = st.sidebar.radio("Menu", ["Fase 1: Liste", "Fase 2: Calendario", "Fase 3: Pronostici"])
api_key = st.sidebar.text_input("Inserisci API Key", type="password")
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# --- DATI TECNICI DALLE TUE IMMAGINI ---
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com/football-"

st.title("⚽ PL Analyzer Pro")

# Sidebar per la Key e la Navigazione
api_key = st.sidebar.text_input("Inserisci la tua X-RapidAPI-Key", type="password")
menu = st.sidebar.radio("Menu", ["Fase 1: Liste", "Fase 2: Calendario", "Fase 3: Pronostici"])

if menu == "Fase 1: Liste":
    st.header("🏆 Caricamento Campionati")
    st.write("Scarichiamo la lista completa dei campionati per ottenere gli ID.")

    if st.button("Aggiorna Lista Campionati"):
        if not api_key:
            st.error("Inserisci la Key nella barra laterale!")
        else:
            headers = {
                "X-Rapidapi-Key": api_key,
                "X-Rapidapi-Host": API_HOST
            }
            with st.spinner("Recupero dati da RapidAPI..."):
                # Endpoint esatto visto nelle tue immagini
                url = f"{BASE_URL}get-all-leagues"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # Navighiamo nella struttura dei dati della tua API
                    if "response" in data and "leagues" in data["response"]:
                        df = pd.DataFrame(data["response"]["leagues"])
                        st.success(f"Trovati {len(df)} campionati!")
                        st.dataframe(df) # Mostra la tabella
                    else:
                        st.json(data) # Debug se la struttura è diversa
                else:
                    st.error(f"Errore {response.status_code}: Controlla la Key.")

elif menu == "Fase 2: Calendario":
    st.header("📅 Calendario Partite")
    st.write("Qui vedremo i match in programma.")

elif menu == "Fase 3: Pronostici":
    st.header("📈 Analisi e Pronostico")
    st.write("Algoritmo in fase di sviluppo...")
