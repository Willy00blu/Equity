RANKS = "23456789TJQKA"
SUITS = "hdcs"

def card_to_int(card_str):
    """Converte una stringa carta (es. 'Ah') nel suo intero identificativo."""
    if len(card_str) < 2:
        return -1
    try:
        r = RANKS.index(card_str[0].upper())
        s = SUITS.index(card_str[1].lower())
        return (s * 13) + r
    except:
        return -1

def _is_valid_combo(combo, known_cards_set):
    """Scarta le combo che usano carte già in gioco (hero o board)."""
    if combo[0] in known_cards_set or combo[1] in known_cards_set:
        return False
    if combo[0] == combo[1]:
        return False
    return True

def _generate_pair_combos(rank_char):
    """Genera le 6 combinazioni possibili per una coppia."""
    try:
        r_val = RANKS.index(rank_char)
    except ValueError:
        return []
    combos = []
    for s1 in range(4):
        for s2 in range(s1 + 1, 4):
            combos.append([(s1 * 13) + r_val, (s2 * 13) + r_val])
    return combos

def _generate_suited_combos(rank_high, rank_low):
    """Genera le 4 combinazioni suited per una mano (es. AKs)."""
    try:
        r1 = RANKS.index(rank_high)
        r2 = RANKS.index(rank_low)
    except ValueError:
        return []
    combos = []
    for s in range(4):
        c1 = (s * 13) + r1
        c2 = (s * 13) + r2
        combos.append([c1, c2])
    return combos

def _generate_offsuit_combos(rank_high, rank_low):
    """Genera le 12 combinazioni offsuit per una mano (es. AKo)."""
    try:
        r1 = RANKS.index(rank_high)
        r2 = RANKS.index(rank_low)
    except ValueError:
        return []
    combos = []
    for s1 in range(4):
        for s2 in range(4):
            if s1 == s2:
                continue
            c1 = (s1 * 13) + r1
            c2 = (s2 * 13) + r2
            combos.append([c1, c2])
    return combos

def parse_range_breakdown(range_str, hero_str="", board_str=""):
    """
    Converte una stringa di range (es. 'QQ+, AKs, 77-99') in un dizionario
    label -> lista di combo [int, int], già filtrate dai blockers.
    """
    range_str = range_str.replace(" ", "").upper()
    parts = range_str.split(",")

    # costruiamo il set delle carte già note per filtrare i blockers
    known_cards_str = hero_str.split() + board_str.split()
    known_cards_int = [card_to_int(c) for c in known_cards_str]
    known_cards_int = [c for c in known_cards_int if c != -1]
    known_cards_set = set(known_cards_int)

    breakdown = {}

    for part in parts:
        if not part:
            continue

        # coppie: i due caratteri iniziali sono uguali (es. AA, 77+, 22-55)
        if part[0] in RANKS and part[1] in RANKS and part[0] == part[1]:
            base_rank = part[0]
            ranks_to_gen = []

            if '-' in part:
                try:
                    p = part.split('-')
                    idx1, idx2 = RANKS.index(p[0][0]), RANKS.index(p[1][0])
                    for i in range(min(idx1, idx2), max(idx1, idx2) + 1):
                        ranks_to_gen.append(RANKS[i])
                except:
                    pass
            elif '+' in part:
                idx = RANKS.index(base_rank)
                for i in range(idx, 13):
                    ranks_to_gen.append(RANKS[i])
            else:
                ranks_to_gen.append(base_rank)

            for r in ranks_to_gen:
                label = r + r
                combos = _generate_pair_combos(r)
                valid = [c for c in combos if _is_valid_combo(c, known_cards_set)]
                if valid:
                    breakdown[label] = valid
            continue

        # mani non-coppia: AKs, T9o, AJs+, ecc.
        is_plus = '+' in part
        clean_part = part.replace('+', '')

        if len(clean_part) < 2:
            continue

        r_char1, r_char2 = clean_part[0], clean_part[1]
        try:
            idx1 = RANKS.index(r_char1)
            idx2 = RANKS.index(r_char2)
        except ValueError:
            continue

        if idx1 > idx2:
            idx_high, idx_low = idx1, idx2
            char_high, char_low = r_char1, r_char2
        else:
            idx_high, idx_low = idx2, idx1
            char_high, char_low = r_char2, r_char1

        suffix = clean_part[2:] if len(clean_part) > 2 else ""
        want_suited = 'S' in suffix or len(clean_part) == 2
        want_offsuit = 'O' in suffix or len(clean_part) == 2

        if len(clean_part) == 2:
            want_suited = True
            want_offsuit = True

        low_limit = idx_low
        high_limit = idx_high - 1  # il + su non-coppie alza il kicker, non arriva alla coppia

        target_low_indices = []
        if is_plus:
            for i in range(low_limit, high_limit + 1):
                target_low_indices.append(i)
        else:
            target_low_indices.append(low_limit)

        for i_low in target_low_indices:
            c_low = RANKS[i_low]
            c_high = RANKS[idx_high]

            base_lbl = c_high + c_low

            if want_suited:
                lbl = base_lbl + "s"
                combos = _generate_suited_combos(c_high, c_low)
                valid = [c for c in combos if _is_valid_combo(c, known_cards_set)]
                if valid:
                    breakdown[lbl] = valid

            if want_offsuit:
                lbl = base_lbl + "o"
                combos = _generate_offsuit_combos(c_high, c_low)
                valid = [c for c in combos if _is_valid_combo(c, known_cards_set)]
                if valid:
                    breakdown[lbl] = valid

    return breakdown
