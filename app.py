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
    
    # Questa è la password che darai ai tuoi clienti
    password_master = "BOMBER2026" 
    
    input_pass = st.text_input("Chiave d'accesso:", type="password")
    
    if st.button("Sblocca Software"):
        if input_pass == password_master:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Chiave errata. Controlla l'email di conferma.")
    st.stop() 

# 3. Interfaccia del Software
st.title("⚽ PL Analyzer Pro - Intelligence Dati")
st.sidebar.success("Licenza Attiva")

# --- LA TUA API KEY INSERITA ---
API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd" 

# Selezione del Campionato
campionato = st.selectbox("Seleziona il Campionato da analizzare:", 
                          ["soccer_italy_serie_a", "soccer_epl", "soccer_spain_la_liga", "soccer_germany_bundesliga"])

if st.button("Analizza Partite e Trend Quote"):
    st.info("Ricerca in corso nei database dei bookmaker...")
    
    # Chiamata alle API per le quote
    url = f"https://api.the-odds-api.com/v4/sports/{campionato}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            partite = response.json()
            
            if not partite:
                st.warning("Nessuna partita trovata al momento per questo campionato.")
            
            for match in partite:
                with st.expander(f"📊 {match['home_team']} vs {match['away_team']}"):
                    st.write("**Quote Attuali (Testa a Testa):**")
                    
                    # Mostriamo i dati dei bookmaker disponibili
                    for bookie in match['bookmakers'][:3]: # Mostra fino a 3 bookmaker
                        st.write(f"--- {bookie['title']} ---")
                        odds = bookie['markets'][0]['outcomes']
                        
                        col1, col2, col3 = st.columns(3)
                        # Cerchiamo di mappare 1, X, 2 correttamente
                        for outcome in odds:
                            if outcome['name'] == match['home_team']:
                                col1.metric("1 (Casa)", outcome['price'])
                            elif outcome['name'] == match['away_team']:
                                col3.metric("2 (Ospite)", outcome['price'])
                            else:
                                col2.metric("X (Pareggio)", outcome['price'])
        else:
            st.error(f"Errore API: {response.status_code}. Verifica il tuo piano su The Odds API.")
    except Exception as e:
        st.error(f"Si è verificato un errore tecnico: {e}")

# 4. Nota per l'utente
st.sidebar.divider()
st.sidebar.write("© 2026 PL Analyzer - Solo Cibo Vero per le tue scommesse.")
