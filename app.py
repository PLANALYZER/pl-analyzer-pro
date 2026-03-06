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
        # Prendiamo la lista dei match
        all_matches = response.get('response', {}).get('matches', [])
        
        filtered_results = []
        
        for m in all_matches:
            # Creiamo una stringa unica con tutti i nomi del match per cercarci dentro
            match_context = str(m).lower()
            
            # Cerchiamo Serie A, Italy o squadre famose per essere sicuri
            if any(term in match_context for term in ["serie a", "italy", "juventus", "atalanta", "cagliari"]):
                h_team = m.get('homeTeam', {}).get('name', 'N/A')
                a_team = m.get('awayTeam', {}).get('name', 'N/A')
                
                # Statistiche
                h_avg = float(m.get('homeTeam', {}).get('avg_goals', 1.5))
                a_avg = float(m.get('awayTeam', {}).get('avg_goals', 1.2))
                
                filtered_results.append({
                    "Orario": m.get('status', {}).get('startTimeStr', 'N/A'),
                    "Match": f"{h_team} - {a_team}",
                    "Media Gol Casa": h_avg,
                    "Media Gol Ospite": a_avg,
                    "Pronostico": "OVER 2.5" if (h_avg + a_avg) > 2.6 else "UNDER/MULTIGOL"
                })
        
        return filtered_results, all_matches[:3] # Restituiamo anche un esempio di match
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return [], []

if st.button("🔍 GENERA ANALISI"):
    with st.spinner("Scansione database in corso..."):
        risultati, esempio = get_analysis()
        
        if risultati:
            st.success(f"Trovati {len(risultati)} match!")
            st.table(pd.DataFrame(risultati))
        else:
            st.warning("Filtro specifico non riuscito. Vediamo come l'API scrive i dati:")
            # Questo ci mostrerà esattamente come sono scritti i primi 3 match
            st.write(esempio)
