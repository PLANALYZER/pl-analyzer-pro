import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="PL Analyzer Pro - Global", layout="wide")
st.title("📈 PL Analyzer: England, Denmark, Portugal & More")

# --- DATABASE AGGIORNATO CON BACKUP ---
LEAGUES = {
    "Serie A 🇮🇹": "I1",
    "Serie B 🇮🇹": "I2",
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E0",
    "Championship 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E1",
    "League One 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E2",
    "League Two 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E3",
    "National League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "EC",
    "Olanda - Eredivisie 🇳🇱": "N1",
    "Olanda - Eerste Divisie 🇳🇱": "N2",
    "Portogallo - Liga I 🇵🇹": "P1",
    "Germania - Bundesliga 🇩🇪": "D1",
    "Germania - Bundesliga 2 🇩🇪": "D2",
    "Spagna - La Liga 🇪🇸": "SP1",
    "Spagna - Segunda 🇪🇸": "SP2",
    "Belgio - Pro League 🇧🇪": "B1",
    "Austria - Bundesliga 🇦🇹": "AUT",
    "Svizzera - Super League 🇨🇭": "SWZ",
    "Danimarca - Superliga 🇩🇰": "DAN",
    "Polonia - Ekstraklasa 🇵🇱": "POL"
}

scelta = st.sidebar.selectbox("Seleziona Campionato", list(LEAGUES.keys()))
code = LEAGUES[scelta]

@st.cache_data(ttl=3600)
def load_data(league_code):
    # Prova stagione attuale 25/26
    url = f"https://www.football-data.co.uk/mmz4281/2526/{league_code}.csv"
    try:
        df = pd.read_csv(url)
        if not df.empty and 'HomeTeam' in df.columns:
            return df.dropna(subset=['HomeTeam', 'AwayTeam'])
    except:
        # Backup: Prova stagione 24/25 se la nuova non esiste
        url_bkp = f"https://www.football-data.co.uk/mmz4281/2425/{league_code}.csv"
        try:
            df = pd.read_csv(url_bkp)
            return df.dropna(subset=['HomeTeam', 'AwayTeam'])
        except:
            return pd.DataFrame()

df = load_data(code)

if not df.empty:
    avg_h_league = df['FTHG'].mean()
    avg_a_league = df['FTAG'].mean()

    teams = sorted(df['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    h_team = col1.selectbox("Squadra Casa", teams)
    a_team = col2.selectbox("Squadra Ospite", teams)

    if h_team and a_team:
        # Analisi xG
        att_h = df[df['HomeTeam'] == h_team]['FTHG'].mean() / avg_h_league
        def_a = df[df['AwayTeam'] == a_team]['FTHG'].mean() / avg_h_league
        lambda_h = att_h * def_a * avg_h_league
        
        att_a = df[df['AwayTeam'] == a_team]['FTAG'].mean() / avg_a_league
        def_h = df[df['HomeTeam'] == h_team]['FTAG'].mean() / avg_a_league
        lambda_a = att_a * def_h * avg_a_league
        total_xg = lambda_h + lambda_a

        # Risultati Esatti
        def prob_score(l, k): return poisson.pmf(k, l)
        scores = []
        for h in range(4):
            for a in range(4):
                prob = prob_score(lambda_h, h) * prob_score(lambda_a, a)
                scores.append({'Risultato': f"{h}-{a}", 'Probabilità': prob})
        df_scores = pd.DataFrame(scores).sort_values(by='Probabilità', ascending=False).head(5)

        st.divider()
        res1, res2, res3 = st.columns(3)
        res1.metric(f"xG {h_team}", round(lambda_h, 2))
        res2.metric(f"xG {a_team}", round(lambda_a, 2))
        res3.metric("Goal Totali", round(total_xg, 2))

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.subheader("🎯 Pronostico")
            if total_xg > 3.0: st.success("🔥 OVER 2.5 / GOAL")
            elif total_xg > 2.2: st.info("✅ OVER 1.5")
            else: st.warning("⚠️ ANALISI UNDER")
            
        with col_p2:
            st.subheader("🔢 Risultati Probabili")
            st.table(df_scores.assign(Probabilità=lambda x: x['Probabilità'].map('{:.1%}'.format)))
else:
    st.error("Dati non disponibili per questo campionato su Football-Data.co.uk")
