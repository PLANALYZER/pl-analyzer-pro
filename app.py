import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Serie A PRO: Weekend 7-8 Marzo")

MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HEADERS = {
    "x-rapidapi-key": MY_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

def get_weekend_data():
    dates = ["20260307", "20260308"]
    final_list = []
    seen_ids = set()

    for d in dates:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        try:
            response = requests.get(url, headers=HEADERS, params={"date": d})
            data = response.json()
            matches = data.get('response', {}).get('matches', [])
            
            for m in matches:
                h = m.get('home', {}).get('name', '')
                a = m.get('away', {}).get('name', '')
                l_id = str(m.get('leagueId', ''))
                m_id = m.get('id')

                # Filtriamo per Serie A (ID 55) o match specifici come la Juve
                if (l_id == "55" or "Juventus" in h) and m_id not in seen_ids:
                    # Pulizia squadre minori/Next Gen
                    if "Next Gen" in h or "06.03" in m.get('time', ''):
                        continue

                    # --- ASSEGNAZIONE DATI SPECIFICI ---
                    # Default
                    xh, xa, pr = 1.40, 1.20, "MULTIGOL 2-4"

                    # Sabato
                    if "Juventus" in h:
                        xh, xa, pr = 2.15, 0.65, "1 + OVER 1.5"
                    elif "Atalanta" in h:
                        xh, xa, pr = 2.30, 1.10, "OVER 2.5"
                    elif "Cagliari" in h:
                        xh, xa, pr = 1.55, 1.15, "1X + MULTIGOL"
                    
                    # Domenica
                    elif "Lecce" in h:
                        xh, xa, pr = 1.20, 1.10, "UNDER 2.5"
                    elif "Bologna" in h:
                        xh, xa, pr = 1.80, 0.90, "1 (DNB)"
                    elif "Fiorentina" in h:
                        xh, xa, pr = 1.95, 1.25, "GOAL"
                    elif "Genoa" in h:
                        xh, xa, pr = 1.10, 1.75, "X2"
                    elif "Inter" in h or "Inter" in a:
                        xh, xa, pr = 2.50, 0.80, "1 + OVER 2.5"
                    elif "Milan" in h or "Lazio" in h or "Milan" in a or "Lazio" in a:
                        xh, xa, pr = 1.85, 1.50, "GOAL + OVER 2.5"

                    final_list.append({
                        "Giorno": "Sabato" if d == "20260307" else "Domenica",
                        "Orario": m.get('time', 'N/A'),
                        "Incontro": f"{h} - {a}",
                        "xG Casa": xh,
                        "xG Ospite": xa,
                        "Pronostico": pr
                    })
                    seen_ids.add(m_id)
        except Exception as e:
            continue
            
    return final_list

if st.button("📊 ANALIZZA WEEKEND COMPLETO"):
    with st.spinner("Scansione Serie A in corso..."):
        risultati = get_weekend_data()
        if risultati:
            st.success(f"Analisi completata per {len(risultati)} match!")
            st.table(pd.DataFrame(risultati))
        else:
            st.error("N
