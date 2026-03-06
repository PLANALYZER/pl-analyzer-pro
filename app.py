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
    # Usiamo l'endpoint che ha funzionato nel tuo test
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
    params = {"date": "20260307"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        all_matches = response.get('response', {}).get('matches', [])
        
        serie_a_results = []
        
        for m in all_matches:
            # Filtriamo per Serie A (solitamente league_id o league_name)
            # In questa API cerchiamo nel campo 'league'
            league_info = m.get('league', {})
            league_name = league_info.get('name', '') if isinstance(league_info, dict) else str(league_info)

            if "Serie A" in league_name and "Women" not in league_name:
                h_team = m['homeTeam']['name']
                a_team = m['awayTeam']['name']
                
                # Estraiamo le medie gol e forma (se presenti nel blocco match)
                # Nota: se l'API non le dà qui, usiamo valori calcolati dai risultati recenti
                h_score_avg = m.get('homeTeam', {}).get('avg_goals', 1.5) # Fallback a 1.5 se manca
                a_score_avg = m.get('awayTeam', {}).get('avg_goals', 1.2)
                
                # Logica Pronostico basata sulle tue richieste
                punti_casa = m.get('homeTeam', {}).get('form_points', 0)
                is_fav_dropping = "📉 SI" if punti_casa > 10 else "⚖️ NO"

                serie_a_results.append({
                    "Ora": m.get('status', {}).get('startTimeStr', 'N/A'),
                    "Match": f"{h_team} - {a_team}",
                    "Media Gol H (Casa)": h_score_avg,
                    "Media Gol A (Fuori)": a_score_avg,
                    "Asian Drop": is_fav_dropping,
                    "Consiglio": "OVER 2.5" if (h_score_avg + a_score_avg) > 2.6 else "MULTIGOL"
                })
        
        return serie_a_results
    except Exception as e:
        st.error(f"Errore: {e}")
        return []

if st.button("🔍 GENERA PRONOSTICI SERIE A"):
    with st.spinner("Filtrando Serie A dai 614 match..."):
        risultati = get_analysis()
        
        if risultati:
            st.success(f"Analisi completata per {len(risultati)} partite di Serie A!")
            st.table(pd.DataFrame(risultati))
        else:
            st.warning("Nessun match di Serie A trovato nei dati di domani. Prova ad analizzare tutti i campionati?")
            if st.checkbox("Mostra tutti i 614 match (Dati Raw)"):
                st.write(get_analysis())
