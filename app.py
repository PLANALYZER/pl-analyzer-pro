import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="PL Analyzer Pro - Over & Asian", layout="wide")
st.title("📈 PL Analyzer: Top Scorer Leagues & Asian Odds")

# --- DATABASE CAMPIONATI "OVER" (Stagione 2025/2026) ---
LEAGUES = {
    "Olanda - Eredivisie 🇳🇱 (TOP GOL)": "https://www.football-data.co.uk/mmz4281/2526/N1.csv",
    "Belgio - Pro League 🇧🇪": "https://www.football-data.co.uk/mmz4281/2526/B1.csv",
    "Germania - Bundesliga 🇩🇪": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Inghilterra - League One 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/E2.csv",
    "Serie A 🇮🇹": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
}

scelta = st.sidebar.selectbox("Seleziona Campionato ad alto tasso di gol", list(LEAGUES.keys()))

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # AvgH, AvgD, AvgA = Quote 1X2 | Avg>2.5 = Media Quote Over
        return df.dropna(subset=['HomeTeam', 'AwayTeam'])
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
        # ANALISI TREND
        df_h = df[df['HomeTeam'] == h_team].tail(5)
        df_a = df[df['AwayTeam'] == a_team].tail(5)
        
        # CALCOLO xG (POISSON)
        att_h = df[df['HomeTeam'] == h_team]['FTHG'].mean() / avg_h_league
        def_a = df[df['AwayTeam'] == a_team]['FTHG'].mean() / avg_h_league
        lambda_h = att_h * def_a * avg_h_league
        
        att_a = df[df['AwayTeam'] == a_team]['FTAG'].mean() / avg_a_league
        def_h = df[df['HomeTeam'] == h_team]['FTAG'].mean() / avg_a_league
        lambda_a = att_a * def_h * avg_a_league
        total_xg = lambda_h + lambda_a

        # --- RISULTATI ESATTI (MATRICE DI POISSON) ---
        def prob_score(l, k): return poisson.pmf(k, l)
        
        scores = []
        for h in range(4):
            for a in range(4):
                prob = prob_score(lambda_h, h) * prob_score(lambda_a, a)
                scores.append({'Risultato': f"{h}-{a}", 'Probabilità': prob})
        
        df_scores = pd.DataFrame(scores).sort_values(by='Probabilità', ascending=False).head(5)

        # --- DASHBOARD ---
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric(f"xG {h_team}", round(lambda_h, 2))
        c2.metric(f"xG {a_team}", round(lambda_a, 2))
        c3.metric("xG Totali Match", round(total_xg, 2))

        # --- PRONOSTICO E ASIAN ODDS ---
        st.subheader("🎯 Pronostico & Analisi Mercato")
        
        # Analisi del drop della quota (Asian Style)
        last_odd = df[df['HomeTeam'] == h_team]['AvgH'].iloc[-1]
        mean_odd = df[df['HomeTeam'] == h_team]['AvgH'].mean()
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.write("#### Suggerimenti")
            if total_xg > 3.0: st.success("🔥 OVER 2.5 + GOAL")
            elif total_xg > 2.2: st.info("✅ OVER 1.5")
            else: st.warning("⚠️ UNDER 2.5")
            
            if last_odd < (mean_odd * 0.90):
                st.error("📉 ATTENZIONE: Forte calo quota Casa (Asian Drop!)")

        with col_p2:
            st.write("#### Risultati Esatti più probabili")
            st.table(df_scores.assign(Probabilità=lambda x: x['Probabilità'].map('{:.1%}'.format)))

else:
    st.info("Seleziona un campionato per caricare i dati.")
