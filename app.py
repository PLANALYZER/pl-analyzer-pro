# --- 4. LOGICA ALGORITMO OVER/UNDER & xG TOTALI ---
        def calcola_pronostico_over_under(home_stats, away_stats, played_home, played_away):
            # Media Campionato (esempio Serie A)
            league_avg_home = 1.50
            league_avg_away = 1.25

            # 1. Calcolo Forza Attacco/Difesa basato sulle partite giocate (Played)
            # xG_fatti / partite_giocate
            att_h = (home_stats['xg_for'] / played_home) / league_avg_home
            def_h = (home_stats['xg_against'] / played_home) / league_avg_away
            
            att_a = (away_stats['xg_for'] / played_away) / league_avg_away
            def_a = (away_stats['xg_against'] / played_away) / league_avg_home

            # 2. xG Attesi per questa specifica partita
            exp_home = att_h * def_a * league_avg_home
            exp_away = att_a * def_h * league_avg_away
            
            # 3. xG TOTALI DELLA PARTITA
            xg_totale_match = exp_home + exp_away

            # 4. LOGICA PRONOSTICI OVER
            pronostici = []
            if xg_totale_match > 1.6: pronostici.append("OVER 1.5")
            if xg_totale_match > 2.5: pronostici.append("OVER 2.5")
            if xg_totale_match > 3.4: pronostici.append("OVER 3.5")
            
            # Combo Goal + Over
            if exp_home > 0.8 and exp_away > 0.8 and xg_totale_match > 2.4:
                pronostici.append("GOAL + OVER 2.5")
            
            return round(xg_totale_match, 2), pronostici

        # --- Visualizzazione nell'App Streamlit ---
        # (Esempio con dati fittizi che dovrai mappare con le tue API)
        xg_tot, lista_pronostici = calcola_pronostico_over_under(
            {'xg_for': 25.4, 'xg_against': 12.1}, # Dati Casa accumulati
            {'xg_for': 18.2, 'xg_against': 22.5}, # Dati Ospite accumulati
            14, 13 # Partite giocate finora
        )

        st.markdown(f"### ⚽ Analisi Goal: **{xg_tot} xG Totali**")
        
        cols = st.columns(len(lista_pronostici) if lista_pronostici else 1)
        for i, p in enumerate(lista_pronostici):
            cols[i].success(f"🔥 {p}")
