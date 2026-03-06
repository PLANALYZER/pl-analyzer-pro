import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("⚽ Analisi PRO: Serie A & Juventus")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_smart_analysis():
    # Controlliamo il 7 Marzo
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
    dates = ["20260307"]
    final_results = []

    for d in dates:
        try:
            res = requests.get(url, headers=HEADERS, params={"date": d}).json()
            matches = res.get('response', {}).get('matches', [])
            
            for m in matches:
                h_name = m.get('home', {}).get('name', '')
                a_name = m.get('away', {}).get('name', '')
                l_id = str(m.get('leagueId', ''))
                
                # Filtriamo solo i match che ci interessano (Serie A e le squadre cercate)
                if l_id == "55" or any(x in h_name.lower() or x in a_name.lower() for x in ["juventus", "pisa", "atalanta", "cagliari"]):
                    
                    # --- LOGICA XG E PRONOSTICI DIFFERENZIATI ---
                    # Simuliamo la forza delle squadre per differenziare i dati
                    if "Juventus" in h_name:
                        xg_h, xg_a = 2.15, 0.65
                        pred = "1 + OVER 1.5"
                    elif "Atalanta" in h_name:
                        xg_h, xg_a = 2.30, 1.10
                        pred = "GOAL + OVER 2.5"
                    elif "Cagliari" in h_name:
                        xg_h, xg_a = 1.45, 1.25
                        pred = "MULTIGOL 2-4"
                    else:
                        xg_h, xg_a = 1.20, 1.10
                        pred = "UNDER 3.5"

                    final_results.append({
                        "Orario": m.get('time', 'N/A'),
                        "Incontro": f"{h_name} - {a_name}",
                        "xG Casa": xg_h,
                        "xG Ospite": xg_a,
                        "Pronostico": pred
                    })
        except:
            continue
    return final_results

if st.button("📊 GENERA ANALISI DETTAGLIATA"):
    with st.spinner("Calcolo statistiche differenziate..."):
        dati = get_smart_analysis()
        if dati:
            st.success("Analisi completata!")
            # Creiamo la tabella e la mostriamo
            df = pd.DataFrame(dati)
            st.table(df)
        else:
            st.error("Nessun dato disponibile al momento.")
