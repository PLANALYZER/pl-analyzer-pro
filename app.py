import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Analizzatore Campionati", layout="wide")
st.title("📂 Palinsesto Campionati per Cartelle")

# Configurazione API
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"

# Tutti i tuoi 25 codici campionato ripristinati
MY_LEAGUES = {
    "Serie A": "55", "Premier League": "47", "Championship": "48", 
    "League One": "108", "League Two": "109", "National League": "117", 
    "Serie B": "86", "Serie C": "147", "Bundesliga": "54", 
    "2. Bundesliga": "146", "La Liga": "87", "Ligue 1": "53", 
    "Eredivisie": "57", "Eerste Divisie": "111", "Super League (SUI)": "69", 
    "Challenge League (SUI)": "163", "First Division (BEL)": "40", 
    "Liga Portugal": "61", "Eliteserien (NOR)": "59", "Superligaen (DEN)": "46", 
    "1. Division (DEN)": "85", "Serie A (BUL)": "270", "Bundesliga (AUT)": "38", 
    "Ekstraklasa (POL)": "196", "Super Lig (TUR)": "71"
}

data_scelta = st.sidebar.text_input("Data (YYYYMMDD)", "20260307")

# Funzione per analizzare il match (H2H)
def analizza_match(event_id):
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    url = f"https://{API_HOST}/football-get-head-to-head-by-event-id?eventid={event_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        h_data = res.json().get('response', {}).get('summary', [])
        if h_data and len(h_data) >= 3:
            tot = sum(h_data)
            p1, px, p2 = (h_data[0]/tot)*100, (h_data[1]/tot)*100, (h_data[2]/tot)*100
            st.write(f"📊 **H2H:** Casa {p1:.1f}% | Pareggio {px:.1f}% | Ospiti {p2:.1f}%")
            if p1 > 45: st.success("Consiglio: 1X")
            elif px > 40: st.info("Consiglio: X")
            else: st.warning("Consiglio: X2")
        else:
            st.write("Dati H2H non disponibili.")

# Creazione delle cartelle per ogni campionato
st.write("### Seleziona un campionato per vedere le partite:")

for name, lid in MY_LEAGUES.items():
    with st.expander(f"🏆 {name} (ID: {lid})"):
        if st.button(f"Carica {name}", key=f"btn_{lid}"):
            headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
            url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_scelta}&leagueid={lid}"
            
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                if "response" in data and data["response"]:
                    for item in data["response"]:
                        if "matches" in item:
                            for m in item["matches"]:
                                col1, col2, col3 = st.columns([1, 3, 1])
                                col1.write(f"🕒 {m.get('time')}")
                                col2.write(f"**{m.get('home', {}).get('name')} vs {m.get('away', {}).get('name')}**")
                                if col3.button("Analizza", key=f"an_{m.get('id')}"):
                                    analizza_match(m.get('id'))
                else:
                    st.info("Nessuna partita trovata per questa data.")
            else:
                st.error("Errore API.")
