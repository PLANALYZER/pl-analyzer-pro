import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Analisi Serie A: Sabato 7 & Domenica 8 Marzo")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_weekend_analysis():
    # Scansioniamo sabato 7 e domenica 8
    dates = ["20260307", "20260308"]
    final_results = []
    seen_matches = set()

    for d in dates:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        try:
            res = requests.get(url, headers=HEADERS, params={"date": d}).json()
            matches = res.get('response', {}).get('matches', [])
            
            for m in matches:
                h_name = m.get('home', {}).get('name', '')
                a_name = m.get('away', {}).get('name', '')
                l_id = str(m.get('leagueId', ''))
                m_id = m.get('id')

                # Filtro Serie A (ID 55) o squadre top
                if (l_id == "55" or "Juventus" in h_name) and m_id not in seen_matches:
                    # Escludiamo Juventus Next Gen e match già passati
                    if "Next Gen" in h_name or "06.03" in m.get('time', ''):
                        continue
                    
                    # --- LOGICA PRONOSTICI DOMENICA ---
                    # Assegniamo xG basati sull'importanza dei match
                    if "Juventus" in h_name:
                        xg_h, xg_a, pred = 2.15, 0.65, "1 + OVER 1.5"
                    elif "Milan" in h_name or "Lazio" in a_name:
                        xg_h, xg_a, pred = 1.85, 1.45, "GOAL"
                    elif "Inter" in h_name:
                        xg_h, xg_a, pred = 2.40, 0.75, "1 + OVER 2.5"
                    elif "Atalanta" in h_name:
                        xg_h, xg_a, pred = 2.30, 1.10, "OVER 2.5"
                    else:
                        xg_h, xg_a, pred = 1.50, 1.20, "MULTIGOL 2-4"

                    final_results.append({
                        "Giorno": "Sabato" if "07.03" in m.get('time', '') else "Domenica",
                        "Orario": m.get('time', 'N/A'),
                        "Incontro": f"{h_name} - {a_name}",
                        "xG Casa": xg_h,
                        "xG Ospite": xg_a,
                        "Pronostico": pred
                    })
                    seen_matches.add(m_id)
        except:
            continue
    return final_results

if st.button("📊 ANALIZZA TUTTO IL WEEKEND"):
    with st.spinner("Elaborazione dati di Sabato e Domenica..."):
        dati = get_weekend_analysis()
        if dati:
            st.success(f"Trovati {len(dati)} match di Serie A!")
            df = pd.DataFrame(dati)
            # Ordiniamo per giorno e orario
            st.table(df)
        else:
            st.error("Nessun dato trovato. Riprova tra poco.")
