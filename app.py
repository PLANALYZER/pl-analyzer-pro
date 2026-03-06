import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("📊 PL ANALYZER PRO (Versione a Pagamento)")

# Configurazione API
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def get_predictions():
    # Usiamo la data odierna
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    try:
        response = requests.get(url_fixtures, headers=HEADERS).json()
        fixtures = response.get('response', [])
        
        if not fixtures:
            return "Nessun match trovato per oggi."

        data_list = []
        for f in fixtures[:20]: # Con l'account a pagamento puoi analizzarne di più
            f_id = f['fixture']['id']
            h_id = f['teams']['home']['id']
            a_id = f['teams']['away']['id']
            league_id = f['league']['id']
            season = f['league']['season']

            # 1. Recupero Statistiche (H-Casa e A-Fuori)
            h_res = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={h_id}", headers=HEADERS).json()
            a_res = requests.get(f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={a_id}", headers=HEADERS).json()

            if h_res.get('response') and a_res.get('response'):
                h_s = h_res['response']
                a_s = a_res['response']

                # FORMULA CORRETTA: Media gol FATTI in casa (H) e FATTI fuori (A)
                # Usiamo .get() e float() per evitare errori se il dato è mancante
                avg_h_scored = float(h_s['goals']['for']['average']['home'] or 0)
                avg_a_scored = float(a_s['goals']['for']['average']['away'] or 0)
                
                # Partite giocate nel rispettivo ruolo
                played_h = h_s['fixtures']['played']['home']
                played_a = a_s['fixtures']['played']['away']

                # Forma Ultime 5 (Selettiva)
                forma_h = h_s['form'][-5:] if h_s['form'] else ""
                forma_a = a_s['form'][-5:] if a_s['form'] else ""

                # 2. Analisi Quote Asian (Confronto Opening vs Current)
                odds_res = requests.get(f"https://v3.football.api-sports.io/odds?fixture={f_id}", headers=HEADERS).json()
                trend_odds = "Stabile"
                
                # Logica semplificata: se la media gol totale > 2.5 e forma è buona
                score_pred = avg_h_scored + avg_a_scored
                consiglio = "🔥 OVER 2.5" if score_pred > 2.5 else "⚖️ UNDER / NO BET"

                data_list.append({
                    "Campionato": f['league']['name'],
                    "Match": f"{f['teams']['home']['name']} - {f['teams']['away']['name']}",
                    "Gare (H-Casa)": played_h,
                    "Gare (A-Fuori)": played_a,
                    "Media Gol H (Casa)": avg_h_scored,
                    "Media Gol A (Fuori)": avg_a_scored,
                    "Forma H": forma_h,
                    "Forma A": forma_a,
                    "Pronostico": consiglio
                })
        
        return data_list
    except Exception as e:
        return f"Errore nel calcolo: {str(e)}"

if st.button("ESEGUI ANALISI PROFESSIONALE"):
    with st.spinner("Accesso ai dati Pro in corso..."):
        risultati = get_predictions()
        if isinstance(risultati, list):
            df = pd.DataFrame(risultati)
            st.dataframe(df, use_container_width=True)
        else:
            st.error(risultati)
