from . import charts

VALORE_CARTE = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

def normalizza_mano(input_string):
    """Converte l'input grezzo in formato canonico (es. 'a k s' -> 'AKs')."""
    if not input_string:
        return None

    clean = input_string.strip().upper().replace(" ", "")

    if len(clean) < 2 or len(clean) > 3:
        return None

    c1, c2 = clean[0], clean[1]

    if c1 not in VALORE_CARTE or c2 not in VALORE_CARTE:
        return None

    if c1 == c2:
        return c1 + c2

    # senza suffisso non sappiamo se è suited o offsuit
    if len(clean) == 2:
        return "AMBIGUO"

    suffisso_input = clean[2]
    if suffisso_input not in ['S', 'O']:
        return None

    suffisso_db = suffisso_input.lower()

    # la carta più alta va sempre per prima (AKs, non KAs)
    if VALORE_CARTE[c1] < VALORE_CARTE[c2]:
        return c2 + c1 + suffisso_db
    else:
        return c1 + c2 + suffisso_db

def calcola_azione(pos_key, raw_hand):
    """Interroga i range per decidere se aprire o foldare dalla posizione data."""
    mano_norm = normalizza_mano(raw_hand)

    if mano_norm is None:
        return {"titolo": "Formato non valido", "desc": "Usa es: AKs, 77, T9o", "bg": "#f0f0f0", "fg": "red"}

    if mano_norm == "AMBIGUO":
        return {"titolo": "Manca il seme", "desc": "Specifica 's' (suited) o 'o' (offsuit)", "bg": "#f0f0f0", "fg": "#FF9800"}

    if not hasattr(charts, 'OPEN_RANGES'):
        return {"titolo": "Errore DB", "desc": "charts.OPEN_RANGES mancante", "bg": "red", "fg": "white"}

    dati_range = charts.OPEN_RANGES.get(pos_key)
    if not dati_range:
        return {"titolo": "Errore Dati", "desc": f"Nessun dato per {pos_key}", "bg": "red", "fg": "white"}

    if mano_norm in dati_range["always"]:
        return {
            "titolo": f"OPEN RAISE [{mano_norm}]",
            "desc": "Mano forte. Apri sempre.",
            "bg": "#d4edda", "fg": "#155724"
        }

    elif mano_norm in dati_range["conditional"]:
        tip = dati_range.get("tip", "Gioca con cautela.")
        return {
            "titolo": f"CONDIZIONALE [{mano_norm}]",
            "desc": tip,
            "bg": "#fff3cd", "fg": "#856404"
        }

    else:
        return {
            "titolo": f"FOLD [{mano_norm}]",
            "desc": "Mano troppo debole.",
            "bg": "#f8d7da", "fg": "#721c24"
        }
