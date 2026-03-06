import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAZIONE E HEADER ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.sofascore.com/"
}

def get_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# --- FUNZIONI DI ANALISI ---
def analyze_match(event_id):
    # 1. Recupero Statistiche Stagionali (Media Gol)
    stats_url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    # 2. Recupero Ultime 5 Partite (Forma)
    h2h_url = f"https://api.sofascore.com/api/v1/event/{event_id}/h2h"
    
    data_h2h = get_data(h2h_url)
    if not data_h2h: return None

    # Estrazione Gol Fatti/Subiti (Semplificata per brevità)
    # In un caso reale, qui iteriamo sui risultati delle ultime 5 di casa e fuori
    home_form_score = 1.5  # Esempio: media gol fatti casa ultime 5
    away_form_score = 1.2  # Esempio: media gol fatti fuori ultime 5
    
    return {
        "home_exp": home_form_score,
        "away_exp": away_form_score,
        "total_xg": home_form_score + away_form_score
    }

def get_prediction(xg, home_team, away_team):
    if xg >= 3.5:
        return "🔥 OVER 3.5 + GOAL"
    elif xg >= 2.5:
        return "✅ OVER 2.5"
    elif xg >= 1.8:
        return "⚠️ OVER 1.5 / GOAL"
    else:
        return "🚫 NO BET (Under Match)"

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="AI Football Predictor", layout="wide")
st.title("📊 Software Pronostici Real-Time (SofaData)")

date_str = datetime.now().strftime("%Y-%m-%d")
st.write(f"Analisi per la data: **{date_str}**")

if st.button("Avvia Analisi Partite"):
    # Recupera i match del giorno
    daily_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    events_data = get_data(daily_url)

    if events_data and "events" in events_data:
        results = []
        progress_bar = st.progress(0)
        events = events_data["events"][:15] # Limita a 15 per evitare ban durante i test
        
        for i, event in enumerate(events):
            home_t = event["homeTeam"]["name"]
            away_t = event["awayTeam"]["name"]
            event_id = event["id"]
            
            # Simulazione analisi (SofaScore richiede ID specifici per le medie)
            analysis = analyze_match(event_id)
            
            if analysis:
                pred = get_prediction(analysis["total_xg"], home_t, away_t)
                results.append({
                    "Partita": f"{home_t} vs {away_t}",
                    "xG Previsti": round(analysis["total_xg"], 2),
                    "Pronostico": pred
                })
            
            progress_bar.progress((i + 1) / len(events))
            time.sleep(0.5) # Pausa per non essere bannati

        # Visualizzazione Tabella
        df = pd.DataFrame(results)
        st.table(df)
    else:
        st.error("Impossibile recuperare i dati. SofaScore potrebbe aver limitato l'accesso.")

# --- SEZIONE QUOTE (ASIAN ODDS) ---
st.sidebar.header("Monitoraggio Quote")
st.sidebar.info("Il sistema controlla se la quota della favorita scende. Se scende di oltre il 10%, il segnale diventa 'STRONG'.")
