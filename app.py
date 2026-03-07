import streamlit as st
import requests
import pandas as pd
import time  # Aggiunto per gestire le pause tra le chiamate API

st.set_page_config(page_title="PL Analyzer Pro - Live", layout="wide")
st.title("⚽ Dashboard Analisi Live")

# Configurazione API
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"

# Lista Campionati - Serie A spostata in prima posizione per priorità
MY_LEAGUES = {
    "Serie A": "55", 
    "Premier League": "47", "Championship": "48", "League One": "108", 
    "League Two": "109", "National League": "117", "Serie A": "55", "Serie B": "86", 
    "Serie C": "147", "Bundesliga": "54", "2. Bundesliga": "146", 
    "La Liga": "87", "Ligue 1": "53", "Eredivisie": "57", 
    "Eerste Divisie": "111", "Super League (SUI)": "69", 
    "Challenge League (SUI)": "163", "First Division (BEL)": "40", 
    "Liga Portugal": "61", "Eliteserien (NOR)": "59", 
    "Superligaen (DEN)": "46", "1. Division (DEN)": "85", 
    "Serie A (BUL)": "270", "Bundesliga (AUT)": "38", 
    "Ekstraklasa (POL)": "196", "Super Lig (TUR)": "71"
}

st.sidebar.header("Filtri")
data_scelta = st.sidebar.text_input("Data (YYYYMMDD)", "20260307")

if st.button("🔄 Scarica Palinsesto Completo"):
    all_matches = []
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    
    progress_bar = st.progress(0)
    count = 0
    
    for name, lid in MY_LEAGUES.items():
        count += 1
        # Forza una pausa di 0.5 secondi per non sovraccaricare l'API (Rate Limiting)
        time.sleep(0.5) 
        
        url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_scelta}&leagueid={lid}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "response" in data and data["response"]:
                    for item in data["response"]:
                        if "matches" in item:
                            for m in item["matches"]:
                                all_matches.append({
                                    "Campionato": name,
                                    "Ora": m.get("time", "N/D"),
                                    "Casa": m.get("home", {}).get("name", "N/D"),
                                    "Ospiti": m.get("away", {}).get("name", "N/D"),
                                    "ID Partita": m.get("id", "N/D")
                                })
        except:
            continue
        progress_bar.progress(count / len(MY_LEAGUES))

    if all_matches:
        df = pd.DataFrame(all_matches)
        st.session_state['matches_data'] = all_matches
        st.dataframe(df, use_container_width=True)
        st.success(f"Caricate {len(all_matches)} partite!")
    else:
        st.error("⚠️ Nessun match trovato. Se stai guardando la partita ora, l'API potrebbe averla già spostata nei 'Live Scores'.")

# --- SEZIONE ANALISI H2H ---
if 'matches_data' in st.session_state:
    st.divider()
    st.subheader("🕵️ Analizzatore Rapido H2H")
    opzioni = {f"{m['Campionato']} - {m['Casa']} vs {m['Ospiti']}": m['ID Partita'] for m in st.session_state['matches_data']}
    scelta = st.selectbox("Seleziona una partita per il pronostico:", options=list(opzioni.keys()))
    
    if st.button("🚀 Genera Pronostico Statistico"):
        id_ev = opzioni[scelta]
        url_h2h = f"https://{API_HOST}/football-get-head-to-head-by-event-id?eventid={id_ev}"
        h_res = requests.get(url_h2h, headers=headers)
        
        if h_res.status_code == 200:
            h_data = h_res.json().get('response', {}).get('summary', [])
            if h_data and len(h_data) >= 3:
                tot = sum(h_data)
                if tot > 0:
                    p1, px, p2 = (h_data[0]/tot)*100, (h_data[1]/tot)*100, (h_data[2]/tot)*100
                    st.write(f"**Probabilità storiche (H2H):** Casa {p1:.1f}% | Pareggio {px:.1f}% | Ospiti {p2:.1f}%")
                    if p1 > 45: st.success("🎯 Suggerimento: 1X")
                    elif px > 40: st.info("🎯 Suggerimento: X")
                    else: st.warning("🎯 Suggerimento: X2")
            else:
                st.warning("Dati H2H insufficienti per questa partita.")
