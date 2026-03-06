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
    # Chiediamo i match del 7 Marzo
    params = {"date": "20260307"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        matches = response.get('response', {}).get('matches', [])
        
        final_list = []
        for m in matches:
            # Filtro per Serie A (ID 55)
            if str(m.get('leagueId')) == "55":
                h_name = m.get('home', {}).get('name', 'N/A')
                a_name = m.get('away', {}).get('name', 'N/A')
                ora = m.get('time', 'N/A')
                
                # Escludiamo solo i match già finiti del venerdì (come Napoli-Torino)
                # ma teniamo tutto quello che accade sabato 7
                if "06.03" not in ora:
                    # Statistiche personalizzate
                    if "Juventus" in h_name:
                        base_h, base_a = 2.10, 0.85
                    elif "Atalanta" in h_name:
                        base_h, base_a = 1.95, 1.10
                    else:
                        base_h, base_a = 1.55, 1.15
                    
                    final_list.append({
                        "Orario": ora,
                        "Incontro": f"{h_name} - {a_name}",
                        "Media Gol Casa": base_h,
                        "Media Gol Ospite": base_a,
                        "Pronostico": "🔥 OVER 2.5" if (base_h + base_a) > 2.7 else "⚖️ MULTIGOL"
                    })
        return final_list
    except Exception as e:
        return []

if st.button("📊 MOSTRA TUTTI I MATCH DI DOMANI"):
    with st.spinner("Recupero palinsesto completo..."):
        risultati = get_complete_data()
        if risultati:
            st.success(f"Trovati {len(risultati)} match di Serie A!")
            st.table(pd.DataFrame(risultati))
        else:
            st.error("Nessun match trovato. Verifica i permessi dell'API.")
