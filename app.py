# Se mancano le Asian Odds, il software procede comunque con xG e Multigol
def check_params(match_data):
    # 1. Calcolo Probabilità Multigol (Base)
    # 2. Controllo Cartellini (Se l'arbitro non è nel database, usa media squadre)
    # 3. Se Asian Odds calano > 0.10 -> Segnala "VALUE BET"
    
    if match_data['league_id'] in [207, 208]:
        # Logica speciale per la Svizzera (più Over)
        target_market = "Over 2.5 + MG 1-3 Ospite"
    else:
        target_market = "Multigol 1-3 Casa + Over 1.5"
        
    return target_market
