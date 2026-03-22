import ctypes
import os
from .range_parser import card_to_int

base_path = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(base_path, "poker.dylib")

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Libreria poker.dylib non trovata in: {lib_path}")

poker_lib = ctypes.CDLL(lib_path)

# firma della funzione C: 5 argomenti in input, 4 puntatori di output
# hero[2], villain[2], board[n], board_count, sims -> wins, ties, total, stats[9]
poker_lib.run_montecarlo_sim.argtypes = [
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
]
poker_lib.run_montecarlo_sim.restype = None

def _validate_two_cards(ints):
    return (len(ints) == 2 and ints[0] != ints[1] and ints[0] >= 0 and ints[1] >= 0)

def run_simulation(hero_str, board_str, sims, villain_ints_pair=None):
    try:
        hero_ints = [card_to_int(c) for c in hero_str.split()]
    except Exception:
        return {"error": "Hero card parsing failed"}

    if not _validate_two_cards(hero_ints):
        return {"error": "Hero hand invalid"}

    try:
        board_ints = [card_to_int(c) for c in board_str.split()] if board_str else []
        board_ints = [x for x in board_ints if x >= 0]
    except Exception:
        return {"error": "Board card parsing failed"}

    if not _validate_two_cards(villain_ints_pair or []):
        return {"error": "Villain hand invalid"}

    # controllo duplicati tra tutte le carte note prima di passare al C
    all_cards = hero_ints + (villain_ints_pair or []) + board_ints
    if len(all_cards) != len(set(all_cards)):
        return {"error": "Duplicate cards detected"}

    TypeArray2 = ctypes.c_int * 2
    c_hero = TypeArray2(*hero_ints)
    c_villain = TypeArray2(*villain_ints_pair)

    # il board può essere vuoto (preflop): in quel caso passiamo un puntatore null
    if len(board_ints) > 0:
        TypeArrayN = ctypes.c_int * len(board_ints)
        c_board_array = TypeArrayN(*board_ints)
        c_board_ptr = ctypes.cast(c_board_array, ctypes.POINTER(ctypes.c_int))
    else:
        c_board_ptr = ctypes.POINTER(ctypes.c_int)()

    c_wins = ctypes.c_int(0)
    c_ties = ctypes.c_int(0)
    c_total = ctypes.c_int(0)
    c_stats = (ctypes.c_int * 9)()  # un contatore per ciascuno dei 9 tipi di mano

    poker_lib.run_montecarlo_sim(
        c_hero,
        c_villain,
        c_board_ptr,
        ctypes.c_int(len(board_ints)),
        ctypes.c_int(sims),
        ctypes.byref(c_wins),
        ctypes.byref(c_ties),
        ctypes.byref(c_total),
        c_stats
    )

    wins = c_wins.value
    ties = c_ties.value
    total_sims = c_total.value

    if total_sims == 0:
        return {"error": "0 sims executed"}

    losses = total_sims - wins - ties

    hand_types = ["High Card", "Pair", "Two Pair", "Three of a Kind",
                  "Straight", "Flush", "Full House", "Quads", "Straight Flush"]
    stats_dict = {}
    for i in range(9):
        pct = (c_stats[i] / float(total_sims)) * 100
        stats_dict[hand_types[i]] = round(pct, 2)

    # equity = wins + metà dei tie (split pot vale metà)
    return {
        "equity": round((wins + ties / 2) / total_sims * 100, 2),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "win_rate": round((wins / total_sims) * 100, 2),
        "tie_rate": round((ties / total_sims) * 100, 2),
        "loss_rate": round((losses / total_sims) * 100, 2),
        "sims": total_sims,
        "hand_stats": stats_dict
    }
