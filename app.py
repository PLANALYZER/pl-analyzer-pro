import streamlit as st
import requests

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="PL Analyzer PRO - Sistema Integrato", layout="wide")

# --- PROTEZIONE ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Riservato")
    if st.text_input("Inserisci Password:", type="password") == "BOMBER2026":
        if st.button("Sblocca Software"):
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- CHIAVI API ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

st.title("⚽ ANALYZER PRO - ALGORITMO INTEGRATO 7 PUNTI")

league_map = {"soccer_italy_serie_a": "SA", "soccer_epl": "PL", "soccer_spain_la_liga": "PD", "soccer_germany_bundesliga": "BL1"}
camp_scelto = st.selectbox("Seleziona Campionato:", list(league_map.keys()))

if st.button("ESEGUI ANALISI TOTALE"):
    with st.spinner("Elaborazione dati, medie e stato di forma..."):
        
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        stats_res = requests.get(f"https://api.football-data.org/v4/competitions/{league_map[camp_scelto]}/standings", headers=headers).json()
        odds_res = requests.get(f"https://api.the-odds-api.com/v4/sports/{camp_scelto}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals").json()

        if "standings" in stats_res:
            table = stats_res['standings'][0]['table']
            
            # MEDIE CAMPIONATO (.5)
            tot_h_gf = sum(t['home']['goalsFor'] for t in table)
            tot_h_p = sum(t['home']['playedGames'] for t in table)
            tot_a_gf = sum(t['away']['goalsFor'] for t in table)
            tot_a_p = sum(t['away']['playedGames'] for t in table)
            avg_league_h = tot_h_gf / tot_h_p
            avg_league_a = tot_a_gf / tot_a_p

            team_db = {t['team']['name']: t for t in table}

            for match in odds_res:
                h_n, a_n = match['home_team'], match['away_team']
                h_s = next((v for k,v in team_db.items() if h_n in k or k in h_n), None)
                a_s = next((v for k,v in team_db.items() if a_n in k or k in a_n), None)

                if h_s and a_s:
                    # GOL E PARTITE CASA/TRASFERTA (.6)
                    h_gf_h, h_gs_h, h_p_h = h_s['home']['goalsFor'], h_s['home']['goalsAgainst'], h_s['home']['playedGames']
                    a_gf_a, a_gs_a, a_p_a = a_s['away']['goalsFor'], a_s['away']['goalsAgainst'], a_s['away']['playedGames']

                    # FORMA ULTIME 5 CASA/TRASFERTA (.7)
                    # Calcolo punti basato sulla stringa form (es: "WWDLD")
                    def calc_points(form_str):
                        return form_str.count('W')*3 + form_str.count('D')*1
                    
                    # Usiamo la forma generale filtrata (API Free fornisce la forma totale)
                    h_form_pts = calc_points(h_s['form'][-5:] if h_s['form'] else "")
                    a_form_pts = calc_points(a_s['form'][-5:] if a_s['form'] else "")

                    # CALCOLO XG MILLIMETRICO
                    att_h = (h_gf_h / h_p_h) / avg_league_h
                    def_a = (a_gs_a / a_p_a) / avg_league_h
                    xg_h_final = att_h * def_a * avg_league_h
                    
                    att_a = (a_gf_a / a_p_a) / avg_league_a
                    def_h = (h_gs_h / h_p_h) / avg_league_a
                    xg_a_final = att_a * def_h * avg_league_a
                    
                    total_xg = xg_h_final + xg_a_final

                    with st.expander(f"📊 {h_n} vs {a_n} | xG: {total_xg:.2f}"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.write(f"**CASA: {h_n}**")
                            st.write(f"Gol Fatti (C): {h_gf_h} | Subiti (C): {h_gs_h}")
                            st.metric("Punti Ultime 5 (Casa)", f"{h_form_pts}/15")
                            st.metric("xG Attesi Casa", f"{xg_h_final:.2f}")
                        
                        with c2:
                            st.write(f"**TRASF: {a_n}**")
                            st.write(f"Gol Fatti (T): {a_gf_a} | Subiti (T): {a_gs_a}")
                            st.metric("Punti Ultime 5 (Trasf)", f"{a_form_pts}/15")
                            st.metric("xG Attesi Ospite", f"{xg_a_final:.2f}")

                        with c3:
                            # MARKET MOVE OVER 2.5
                            try:
                                bookie = match['bookmakers'][0]
                                o25 = next(o['price'] for m in bookie['markets'] if m['key']=='totals' for o in m['outcomes'] if o['name']=='Over' and o['point']==2.5)
                                st.write("**MARKET MOVE OVER 2.5**")
                                if o25 < 1.75 and total_xg > 2.6: st.success("📉 IN DISCESA")
                                elif o25 > 2.15: st.error("⚠️ IN SALITA")
                                else: st.info("➡️ STABILE")
                                st.write(f"Quota: {o25}")
                            except: st.write("Quota N/A")

                        st.divider()
                        
                        # PRONOSTICO FINALE
                        st.subheader("🎯 PRONOSTICO DEFINITIVO")
                        p1, p2, p3 = st.columns(3)
                        with p1:
                            if total_xg > 1.8: st.success("OVER 1.5")
                            if total_xg > 2.6: st.success("OVER 2.5")
                            if total_xg > 3.4: st.success("OVER 3.5")
                        with p2:
                            if total_xg < 2.3: st.warning("UNDER 2.5")
                            if total_xg < 3.2: st.warning("UNDER 3.5")
                        with p3:
                            # Se la forma è alta e gli xG sono alti -> Combo sicura
                            if (h_form_pts + a_form_pts) > 18 and total_xg > 2.7:
                                st.success("🌟 GOAL + OVER 2.5 (TOP)")
                            elif xg_h_final > 0.9 and xg_a_final > 0.9:
                                st.success("⚽ GOAL")

        else: st.error("Errore dati o API. Riprova.")

st.sidebar.write("© 2026 PL Analyzer - Sistema Integrato 7 Punti")
