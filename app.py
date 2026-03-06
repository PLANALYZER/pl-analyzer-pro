import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="PL Analyzer Pro - Full European Edition", layout="wide")
st.title("📈 PL Analyzer: England, Denmark, Portugal & More")

# --- DATABASE AGGIORNATO (Stagione 2025/2026) ---
LEAGUES = {
    "Inghilterra - Championship 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/E1.csv",
    "Inghilterra - League One 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/E2.csv",
    "Inghilterra - League Two 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/E3.csv",
    "Inghilterra - National League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/EC.csv",
    "Olanda - Eerste Divisie (B) 🇳🇱": "https://www.football-data.co.uk/mmz4281/2526/N2.csv",
    "Danimarca - Superliga (A) DK 🇩🇰": "https://www.football-data.co.uk/mmz4281/2526/DAN.csv",
    "Danimarca - 1st Division (B) DK 🇩🇰": "https://www.football-data.co.uk/mmz4281/2526/D1D.csv",
    "Portogallo - Liga I 🇵🇹": "https://www.football-data.co.uk/mmz4281/2526/P1.csv",
    "Bulgaria - Parva Liga 🇧🇬": "https://www.football-data.co.uk/mmz4281/2526/BUL.csv",
    "Austria - Bundesliga 🇦🇹": "https://www.football-data.co.uk/mmz4281/2526/AUT.csv",
    "Polonia - Ekstraklasa 🇵🇱": "https://www.football-data.co.uk/mmz4281/2526/POL.csv",
    "Svizzera - Super League 🇨🇭": "https://www.football-data.co.uk/mmz4281/2526/SWZ.csv",
    "Serie A 🇮🇹": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Serie B 🇮🇹": "https://www.football-data.co.uk/mmz4281/2526/I2.csv",
    "Olanda - Eredivisie (A) 🇳🇱": "https://www.football-data.co.uk/mmz4281/2526/N1.csv"
}

scelta = st.sidebar.selectbox("Seleziona Campionato", list(LEAGUES.keys()))

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam'])
        return df
    except:
        return pd.DataFrame()

df = load_data(LEAGUES[scelta])

if not df.empty:
    avg_h_league = df['FTHG'].mean()
    avg_a_league = df['FTAG'].mean()

    teams = sorted(df['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    h_team = col1.selectbox("Squadra Casa", teams)
    a_team = col2.selectbox("Squadra Ospite", teams)

    if h_team and a_team:
        # Calcolo Poisson xG
        att_h = df[df['HomeTeam'] == h_team]['FTHG'].mean() / avg_h_league
        def_a = df[df['AwayTeam'] == a_team]['FTHG'].mean() / avg_h_league
        lambda_h = att_h * def_a * avg_h_league
        
        att_a = df[df['AwayTeam'] == a_team]['FTAG'].mean() / avg_a_league
        def_h = df[df['HomeTeam'] == h_team]['FTAG'].mean() / avg_a_league
        lambda_a = att_a * def_h * avg_a_league
        total_xg = lambda_h + lambda_a

        # Risultati Probabili
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
        res3.metric("Goal Totali Previsti", round(total_xg, 2))

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.subheader("🎯 Pronostico")
            if total_xg > 3.0: st.success("🔥 OVER 2.5 / GOAL")
            elif total_xg > 2.2: st.info("✅ OVER 1.5")
            else: st.warning("⚠️ ANALISI UNDER")
            
            if 'AvgH' in df.columns:
                last_odd = df[df['HomeTeam'] == h_team]['AvgH'].iloc[-1]
                mean_odd = df[df['HomeTeam'] == h_team]['AvgH'].mean()
                if last_odd < (mean_odd * 0.92):
                    st.error("📉 ASIAN DROP: Quota casa in calo!")

        with col_p2:
            st.subheader("🔢 Risultati Esatti")
            st.table(df_scores.assign(Probabilità=lambda x: x['Probabilità'].map('{:.1%}'.format)))
else:
    st.error("Dati non disponibili. Prova un'altra lega.")
