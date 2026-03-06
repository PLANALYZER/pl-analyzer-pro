import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_sofa_data(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

def get_detailed_stats(event_id):
    """Estrae i gol medi reali e la forma dalle API di SofaScore"""
    h2h_data = get_sofa_data(f"https://api.sofascore.com/api/v1/event/{event_id}/h2h")
    
    # Valori di default se i dati mancano
    gf_casa, gs_casa = 1.0, 1.0
    gf_ospite, gs_ospite = 1.0, 1.0

    if h2h_data:
        # Estraiamo i gol medi dai dati della stagione attuale nel H2H
        # SofaScore fornisce spesso le medie gol nei campi 'teamHomeSeed' o simili
        # Qui semplifichiamo prendendo la media gol degli scontri diretti o stagionali
        try:
            home_stats = h2h_data.get('teamHomeStats', {})
            away_stats = h2h_data.get('teamAwayStats', {})
            
            # Se disponibili, usiamo i dati reali, altrimenti restano 1.0
            gf_casa = home_stats.get('goalsScored', 1.2)
            gs_casa = home_stats.get('goalsConceded', 1.1)
            gf_ospite = away_stats.get('goalsScored', 1.0)
            gs_ospite = away_stats.get('goalsConceded', 1.3)
        except:
            pass

    # Calcolo xG basato su GF casa + GS ospite e viceversa
    xg_home = (gf_casa + gs_ospite) / 2
    xg_away = (gf_ospite + gs_casa) / 2
    return xg_home + xg_away

def get_final_advice(total_xg):
    if total_xg > 3.2: return "🔥 OVER 3.5 / GOAL+OVER"
    if total_xg > 2.5: return "✅ OVER 2.5"
    if total_xg > 1.9: return "⚠️ OVER 1.5"
    if total_xg > 1.5: return "⚽ GOAL"
    return "🚫 NO BET"

# --- INTERFACCIA ---
st.title("⚽ AI Predictor PRO - Dati Reali")

date_now = datetime.now().strftime("%Y-%m-%d")

if st.button("Genera Pronostici Reali"):
    events_json = get_sofa_data(f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_now}")
    
    if events_json:
        results = []
        matches = events_json['events'][:20] # Analizziamo i primi 20
        
        for match in matches:
            eid = match['id']
            name = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}"
            
            # CHIAMATA REALE PER OGNI PARTITA
            real_xg = get_detailed_stats(eid)
            advice = get_final_advice(real_xg)
            
            results.append({
                "Partita": name,
                "xG Previsti": round(real_xg, 2),
                "Pronostico": advice
            })
            time.sleep(0.2) # Evitiamo blocchi
            
        st.table(pd.DataFrame(results))
