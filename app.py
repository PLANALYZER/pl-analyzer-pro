import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Serie A PRO - Analisi Sabato 7 Marzo")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_complete_data():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
    # Prendiamo i dati del 7 Marzo
    params = {"date": "20260307"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        matches = response.get('response', {}).get('matches', [])
        
        final_list = []
        for m in matches:
            # Identifichiamo i nomi delle squadre e della lega
            h_name = m.get('home', {}).get('name', '')
            a_name = m.get('away', {}).get('name', '')
            l_id = str(m.get('leagueId', ''))
            ora = m.get('time', 'N/A')

            # FILTRO: Deve essere Serie A (55) E non deve essere un match già finito del 6 marzo
            if l_id == "55" and "06.03" not in ora:
                
                # Calcolo Medie Personalizzate
                if "Juventus" in h_name or "Juve" in h_name:
                    base_h, base_a = 2.15, 0.75 # Juventus molto favorita in casa
                elif "Atalanta" in h_name:
                    base_h, base_a = 1.95, 1.10
                else:
                    base_h, base_a = 1.55, 1.15
                
                final_list.append({
                    "Orario": ora,
                    "Incontro": f"{h_name} - {a_name}",
                    "Media Gol Casa": base_h,
                    "Media Gol Ospite": base_a,
                    "Pronostico": "🔥 OVER 2.5" if (base_h + base_a) > 2.6 else "⚖️ MULTIGOL 2-4"
                })
        
        # Ordiniamo per orario così la Juve appare per ultima (20:45)
        return sorted(final_list, key=lambda x: x['Orario'])
    except Exception as e:
        return []

if st.button("📊 MOSTRA TUTTA LA SERIE A DI DOMANI"):
    with st.spinner("Ricerca in corso (inclusa Juventus)..."):
        risultati = get_complete_data()
        if risultati:
            st.success(f"Trovati {len(risultati)} match!")
            st.table(pd.DataFrame(risultati))
        else:
            st.error("Nessun match trovato. Prova a ricaricare tra qualche minuto.")
