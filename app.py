elif menu == "Fase 2: Calendario":
    st.header(f"📅 Partite di Oggi: 07/03/2026")
    
    if 'active_ids' not in st.session_state:
        st.warning("Torna alla Fase 1 e salva gli ID (es. 55)!")
    else:
        data_api = "20260307" 
        
        if st.button("Scarica Partite di Oggi"):
            headers = {
                "X-Rapidapi-Key": api_key,
                "X-Rapidapi-Host": API_HOST
            }
            
            with st.spinner("Interrogazione API..."):
                for league_id in st.session_state['active_ids']:
                    url = f"{BASE_URL}get-matches-by-date-and-league?date={data_api}&leagueid={league_id}"
                    response = requests.get(url, headers=headers)
                    
                    # --- QUESTA PARTE CI DIRÀ L'ERRORE ---
                    st.write(f"Risposta per Lega {league_id}: {response.status_code}")
                    data = response.json()
                    
                    if "response" in data and "matches" in data["response"]:
                        partite = data["response"]["matches"]
                        if len(partite) > 0:
                            df = pd.DataFrame(partite)
                            st.dataframe(df)
                        else:
                            st.warning(f"L'API dice che per la lega {league_id} non ci sono partite oggi.")
                            st.write("Dati grezzi ricevuti:", data) # Così vediamo cosa c'è dentro
                    else:
                        st.error("La struttura dei dati è diversa da quella prevista.")
                        st.json(data)
