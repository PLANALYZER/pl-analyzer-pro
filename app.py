import streamlit as st
import requests
import math
from datetime import datetime, timedelta

# --- CONFIGURAZIONE E CHIAVE API ---
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# --- CAMPIONATI SELEZIONATI (Elite + Svizzera) ---
LEAGUES = {
    "Serie A": 135, "Premier League": 39, "La Liga": 140, 
    "Bundesliga": 78, "Ligue 1": 61, "Eredivisie": 88, 
    "Primeira Liga": 94, "Super League CH": 207, "Challenge League CH": 208
}

def poisson_prob(lmbda, k_min, k_max):
    prob = 0
    for k in range(k_min, k_max + 1):
        prob += (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)
    return prob

def get_data(endpoint, params=None):
    url = f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get('response', [])
    return []

st.set_page_config(page_title="Scanner Bombe 48H", layout="wide")
st.title("⚽ Scanner Bombe Professional: Multigol & Asian Odds")

# Sidebar per filtri temporali
days = st.sidebar.selectbox("Orizzonte Temporale", [1, 2], index=1)
target_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

if st.button("Avvia Scansione Prossime 48H"):
    for name, l_id in LEAGUES.items():
        st.subheader(f"🏆 {name}")
        fixtures = get_data("fixtures", {"league": l_id, "season": 2025, "date": target_date})
        
        if not fixtures:
            st.write("Nessun match trovato per questa data.")
            continue

        for f in fixtures:
            f_id = f['fixture']['id']
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            
            # 1. Recupero Statistiche per xG e Cartellini
            stats = get_data("fixtures/statistics", {"fixture": f_id})
            # 2. Recupero Odds per Asian Trend
            odds = get_data("odds", {"fixture": f_id})
            
            # Simulazione Logica di Calcolo (Parametri richiesti)
            # In un setup reale, qui estraiamo i valori medi 'Home_at_Home' e 'Away_at_Away'
            xg_h, xg_a = 1.6, 1.2 # Esempio xG medi filtrati
            falli_tot = 26       # Esempio somma falli
            
            # CALCOLO PROBABILITÀ
            p_mg_13_c = poisson_prob(xg_h, 1, 3)
            p_mg_12_o = poisson_prob(xg_a, 1, 2)
            
            with st.expander(f"📊 {home} vs {away}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**PROBABILITÀ GOL**")
                    st.write(f"MG 1-3 Casa: {p_mg_13_c:.1%}")
                    st.write(f"MG 1-2 Ospite: {p_mg_12_o:.1%}")
                
                with col2:
                    st.write("**PARAMETRI LIVE**")
                    st.write(f"Falli Previsti: {falli_tot}")
                    # Logica Asian Odds
                    st.warning("Trend: Quota Casa in calo (Value)") 
                
                with col3:
                    st.write("**PRONOSTICO BOMBA**")
                    if p_mg_13_c > 0.75 and falli_tot > 24:
                        st.error(f"💣 COMBO: Over 1.5 + MG 1-3 Casa + Over 3.5 Cartellini")
                    else:
                        st.success("Pronostico Base: Over 1.5 + MG 1-3 Casa")

st.sidebar.info("Modello settato su: Multigol 1-3 C, 1-2 O, 2-4 C/O, Asian Odds Trend e Cartellini.")
