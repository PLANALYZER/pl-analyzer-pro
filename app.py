import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Serie A Analyzer", layout="wide")
st.title("🇮🇹 Focus Serie A: Weekend Analysis")

# Configurazione API
api_key = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
API_HOST = "free-api-live-football-data.p.rapidapi.com"
SERIE_A_ID = "55"

# Data del weekend (modificabile se necessario)
data_weekend = st.sidebar.text_input("Data Weekend (YYYYMMDD)", "20260307")

def scarica_serie_a():
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_weekend}&leagueid={SERIE_A_ID}"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('response', [])
    except:
        return []
    return []

def ottieni_stats(event_id):
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    url = f"https://{API_HOST}/football-get-head-to-head-by-event-id?eventid={event_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get('response', {}).get('summary', [])
    return None

# 1. Caricamento Partite
st.subheader(f"📅 Partite Serie A del {data_weekend}")
partite = scarica_serie_a()

if partite:
    for item in partite:
        for m in item.get('matches', []):
            with st.container():
                col1, col2, col3 = st.columns([2, 4, 2])
                
                casa = m.get('home', {}).get('name')
                ospiti = m.get('away', {}).get('name')
                ora = m.get('time')
                m_id = m.get('id')

                col1.write(f"🕒 **{ora}**")
                col2.write(f"🏟️ {casa} vs {ospiti}")
                
                # 2. Caricamento Statistiche al Click
                if col3.button(f"Analizza Stats", key=f"btn_{m_id}"):
                    stats = ottieni_stats(m_id)
                    if stats:
                        tot = sum(stats)
                        p1, px, p2 = (stats[0]/tot)*100, (stats[1]/tot)*100, (stats[2]/tot)*100
                        
                        st.info(f"📈 **Analisi Storica per {casa}-{ospiti}**")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Vittoria Casa", f"{p1:.1f}%")
                        c2.metric("Pareggio", f"{px:.1f}%")
                        c3.metric("Vittoria Ospiti", f"{p2:.1f}%")
                        
                        # Pronostico rapido
                        if p1 > 45: st.success("🎯 Suggerimento: 1X")
                        elif px > 40: st.warning("🎯 Suggerimento: X")
                        else: st.error("🎯 Suggerimento: X2")
                st.divider()
else:
    st.warning("Nessuna partita di Serie A trovata per questa data. Controlla se sono già state giocate o se l'API è in aggiornamento.")
