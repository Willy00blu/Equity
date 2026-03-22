def analyze_stats(vpip, pfr, bet3, hands):
    """
    Profila un avversario in base alle sue statistiche HUD.
    Basato su logiche di cash game 6-max.
    """

    # sotto le 50 mani i dati non dicono nulla, specie la 3-bet
    reliability = "LOW"
    rel_msg = "DATA UNRELIABLE (<50 hands). Gioca standard ABC."

    if hands >= 50 and hands < 200:
        reliability = "MEDIUM"
        rel_msg = "SAMPLE BASSO (<200). Tendenze indicative, specie sulla 3-Bet."
    elif hands >= 200 and hands < 1000:
        reliability = "HIGH"
        rel_msg = "SAMPLE SOLIDO. Puoi fidarti delle statistiche."
    elif hands >= 1000:
        reliability = "VERY_HIGH"
        rel_msg = "DATABASE COMPLETO. Le statistiche sono legge."

    # gap alto = chiama tanto invece di rilanciare (dead money)
    gap = vpip - pfr
    # aggro_ratio vicino a 1 = rilancia quasi tutto quello che gioca
    aggro_ratio = pfr / vpip if vpip > 0 else 0

    profile = {}

    # VPIP < 19: giocatore stretto, aspetta solo le mani top
    if vpip < 19:
        if gap < 6:
            profile = {
                "name": "NIT / ROCK",
                "color": "#8D6E63",
                "desc": f"Gioca solo il top del range (VPIP:{vpip:.0f}). Se mette chips, sei battuto.",
                "strategy": [
                    "RUBI BUI: Attacca i suoi bui con qualsiasi due carte.",
                    "POST-FLOP: Se mostra forza (Raise/Check-Raise), folda Top Pair/Overpair.",
                    "IMPLIED ODDS: Chiama i suoi raise con coppie basse (Set Mining). Se chiudi il set, ti darà tutto lo stack.",
                    "BLUFF: C-betta se fa check. Molla se chiama."
                ]
            }
        else:
            # stretto ma non aggressivo: folda a qualsiasi pressione
            profile = {
                "name": "WEAK TIGHT",
                "color": "#BCAAA4",
                "desc": "Gioca poche mani e con paura. Facile da bullizzare post-flop.",
                "strategy": [
                    "AGGRESSIONE PURA: Punta su ogni street 'scary'. Ha paura di perdere.",
                    "NO HERO CALL: Se punta al River, ha il Nuts assoluto."
                ]
            }

    # 19-27 VPIP: range ottimale per il 6-max, i veri regolari
    elif 19 <= vpip <= 27:
        if bet3 < 4.5:
            # 3-bet rarissima = solo valore puro, semplice da giocare contro
            profile = {
                "name": "TAG (Value Oriented)",
                "color": "#43A047",
                "desc": "Regolare solido ma onesto. La sua 3-bet è solo valore (QQ+, AK).",
                "strategy": [
                    "3-BET DEFENSE: Folda AQ/JJ contro la sua 3-bet.",
                    "RESPECT: Non cercare bluff complessi contro di lui.",
                    "TARGET: Cerca di portarlo fuori posizione."
                ]
            }
        elif bet3 > 9:
            # 3-bet alta = range bilanciato, il profilo più difficile da affrontare
            profile = {
                "name": "TAG (Aggressive/Balanced)",
                "color": "#66BB6A",
                "desc": "Il profilo più difficile. Ha range bilanciati di bluff e valore.",
                "strategy": [
                    "4-BET BLUFF: Inserisci A5s/A4s nel range di 4-bet bluff.",
                    "TRAP: Fai slowplay con mani monster, aggredirà lui per te.",
                    "VARIANZA: Preparati a swingare, non ti regalerà nulla."
                ]
            }
        else:
            profile = {
                "name": "TAG (Standard Reg)",
                "color": "#4CAF50",
                "desc": "Giocatore ABC competente. Fa pochi errori gravi.",
                "strategy": [
                    "A-GAME: Gioca solido. Evita spot marginali.",
                    "TABLE SELECT: Se puoi, cambia tavolo o siediti alla sua sinistra."
                ]
            }

    # 28-38 VPIP: zona grigia, dipende da quanto è aggressivo
    elif 28 <= vpip <= 38:
        if pfr > 22 and bet3 > 8:
            profile = {
                "name": "LAG (Loose Aggressive)",
                "color": "#FF9800",
                "desc": "Gioca troppe mani ma le gioca bene post-flop. Ti mette pressione.",
                "strategy": [
                    "LIGHT CALL: Chiama con 2nd pair / Top pair debole per indurre bluff.",
                    "NO FOLD: Non foldare facilmente alle C-bet.",
                    "4-BET: Punisci la sua 3-bet larga con 4-bet for value (TT+, AQ+)."
                ]
            }
        elif gap > 10:
            # loose ma passivo: entra in troppe mani e le chiama invece di rilanciare
            profile = {
                "name": "BAD REG / SLIGHTLY LOOSE",
                "color": "#FFEB3B",
                "desc": "Gioca troppe mani e spesso chiama invece di rilanciare.",
                "strategy": [
                    "ISOLATION: Rilancia sui suoi limp per giocare heads-up in posizione.",
                    "VALUE: Estrai valore anche con mani medie."
                ]
            }
        else:
            profile = {
                "name": "HYBRID / LOOSE-TAG",
                "color": "#FFC107",
                "desc": "Al limite tra TAG e LAG. Un po' troppo loose preflop.",
                "strategy": ["Gioca tight preflop e aggressivo post-flop."]
            }

    # VPIP > 38: il fish territory
    elif vpip > 38:
        if pfr > 25 and bet3 > 15:
            profile = {
                "name": "MANIAC / SPEWER",
                "color": "#D50000",
                "desc": "Rilancia con spazzatura. Il bancomat del tavolo se hai pazienza.",
                "strategy": [
                    "PATIENCE: Folda finché non hai una mano decente (88+, ATs+, KJ+).",
                    "TRAP: Mai rilanciare se non per valore. Lascialo puntare.",
                    "CALL DOWN: Chiama con Top Pair fino al river. Non foldare.",
                    "NOTE: Aspettati alta varianza."
                ]
            }
        elif aggro_ratio < 0.5:
            # entra in tutto ma non rilancia mai: la fonte di profitto più facile
            profile = {
                "name": "WHALE / STATION",
                "color": "#2962FF",
                "desc": f"Il target ideale. VPIP alto ({vpip:.0f}) e passivo. Non folda mai.",
                "strategy": [
                    "ZERO BLUFF: Cancella la parola bluff dal vocabolario.",
                    "MAX VALUE: Punta POT o OVERBET con Top Pair o meglio.",
                    "FOLD AL RIVER: Se lui improvvisamente punta forte al river, HA IL NUTS.",
                    "ISOLATE: Rilancia largo preflop per isolarlo."
                ]
            }
        else:
            profile = {
                "name": "LOOSE PASSIVE",
                "color": "#03A9F4",
                "desc": "Gioca troppe mani e male post-flop.",
                "strategy": ["Gioca semplice. Value bet, no bluff."]
            }

    if not profile:
        profile = {
            "name": "UNKNOWN",
            "color": "gray",
            "desc": "Statistiche non classificabili.",
            "strategy": ["Raccogli più mani."]
        }

    profile["reliability"] = rel_msg
    return profile
