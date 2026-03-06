import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
import io

st.set_page_config(page_title="PL Analyzer Pro - Ultra", layout="wide")
st.title("⚽ PL Analyzer Pro: Analisi Dati Multi-League")

# --- DATABASE MAPPATO CON CURA ---
LEAGUES = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E0",
    "Championship 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E1",
    "League One 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E2",
    "League Two 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "E3",
    "National League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "EC",
    "Serie A 🇮🇹": "I1",
    "Serie B 🇮🇹": "I2",
    "La Liga 🇪🇸": "SP1",
    "Segunda Division 🇪🇸": "SP2",
    "Bundesliga 🇩🇪": "D1",
    "Bundesliga 2 🇩🇪": "D2",
    "Eredivisie 🇳🇱": "N1",
    "Eerste Divisie 🇳🇱": "N2",
    "Portogallo Liga I 🇵🇹": "P1",
    "Belgio Pro League 🇧🇪": "B1",
    "Austria Bundesliga 🇦🇹": "AUT",
    "Svizzera Super League 🇨🇭": "SWZ",
    "Danimarca Superliga 🇩🇰": "DAN",
    "Polonia Ekstraklasa 🇵🇱": "POL",
    "Bulgaria Parva Liga 🇧🇬": "BUL"
}

scelta = st.sidebar.selectbox("Scegli Campionato", list(LEAGUES.keys()))
league_code = LEAGUES[scelta]

@st.cache_data(ttl=3600)
def load_data_final(code):
    # Prova 1: Stagione attuale 25/26 | Prova 2: Stagione precedente 24/25
    for season in ["2526", "2425"]:
        url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                if not df.empty and 'HomeTeam' in df.columns:
                    return df.dropna(subset=['HomeTeam', 'AwayTeam']), season
        except:
            continue
    return pd.DataFrame(), None

df, stagione_usata = load_data_final(league_code)

if not df.empty:
    st.success(f"Dati caricati! (Stagione: {stagione_usata})")
    
    # Pulizia colonne per evitare errori su campionati minori
    cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    df = df[cols].dropna()

    teams = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    h_team = c1.selectbox("Casa", teams)
    a_team = c2.selectbox("Trasferta", teams)

    if h_team and a_team:
        # Calcolo Medie
        avg_h = df['FTHG'].mean()
        avg_a = df['FTAG'].mean()

        def get_xg(team, is_home):
            sub = df[df['HomeTeam'] == team] if is_home else df[df['AwayTeam'] == team]
            return sub['FTHG'].mean() if is_home else sub['FTAG'].mean()

        l_h = (get_xg(h_team, True) / avg_h) * (get_xg(a_team, False) / avg_h) * avg_h
        l_a = (get_xg(a_team, False) / avg_a) * (get_xg(h_team, True) / avg_a) * avg_a

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric(f"xG {h_team}", round(l_h, 2))
        m2.metric(f"xG {a_team}", round(l_a, 2))
        m3.metric("Goal Totali", round(l_h + l_a, 2))

        # Pronostico
        st.subheader("🎯 Pronostico")
        total = l_h + l_a
        if total > 2.8: st.success("OVER 2.5")
        elif total > 2.1: st.info("OVER 1.5")
        else: st.warning("UNDER 2.5")

        # Risultati Esatti
        st.subheader("🔢 Probabilità Risultati")
        res = []
        for h in range(4):
            for a in range(4):
                p = poisson.pmf(h, l_h) * poisson.pmf(a, l_a)
                res.append({'Score': f"{h}-{a}", 'P': p})
        
        for r in pd.DataFrame(res).sort_values('P', ascending=False).head(3).to_dict('records'):
            st.write(f"**{r['Score']}** ({r['P']:.1%})")
else:
    st.error("⚠️ Il database non ha dati per questo campionato. Potrebbe essere in pausa o il file non è ancora pronto sul server.")
