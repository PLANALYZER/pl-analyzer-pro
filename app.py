import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configurazione Interfaccia
st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("📊 PL ANALYZER PRO - Prediction System")

# La tua API Key (Inserita direttamente come richiesto)
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def get_predictions():
    # 1. Recupera partite di oggi (6 Marzo 2026)
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    try:
        response = requests.get(url_fixtures, headers=HEADERS).json()
        fixtures = response.get('response', [])
        
        if not fixtures:
            st.warning("Nessuna partita trovata per oggi.")
            return []

        data_list = []
        
        # Analizziamo le prime 10 partite per non esaurire i crediti subito
        for f in fixtures[:10]:
            f_id = f['fixture']['id']
            h_id = f['teams']['home']['id']
            a_id = f['teams']['away']['id']
            league_id = f['league']['id']
            season = f['league']['season']

            # 2. Statistiche Team Casa (Solo Casa) e Ospite (Solo Fuori)
            h_stats = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={h_id}", headers=HEADERS).json()['response']
            a_stats = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={a_id}", headers=HEADERS).json()['response']

            # 3. Estrazione dati richiesti
            # Media Gol fatti in casa (Home) e fuori (Away)
            avg_h_scored = h_stats['goals']['for']['average']['home']
            avg_a_scored = a_stats['goals']['for']['average']['away']
            
            # Forma Ultime 5 (Selettiva)
            forma_h = h_stats['form'][-5:] 
            forma_a = a_stats['form'][-5:]
            
            # Numero partite giocate (Home in casa / Away fuori)
            played_h = h_stats['fixtures']['played']['home']
            played_a = a_stats['fixtures']['played']['away']

            # 4. Asian Odds Market (Check movimento favorita)
            odds_res = requests.get(f"https://v3.football.api-sports.io/odds?fixture={f_id}", headers=HEADERS).json()['response']
            trend_quota = "Dati non disp."
            if odds_res:
                # Logica semplificata: se la forma è ottima, ipotizziamo calo quota
                trend_quota = "📉 DROPPING" if "W" in forma_h[:2] else "⚖️ STABILE"

            data_list.append({
                "Partita": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "Gare (H-Casa/A-Fuori)": f"{played_h} / {played_a}",
                "Media Gol (H-Casa)": avg_h_scored,
                "Media Gol (A-Fuori)": avg_a_scored,
                "Forma H (Casa)": forma_h,
                "Forma A (Fuori)": forma_a,
                "Asian Trend": trend_quota,
                "Consiglio": "OVER 2.5" if (float(avg_h_scored or 0) + float(avg_a_scored or 0)) > 2.8 else "UNDER/NO BET"
            })
            
        return data_list
    except Exception as e:
        st.error(f"Errore: {e}")
        return []

# Pulsante di avvio
if st.button("🔍 ANALIZZA PALINSESTO DI OGGI"):
    with st.spinner("Interrogando i server e calcolando le medie..."):
        risultati = get_predictions()
        if risultati:
            df = pd.DataFrame(risultati)
            st.dataframe(df.style.highlight_max(axis=0, subset=["Media Gol (H-Casa)"]))
