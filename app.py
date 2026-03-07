if st.button("🔄 Scarica Tutto il Palinsesto"):
    all_matches = []
    headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
    
    # Creiamo una lista dei campionati per monitorare i fallimenti
    failed_leagues = []
    progress_bar = st.progress(0)
    
    for name, lid in MY_LEAGUES.items():
        url = f"https://{API_HOST}/football-get-matches-by-date-and-league?date={data_scelta}&leagueid={lid}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Debug specifico per Serie A
                if lid == "55":
                    st.sidebar.write(f"DEBUG Serie A: {len(data.get('response', []))} blocchi trovati")
                
                if "response" in data and data["response"]:
                    for item in data["response"]:
                        for m in item.get("matches", []):
                            all_matches.append({
                                "Campionato": name,
                                "Ora": m.get("time", "N/D"),
                                "Casa": m.get("home", {}).get("name", "N/D"),
                                "Ospiti": m.get("away", {}).get("name", "N/D"),
                                "ID Partita": m.get("id", "N/D")
                            })
                else:
                    if lid == "55": failed_leagues.append(name)
        except:
            failed_leagues.append(name)
            
    if all_matches:
        df = pd.DataFrame(all_matches)
        st.dataframe(df, use_container_width=True)
        st.session_state['matches_data'] = all_matches
        if failed_leagues:
            st.warning(f"⚠️ Non ho trovato dati per: {', '.join(failed_leagues)}. Riprova tra un minuto.")
