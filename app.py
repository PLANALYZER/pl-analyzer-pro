if menu == "Fase 1: Liste":
    st.header("🏆 Selezione Campionati")
    
    if st.button("Aggiorna Lista Globale"):
        headers = {"X-Rapidapi-Key": api_key, "X-Rapidapi-Host": API_HOST}
        response = requests.get(f"{BASE_URL}get-all-leagues", headers=headers)
        if response.status_code == 200:
            st.session_state['all_leagues'] = response.json()["response"]["leagues"]
            st.success("Lista aggiornata!")

    if 'all_leagues' in st.session_state:
        df_all = pd.DataFrame(st.session_state['all_leagues'])
        
        # --- FILTRO DI RICERCA ---
        search = st.text_input("Cerca campionato (es. Italy, Premier, Champions...)", "")
        df_filtered = df_all[df_all['name'].str.contains(search, case=False) | 
                             df_filtered['localizedName'].str.contains(search, case=False)]
        
        st.write("Seleziona i campionati che vuoi monitorare:")
        selected_leagues = st.multiselect("Campionati attivi:", 
                                          options=df_filtered['name'].tolist(),
                                          default=[])
        
        # Salviamo gli ID dei campionati scelti per la Fase 2
        if selected_leagues:
            watchlist = df_all[df_all['name'].isin(selected_leagues)][['id', 'name']]
            st.session_state['watchlist'] = watchlist
            st.table(watchlist)
            st.success("Configurazione salvata! Ora puoi andare alla Fase 2.")
