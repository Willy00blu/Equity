def calcola_pot_odds(pot, bet, outs, is_allin=False):
    """
    Calcola pot odds e equity approssimata tramite la regola degli outs.
    is_allin: se True usa il moltiplicatore x4 (2 carte a venire), altrimenti x2.
    """
    try:
        if not pot or not bet or not outs:
            return {"status": "ERROR", "msg": "Inserisci tutti i dati."}

        # accetto sia virgola che punto decimale (tastiere IT)
        pot = float(str(pot).replace(",", "."))
        bet = float(str(bet).replace(",", "."))
        outs = int(str(outs).replace(",", "."))
    except ValueError:
        return {"status": "ERROR", "msg": "Inserisci solo numeri validi."}

    # quanto devo mettere rispetto al piatto totale che si formerà
    piatto_finale = pot + bet + bet
    required_equity = (bet / piatto_finale) * 100

    # al flop all-in vedo turn+river quindi x4, altrimenti una carta sola x2
    if is_allin:
        factor = 4
        modalita = "All-In (2 carte)"
    else:
        factor = 2
        modalita = "Standard (1 carta)"

    actual_equity = min(outs * factor, 99)

    diff = actual_equity - required_equity

    req_str = f"{required_equity:.1f}%"
    act_str = f"{actual_equity}%"

    if diff >= 0:
        decisione = "CALL"
        colore_bg = "#d4edda"
        consiglio = f"Modalita: {modalita}\nHai il {act_str}. Serve il {req_str}.\nSEI IN VANTAGGIO."
    elif diff > -5:
        # margine troppo stretto per un fold secco, ma serve un motivo extra (implied odds)
        decisione = "MARGINALE"
        colore_bg = "#fff3cd"
        consiglio = f"Modalita: {modalita}\nHai il {act_str}. Serve il {req_str}.\nChiama solo per Implied Odds."
    else:
        decisione = "FOLD"
        colore_bg = "#f8d7da"
        consiglio = f"Modalita: {modalita}\nHai solo il {act_str}. Serve il {req_str}.\nMATEMATICAMENTE PERDENTE."

    return {
        "status": "OK",
        "decision": decisione,
        "msg": consiglio,
        "bg": colore_bg
    }
