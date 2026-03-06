import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Analisi Match PRO - 7 Marzo")

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
        # Otteniamo la lista dei match
        all_matches = response.get('response', {}).get('matches', [])
        
        filtered_results = []
        
        for m in all_matches:
            # Cerchiamo i nomi delle squadre in diversi possibili formati dell'API
            h_name = m.get('homeTeam', {}).get('name') or m.get('home_team') or m.get('team_home', {}).get('name', 'N/A')
            a_name = m.get('awayTeam', {}).get('name') or m.get('away_team') or m.get('team_away', {}).get('name', 'N/A')
            
            # Cerchiamo il nome della lega
            league_obj = m.get('league', {})
            l_name = league_obj.get('name', '') if isinstance(league_obj, dict) else str(league_obj)

            # FILTRO: Italia o Serie A o Juventus (per test)
            match_text = (str(h_name) + str(a_name) + l_name).lower()
            
            if any(x in match_text for x in ["italy", "serie a", "juventus", "atalanta", "milan", "inter"]):
                # Medie gol (uso 1.5 e 1.2 come base se l'API non le fornisce nel json dei match)
                h_avg = float(m.get('homeTeam', {}).get('avg_goals', 1.50))
                a_avg = float(m.get('awayTeam', {}).get('avg_goals', 1.20))
                
                filtered_results.append({
                    "Campionato": l_name if l_name else "Serie A",
                    "Match": f"{h_name} - {a_name}",
                    "Media Gol Casa": h_avg,
                    "Media Gol Ospite": a_avg,
                    "Pronostico": "🔥 OVER 2.5" if (h_avg + a_avg) > 2.6 else "MULTIGOL"
                })
        
        return filtered_results, all_matches[0] if all_matches else None
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return [], None

if st.button("🔍 GENERA ANALISI DEFINITIVA"):
    with st.spinner("Estrazione dati in corso..."):
        risultati, raw_example = get_analysis()
        
        if risultati:
            st.success(f"Trovati {len(risultati)} match!")
            df = pd.DataFrame(risultati)
            st.table(df)
        else:
            st.warning("Non sono riuscito a leggere i nomi delle squadre. Analizzo la struttura dei dati...")
            # Questo ci dice esattamente come l'API chiama i campi
            st.write("Esempio dati raw del primo match per correggere i nomi:", raw_example)
