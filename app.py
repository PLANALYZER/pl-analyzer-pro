import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ultimate PL Analyzer - Business", layout="wide")

st.title("🏆 PL Analyzer Pro (Versione Illimitata)")
st.write("Software di analisi senza costi API - Copertura Europea Totale")

# Mappa dei campionati su FBRef (Esempi)
LEAGUE_URLS = {
    "Serie A 🇮🇹": "https://fbref.com/it/comp/11/Statistiche-di-Serie-A",
    "Polonia 🇵🇱": "https://fbref.com/it/comp/36/Statistiche-di-Ekstraklasa",
    "Bulgaria 🇧🇬": "https://fbref.com/it/comp/69/Statistiche-di-First-Professional-Football-League",
    "Svizzera 🇨🇭": "https://fbref.com/it/comp/57/Statistiche-di-Super-League",
    "Danimarca 🇩🇰": "https://fbref.com/it/comp/50/Statistiche-di-Superliga"
}

scelta = st.sidebar.selectbox("Seleziona Campionato", list(LEAGUE_URLS.keys()))

@st.cache_data(ttl=86400) # Salva i dati per 24 ore per essere velocissimo
def load_data(url):
    # Legge tutte le tabelle della pagina
    tables = pd.read_html(url)
    df = tables[0] # La prima tabella è sempre la classifica
    return df

try:
    data = load_data(LEAGUE_URLS[scelta])
    
    # Pulizia nomi colonne per FBRef
    data = data[['Squadra', 'MP', 'GF', 'GS', 'DR', 'Pti', 'Ultimi 5']]
    
    st.subheader(f"Classifica e Forma Recente: {scelta}")
    st.dataframe(data, use_container_width=True)

    c1, c2 = st.columns(2)
    casa = c1.selectbox("Squadra in Casa", data['Squadra'].unique())
    fuori = c2.selectbox("Squadra in Trasferta", data['Squadra'].unique())

    if st.button("GENERA PRONOSTICO"):
        # Estrazione dati per algoritmo
        stats_casa = data[data['Squadra'] == casa].iloc[0]
        stats_fuori = data[data['Squadra'] == fuori].iloc[0]
        
        # Calcolo medie gol (Semplificato per il prototipo)
        media_gol_casa = stats_casa['GF'] / stats_casa['MP']
        media_gol_fuori = stats_fuori['GF'] / stats_fuori['MP']
        tot_media = (media_gol_casa + media_gol_fuori)

        st.divider()
        st.subheader("🎯 Consiglio Algoritmo")
        
        # I TUOI 5 CONSIGLI BASATI SUI DATI REALI
        if tot_media > 3.2:
            st.success("🔥 Suggerimento: **OVER 3.5**")
        elif tot_media > 2.6:
            st.success("⚽ Suggerimento: **GOAL + OVER 2.5**")
        elif tot_media > 2.2:
            st.success("✅ Suggerimento: **OVER 2.5**")
        elif tot_media > 1.6:
            st.info("👍 Suggerimento: **OVER 1.5**")
        else:
            st.warning("⚠️ Suggerimento: **NO BET** (Partita da Under)")

except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
    st.info("Nota: FBRef potrebbe limitare le richieste frequenti. Il sistema usa la cache per proteggerti.")
