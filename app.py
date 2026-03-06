import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Serie A PRO - Analisi 7 Marzo")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_analysis():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
    params = {"date": "20260307"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        # Navighiamo nella struttura che abbiamo visto nell'ultimo screenshot
        all_matches = response.get('response', {}).get('matches', [])
        
        serie_a_results = []
        campionati_trovati = set() # Per debug
        
        for m in all_matches:
            # Estraiamo il nome del campionato in modo sicuro
            league_obj = m.get('league', {})
            l_name = ""
            if isinstance(league_obj, dict):
                l_name = league_obj.get('name', '')
            else:
                l_name = str(league_obj)
            
            campionati_trovati.add(l_name)

            # FILTRO AGGRESSIVO: Cerca Serie A o Italy
            if "Serie A" in l_name or "Italy" in l_name:
                h_team = m.get('homeTeam', {}).get('name', 'N/A')
                a_team = m.get('awayTeam', {}).get('name', 'N/A')
                
                # Calcolo medie (usando dati reali se presenti, o 0)
                h_avg = float(m.get('homeTeam', {}).get('avg_goals', 0) or 0)
                a_avg = float(m.get('awayTeam', {}).get('avg_goals', 0) or 0)
                
                # Pronostico
                score = h_avg + a_avg
                consiglio = "🔥 OVER" if score > 2.5 else "⚖️ MULTIGOL"

                serie_a_results.append({
                    "Campionato": l_name,
                    "Match": f"{h_team} - {a_team}",
                    "Media Gol H": h_avg,
                    "Media Gol A": a_avg,
                    "Pronostico": consiglio
                })
        
        return serie_a_results, sorted(list(campionati_trovati))
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return [], []

if st.button("🔍 GENERA PRONOSTICI"):
    with st.spinner("Analizzando i 614 match..."):
        risultati, lista_leghe = get_analysis()
        
        if risultati:
            st.success(f"Trovati {len(risultati)} match!")
            st.table(pd.DataFrame(risultati))
        else:
            st.warning("Ancora nessun match trovato con il filtro 'Serie A'.")
            with st.expander("Vedi tutti i campionati disponibili per domani"):
                st.write(lista_leghe)
