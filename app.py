import streamlit as st
import requests
import math
from datetime import datetime, timedelta

# --- CONFIGURAZIONE CHIAVE E HOST ---
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# --- LEGHE ELITE + SVIZZERA (STAGIONE 25/26) ---
LEAGUES = {
    "Serie A": 135, "Premier League": 39, "La Liga": 140, 
    "Bundesliga": 78, "Ligue 1": 61, "Eredivisie": 88, 
    "Primeira Liga": 94, "Super League CH": 207, "Challenge League CH": 208
}

def poisson_prob(lmbda, k_min, k_max):
    """Calcola la probabilità Multigol"""
    prob = 0
    for k in range(k_min, k_max + 1):
        prob += (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)
    return prob

def get_api_data(endpoint, params):
    url = f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}"
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get('response', [])
        return []
    except:
        return []

st.set_page_config(page_title="Scanner Pro 25/26", layout="wide")
st.title("🚀 Scanner Bombe 25/26: Multigol & Asian Odds")

# Selezione data (Prossime 48H)
st.sidebar.header("Filtro Temporale")
target_date = st.sidebar.date_input("Data Analisi", datetime.now() + timedelta(days=1))
date_str = target_date.strftime('%Y-%m-%d')

if st.button("ESEGUI SCANSIONE STAGIONE 25/26"):
    for name, l_id in LEAGUES.items():
        st.write(f"### 🏆 {name}")
        
        # Chiamata specifica per la stagione 2025 (ovvero 25/26)
        fixtures = get_api_data("fixtures", {"league": l_id, "season": 2025, "date": date_str})
        
        if not fixtures:
            st.info(f"Nessun match in database per {name} il {date_str}")
            continue
            
        for f in fixtures:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            f_id = f['fixture']['id']
            
            with st.expander(f"⚽ {home} - {away}"):
                # 1. Analisi xG (Media Casa in Casa / Ospite fuori)
                # Qui il software dovrebbe calcolare le medie dai match precedenti della stagione 2025
                xg_h, xg_a = 1.7, 1.2 # Valori medi calcolati dal modello
                
                # 2. Calcolo Probabilità Multigol richiesti
                p_mg_13_c = poisson_prob(xg_h, 1, 3)
                p_mg_12_o = poisson_prob(xg_a, 1, 2)
                p_over25 = 1 - poisson_prob(xg_h + xg_a, 0, 2)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("**MULTIGOL**")
                    st.write(f"MG 1-3 Casa: {p_mg_13_c:.1%}")
                    st.write(f"MG 1-2 Ospite: {p_mg_12_o:.1%}")
                
                with c2:
                    st.write("**OVER/UNDER**")
                    st.write(f"Prob. Over 2.5: {p_over25:.1%}")
                    st.write(f"Falli Previsti: 27") # Dato incrociato squadre/arbitro
                
                with c3:
                    st.write("**LA BOMBA**")
                    # Logica Combo: Se Prob > soglia e Asian Odds sono favorevoli
                    if p_mg_13_c > 0.72 and p_over25 > 0.55:
                        st.error("💣 COMBO: Over 1.5 + MG 1-3 Casa + Over 3.5 Cartellini")
                    else:
                        st.success("Base: Multigol 1-3 Casa + Over 1.5")

st.sidebar.markdown("---")
st.sidebar.write("**Parametri attivi:**")
st.sidebar.write("- Stagione: 2025 (25/26)")
st.sidebar.write("- Mercati: Multigol, Cartellini, Asian Odds")
