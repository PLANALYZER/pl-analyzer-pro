def get_weekend_analysis():
    dates = ["20260307", "20260308"]
    final_results = []
    seen_matches = set()

    for d in dates:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        try:
            res = requests.get(url, headers=HEADERS, params={"date": d}).json()
            matches = res.get('response', {}).get('matches', [])
            
            for m in matches:
                h_name = m.get('home', {}).get('name', '')
                a_name = m.get('away', {}).get('name', '')
                l_id = str(m.get('leagueId', ''))
                m_id = m.get('id')

                if (l_id == "55" or "Juventus" in h_name) and m_id not in seen_matches:
                    if "Next Gen" in h_name or "06.03" in m.get('time', ''):
                        continue
                    
                    # --- LOGICA PERSONALIZZATA PER OGNI MATCH ---
                    # Sabato
                    if "Juventus" in h_name:
                        xg_h, xg_a, pred = 2.15, 0.65, "1 + OVER 1.5"
                    elif "Atalanta" in h_name:
                        xg_h, xg_a, pred = 2.30, 1.10, "OVER 2.5"
                    elif "Cagliari" in h_name:
                        xg_h, xg_a, pred = 1.45, 1.25, "MULTIGOL 2-4"
                    
                    # Domenica (Nuova Logica Differenziata)
                    elif "Lecce" in h_name:
                        xg_h, xg_a, pred = 1.25, 1.05, "UNDER 2.5"
                    elif "Bologna" in h_name:
                        xg_h, xg_a, pred = 1.75, 0.95, "1X + UNDER 3.5"
                    elif "Fiorentina" in h_name:
                        xg_h, xg_a, pred = 1.90, 1.20, "GOAL"
                    elif "Genoa" in h_name:
                        xg_h, xg_a, pred = 1.15, 1.80, "X2 + MULTIGOL 1-3"
                    elif "Inter" in h_name or "Inter" in a_name:
                        xg_h, xg_a, pred = 2.45, 0.85, "1 + OVER 2.5"
                    else:
                        xg_h, xg_a, pred = 1.40, 1.30, "MULTIGOL 1-4"

                    final_results.append({
                        "Giorno": "Sabato" if "07.03" in m.get('time', '') else "Domenica",
                        "Orario": m.get('time', 'N/A'),
                        "Incontro": f"{h_name} - {a_name}",
                        "xG Casa": xg_h,
                        "xG Ospite": xg_a,
                        "Pronostico": pred
                    })
                    seen_matches.add(m_id)
        except:
            continue
    return final_results
