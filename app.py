import streamlit as st
import requests

# 1. Configurazione della pagina
st.set_page_config(page_title="PL Analyzer Pro", layout="wide")

# 2. Sistema di Accesso (Password per la vendita)
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato - PL Analyzer")
    st.write("Inserisci la chiave d'accesso ricevuta dopo il pagamento PayPal.")
    
    # Puoi cambiare questa password quando vuoi per i nuovi clienti
    password_master = "BOMBER2026" 
    
    input_pass = st.text_input("Chiave d'accesso:", type="password")
    
    if st.button("Sblocca Software"):
        if input_pass == password_master:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Chiave errata. Controlla l'email di conferma.")
    st.stop() # Blocca il resto del codice se non sei loggato

# 3. Interfaccia del Software (Cosa vede il cliente che paga)
st.title("⚽ PL Analyzer Pro - Intelligence Dati")
st.sidebar.success("Licenza Attiva")

# INSERISCI QUI LA TUA CHIAVE API (quella che ti è arrivata via email)
API_KEY = "IL_TUO_CODICE_QUI" 

# Selezione del Campionato
campionato = st.selectbox("Seleziona il Campionato da analizzare:", 
                          ["soccer_italy_serie_a", "soccer_epl", "soccer_spain_la_liga", "soccer_germany_bundesliga"])

if st.button("Analizza Partite e Trend Quote"):
    st.info("Ricerca in corso nei database dei bookmaker...")
    
    # Chiamata alle API per le quote
    url = f"https://api.the-odds-api.com/v4/sports/{campionato}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    response = requests.get(url)
    
    if response.status_code == 200:
        partite = response.json()
        
        if not partite:
            st.warning("Nessuna partita trovata al momento.")
        
        for match in partite:
            with st.expander(f"📊 {match['home_team']} vs {match['away_team']}"):
                st.write("**Analisi Quote (Market Move):**")
                
                # Mostriamo le quote dei primi 2 bookmaker trovati
                for bookie in match['bookmakers'][:2]:
                    st.write(f"Sito: {bookie['title']}")
                    odds = bookie['markets'][0]['outcomes']
                    col1, col2, col3 = st.columns(3)
                    col1.metric(f"1 ({odds[0]['name']})", odds[0]['price'])
                    col2.metric(f"2 ({odds[1]['name']})", odds[1]['price'])
                    if len(odds) > 2:
                        col3.metric("X", odds[2]['price'])
    else:
        st.error("Errore di connessione. Verifica di aver inserito correttamente la tua API KEY.")

# 4. Nota per l'utente
st.sidebar.divider()
st.sidebar.write("© 2026 PL Analyzer - Solo Cibo Vero per le tue scommesse.")
