import streamlit as st
import requests
import pandas as pd

# CONFIGURAZIONE PAGINA
st.set_page_config(page_title="PL ANALYZER PRO", layout="wide")
st.title("🇮🇹 Serie A PRO - Analisi 7 Marzo 2026")

# --- CHIAVE API (Sostituisci se l'hai rigenerata) ---
# Assicurati che non ci siano spazi prima o dopo le virgolette
MY_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"

HEADERS = {
    'x-rapidapi-key': MY_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def get_data():
    # Endpoint specifico per Serie A (135), Stagione 2025, Data 7 Marzo
    url = "https://v3.football.api-sports.io/fixtures?league=135&season=2025&date=2026-03-07&timezone=Europe/Rome"
    
    try:
        # Usiamo timeout per evitare che Streamlit si blocchi se il server è lento
        response = requests.get(url, headers=HEADERS, timeout=10).json()
        return response
    except Exception as e:
        return {"errors": {"exception": str(e)}}

if st.button("🔍 ANALIZZA MATCH DI DOMANI"):
    with st.spinner("Connessione ai server API-Sports..."):
        full_res = get_data()
        
        # Controllo errori immediato
        if full_res.get('errors'):
            st.error("⚠️ L'API HA RIFIUTATO LA CHIAVE O C'È UN ERRORE")
            st.json(full_res['errors']) # Ti mostra l'errore esatto
        
        elif not full_res.get('response'):
            st.warning("Nessun match trovato per i parametri impostati.")
            st.write("Risposta Raw:", full_res)
            
        else:
            matches = full_res['response']
            st.success(f"Trovati {len(matches)} match in Serie A!")
            
            final_data = []
            for m in matches:
                h_id = m['teams']['home']['id']
                a_id = m['teams']['away']['id']
                h_name = m['teams']['home']['name']
                a_name = m['teams']['away']['name']

                # Recupero statistiche dettagliate per ogni team
                h_url = f"https://v3.football.api-sports.io/teams/statistics?league=135&season=2025&team={h_id}"
                a_url = f"https://v3.football.api-sports.io/teams/statistics?league=135&season=2025&team={a_id}"
                
                h_s = requests.get(h_url, headers=HEADERS).json().get('response', {})
                a_s = requests.get(a_url, headers=HEADERS).json().get('response', {})

                if h_s and a_s:
                    # Estrazione Medie Gol (Fatti in Casa per H, Fatti Fuori per A)
                    avg_h = h_s['goals']['for']['average']['home']
                    avg_a = a_s['goals']['for']['average']['away']
                    
                    # Forma Ultime 5
                    forma_h = h_s['form'][-5:] if h_s.get('form') else "N/A"
                    forma_a = a_s['form'][-5:] if a_s.get('form') else "N/A"
                    
                    # Partite Giocate
                    p_h = h_s['fixtures']['played']['home']
                    p_a = a_s['fixtures']['played']['away']

                    final_data.append({
                        "Match": f"{h_name} - {a_name}",
                        "Gare (H-Casa/A-Fuori)": f"{p_h} / {p_a}",
                        "Media Gol H (Casa)": avg_h,
                        "Media Gol A (Fuori)": avg_a,
                        "Forma H": forma_h,
                        "Forma A": forma_a,
                        "Consiglio": "🔥 OVER" if (float(avg_h or 0) + float(avg_a or 0)) > 2.5 else "⚖️ MULTIGOL"
                    })

            if final_data:
                st.table(pd.DataFrame(final_data))
