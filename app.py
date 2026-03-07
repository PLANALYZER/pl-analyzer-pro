import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# --- CONFIGURAZIONE API ---
API_HOST = "free-api-live-football-data.p.rapidapi.com"
BASE_URL = "https://free-api-live-football-data.p.rapidapi.com/football-"

st.title("⚽ PL Analyzer Pro")

# Sidebar
api_key = st.sidebar.text_input("Inserisci la tua X-RapidAPI-Key", type="password")
menu = st.sidebar.radio("Menu", ["Fase 1: Selezione Campionati", "Fase 2: Calendario", "Fase 3: Pronostici"])

if menu == "Fase 1: Selezione Campionati":
    st.header("🏆 Filtra i tuoi Campionati")
    st.write("Cerca e seleziona solo i campionati che ti interessano.")

    if st.button("Carica/Aggiorna Lista Globale"):
        if api_key:
            headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
            with st.spinner("Scarico dati..."):
                response = requests.get(f"{BASE_URL}get-all-leagues", headers=headers)
                if response.status_code == 200:
                    st.session_state['all_leagues'] = response.json()["response"]["leagues"]
                    st.success("Lista caricata con successo!")
        else:
            st.error("Inserisci la Key a sinistra!")

    if 'all_leagues' in st.session_state:
        df = pd.DataFrame(st.session_state['all_leagues'])
        
        # --- BOX DI RICERCA ---
        ricerca = st.text_input("Digita il nome del campionato o nazione (es: Italy, Premier, Spain...)", "")
        
        # Filtriamo la tabella in base a cosa scrivi
        df_filtrata = df[df['name'].str.contains(ricerca, case=False) | df['localizedName'].str.contains(ricerca, case=False)]
        
        st.write(f"Risultati trovati: {len(df_filtrata)}")
        
        # --- SELEZIONE MULTIPLA ---
        scelti = st.multiselect("Seleziona i campionati da monitorare:", options=df_filtrata['name'].tolist())
        
        if scelti:
            watchlist = df[df['name'].isin(scelti)][['id', 'name', 'localizedName']]
            st.session_state['watchlist'] = watchlist
            st.subheader("I tuoi Campionati attivi:")
            st.table(watchlist)
            st.success("Ottimo! Ora questi campionati sono salvati. Passa alla Fase 2.")

elif menu == "Fase 2: Calendario":
    st.header("📅 Partite in Programma")
    if 'watchlist' not in st.session_state:
        st.warning("Torna nella Fase 1 e seleziona almeno un campionato!")
    else:
        st.write("Campionati monitorati:", st.session_state['watchlist']['name'].tolist())
        # Qui aggiungeremo il tasto per scaricare le partite di oggi

elif menu == "Fase 3: Pronostici":
    st.header("📈 Analisi Statistica")
    st.write("Seleziona una partita dalla Fase 2 per vedere il pronostico.")
