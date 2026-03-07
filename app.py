import streamlit as st
import requests
import pandas as pd

# Impostazioni della Web App
st.set_page_config(page_title="PL Analyzer Pro", layout="wide")
st.title("⚽ PL Analyzer Pro - Dashboard Live")

# La tua Key estratta dai tuoi screenshot
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"

# Parametri che abbiamo testato con successo
target_date = "20260307"
serie_a_id = "55"

if st.button("🔄 Collega API e Scarica Partite"):
    headers = {
        "X-Rapidapi-Key": api_key,
        "X-Rapidapi-Host": API_HOST
    }
    
    # URL esatto dal tuo Playground
    url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={target_date}&leagueid={serie_a_id}"
    
    with st.spinner("Connessione in corso..."):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Navighiamo nella struttura che abbiamo visto nel tuo screen
                matches_extracted = []
                if "response" in data:
                    for item in data["response"]:
                        if "matches" in item:
                            for m in item["matches"]:
                                matches_extracted.append({
                                    "Ora": m.get("time", "N/D"),
                                    "Casa": m.get("home", {}).get("name", "N/D"),
                                    "Ospiti": m.get("away", {}).get("name", "N/D"),
                                    "ID": m.get("id", "N/D")
                                })
                
                if matches_extracted:
                    st.success(f"✅ Collegamento riuscito! Trovate {len(matches_extracted)} partite.")
                    st.table(pd.DataFrame(matches_extracted))
                else:
                    st.warning("⚠️ L'API è collegata ma non ci sono partite per questa data.")
                    st.write("Risposta completa per debug:", data)
            else:
                st.error(f"❌ Errore di connessione: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Errore imprevisto: {e}")

st.sidebar.info("Web App collegata all'API: " + API_HOST)
