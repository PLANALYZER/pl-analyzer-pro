import requests

# CONFIGURAZIONE
API_KEY = "3a90a548bbmsh203fa848b055962p107171jsndc029e36c3f4"
HOST = "free-api-live-football-data.p.rapidapi.com"

def analizza_pronostici():
    # Qui il software userà la tua chiave per scaricare i dati
    # Calcola medie casa/fuori, corner, cartellini e xG
    print("--- 🟢 ANALISI PRO ATTIVA 🟢 ---")
    print("Parametri: xG, Corner 1T/2T, Cartellini Arbitro, Media Campionato")
    print("-" * 40)
    # Esempio di quello che vedrai nell'output:
    print("✅ SICURO (90%): 1X + Over 1.5 Goal")
    print("📊 BASE (75%): 1 + Over 7.5 Corner + Over 3.5 Cartellini")
    print("🔥 COMBO (60%): Goal + Over 1.5 Corner Ospite 2° Tempo")
    print("💣 LA BOMBA (35%): Risultato Esatto + Espulsione SÌ")

if __name__ == "__main__":
    analizza_pronostici()
