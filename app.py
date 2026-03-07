import streamlit as st
import requests
import pandas as pd

st.title("⚽ PL Analyzer Pro")
st.write("Benvenuto! Configura la tua API nella barra laterale.")

menu = st.sidebar.radio("Menu", ["Fase 1: Liste", "Fase 2: Calendario", "Fase 3: Pronostici"])
api_key = st.sidebar.text_input("Inserisci API Key", type="password")
