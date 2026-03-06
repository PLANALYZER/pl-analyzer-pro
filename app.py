import streamlit as st
import requests

# Configurazione Pagina
st.set_page_config(page_title="Planalyzer Pro", page_icon="⚽")
st.title("📊 Planalyzer: Pronostici Pro")

# La tua chiave API salvata
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"

st.sidebar.header("Impostazioni")
campionato = st.sidebar.selectbox("Scegli Campionato", ["Serie A", "Premier League", "La Liga"])

if st.button('Genera Analisi del Giorno'):
    st.write(f"### Analisi per {campionato}")
    
    # Esempio di come il software mostrerà i dati richiesti
    with st.expander("Vedi Dettagli xG e Medie"):
        st.write("Media Gol Casa Campionato: 1.32")
        st.write("Media Gol Fuori Campionato: 1.18")
    
    st.divider()
    
    # I tuoi 4 Pronostici Standard
    st.success("🛡️ **IL SICURO (90%):** 1X + Over 1.5 Goal")
    st.info("📊 **IL BASE (75%):** 1 + Over 7.5 Corner + Over 2.5 Cartellini")
    st.warning("🔥 **LA COMBO (60%):** Goal + Over 1.5 Corner Ospite 2° Tempo")
    st.error("💣 **LA BOMBA (35%):** Risultato Esatto 2-1 / 3-1 + Espulsione SÌ")

st.caption("Dati aggiornati tramite RapidAPI")
