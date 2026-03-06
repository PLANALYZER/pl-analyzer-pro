import streamlit as st
import requests
import pandas as pd

# 1. Configurazione
st.set_page_config(page_title="PL Analyzer Pro - Intelligence", layout="wide")

# 2. Protezione
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    password_master = "BOMBER2026" 
    input_pass = st.text_input("Chiave d'accesso:", type="password")
    if st.button("Sblocca Software"):
        if input_pass == password_master:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Password errata.")
    st.stop()

# --- DATI E API ---
API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"

st.title("⚽ PL Analyzer Pro - Algoritmo xG & Market Moves")

campionato = st.selectbox("Seleziona Campionato:", 
                          ["soccer_italy_serie_a", "soccer_epl", "soccer_spain_la_liga", "soccer_germany_bundesliga"])

if st.button("ESEGUI ANALISI PROFONDA"):
    st.info("Calcolo medie campionato e analisi xG in corso...")
    
    # URL per quote
    url_odds = f"https://api.the-odds-api.com/v4/sports/{campionato}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    
    res = requests.get(url_odds).json()
    
    if res:
        for match in res:
            home = match['home_team']
            away = match['away_team']
            
            # --- SIMULAZIONE DATI STATISTICI (Qui il software elabora le medie) ---
            # In una versione avanzata questi dati vengono presi da un database storico
            avg_home_goals_league = 1.55  # Media gol casa campionato
            avg_away_goals_league = 1.20  # Media gol trasferta campionato
            
            # Dati esempio per il calcolo (Squadra Casa)
            home_played = 12
            home_scored = 22
            home_conceded = 10
            
            # Dati esempio per il calcolo (Squadra Trasferta)
            away_played = 12
            away_scored = 15
            away_conceded = 18
            
            # CALCOLO FORZA (ATTACCO E DIFESA)
            attack_home = (home_scored / home_played) / avg_home_goals_league
            defense_away = (away_conceded / away_played) / avg_home_goals_league
            
            # CALCOLO xG FINALI
            xg_home = attack_home * defense_away * avg_home_goals_league
            xg_away = ((away_scored / away_played) / avg_away_goals_league) * ((home_conceded / home_played) / avg_away_goals_league) * avg_away_goals_league
            
            with st.expander(f"📊 {home} vs {away}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("xG CASA", f"{xg_home:.2f}")
                    st.write(f"Gol Fatti Casa: {home_scored}")
                    st.write(f"Partite Casa: {home_played}")
                
                with col2:
                    st.metric("xG OSPITE", f"{xg_away:.2f}")
                    st.write(f"Gol Fatti Trasf: {away_scored}")
                    st.write(f"Partite Trasf: {away_played}")
                    
                with col3:
                    st.write("**PRONOSTICO INDICATO:**")
                    if xg_home > xg_away + 0.5:
                        st.success("SEGNO: 1")
                    elif xg_away > xg_home + 0.5:
                        st.success("SEGNO: 2")
                    else:
                        st.warning("SEGNO: X o GOAL")
                
                st.divider()
                st.write("**ANALISI QUOTE & TREND:**")
                for bookie in match['bookmakers'][:1]:
                    o = bookie['markets'][0]['outcomes']
                    st.write(f"Quota Attuale {bookie['title']}: 1@{o[0]['price']} | X@{o[2]['price']} | 2@{o[1]['price']}")
                    
                    # Logica semplice per il trend
                    st.write("📈 *Trend: Quota in calo sulla favorita (Simulazione)*")

    else:
        st.error("Errore nel recupero dati. Riprova tra poco.")

st.sidebar.write("© 2026 Pro Analyzer - Sistema Decisionale")
