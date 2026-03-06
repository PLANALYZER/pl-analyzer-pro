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

def get_clean_weekend():
    dates = ["20260307", "20260308"]
    all_data = []
    seen = set()

    for d in dates:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        try:
            res = requests.get(url, headers=HEADERS, params={"date": d}).json()
            matches = res.get('response', {}).get('matches', [])
            
            for m in matches:
                h = m.get('home', {}).get('name', '')
                a = m.get('away', {}).get('name', '')
                l_id = str(m.get('leagueId', ''))
                m_id = m.get('id')

                # Filtro Serie A e pulizia duplicati
                if (l_id == "55" or "Juventus" in h) and m_id not in seen:
                    if "Next Gen" in h or "06.03" in m.get('time', ''):
                        continue
                    
                    # LOGICA XG E PRONOSTICI DIFFERENZIATI
                    # Sabato 7 Marzo
                    if "Juventus" in h:
                        xh, xa, pr = 2.15, 0.65, "1 + OVER 1.5"
                    elif "Atalanta" in h:
                        xh, xa, pr = 2.30, 1.10, "OVER 2.5"
                    elif "Cagliari" in h:
                        xh, xa, pr = 1.45, 1.25, "MULTIGOL 2-4"
                    
                    # Domenica 8 Marzo
                    elif "Lecce" in h:
                        xh, xa, pr = 1.25, 1.05, "UNDER 2.5"
                    elif "Bologna" in h:
                        xh, xa, pr = 1.75, 0.95, "1X + UNDER 3.5"
                    elif "Fiorentina" in h:
                        xh, xa, pr = 1.90, 1.20, "GOAL"
                    elif "Genoa" in h:
                        xh, xa, pr = 1
