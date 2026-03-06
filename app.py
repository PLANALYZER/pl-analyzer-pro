import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="PL Analyzer PRO", layout="wide")

# --- 2. CHIAVI API (Usa st.secrets per sicurezza su GitHub!) ---
ODDS_API_KEY = "c6a3eb71e7e203103715c6ee7dc932cd"
FOOTBALL_DATA_KEY = "1224218727ff4b98bea0cd9941196e99"

# --- 3. FORMULA ALGORITMO OVER/UNDER & xG TOTALI ---
def calcola_analisi_gol(h_xg_f, h_xg_s, a_xg_f, a_xg_s, p_home, p_away):
    # Medie Campionato stimati (es. 1.55 casa, 1.20 trasferta)
    # Questi rendono la formula sensibile al fattore campo
    MEDIA_C = 1.55
    MEDIA_T = 1.20

    # Normalizzazione per partita giocata (Played)
    ph = p_home if p_home > 0 else 1
    pa = p_away if p_away > 0 else 1

    # Calcolo Forza Attacco e Difesa relativa
    # (xG fatti / partite) / media_gol_campionato
    att_h = (h_xg_f / ph) / MEDIA_C
    def_h = (h_xg_s / ph) / MEDIA_T
    att_a = (a_xg_f / pa) / MEDIA_T
    def_a = (a_xg_s / pa) / MEDIA_C

    # Proiezione xG per la partita attuale
    exp_h = att_h * def_a * MEDIA_C
    exp_a = att_a * def_h * MEDIA_T
    xg_totali = exp_h + exp_a

    # Selezione Pronostici basata sulle soglie di probabilità
    pronostici = []
    if xg_totali > 1.75: pronostici.append("OVER 1.5")
    if xg_totali > 2.60: pronostici.append("OVER 2.5")
    if xg_totali > 3.55: pronostici.append("OVER 3.5")
    if exp_h > 0.90 and exp_a > 0.90: pronostici.append("GOAL")
    
    return round(xg_totali, 2), pronostici, round(exp_h, 2), round(exp_a, 2)

# --- 4. INTERFACCIA UTENTE ---
st.title("⚽ ANALYZER PRO - ALGORITMO COMPLETO
