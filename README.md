# Equity

A Monte Carlo equity engine: it estimates, by simulation, how often a poker hand wins against a range of hands. The engine is written in C for speed; a small Python and Tkinter interface sends it the hand, the range and the board, and draws the results.

The point of the project is the probability model: dealing the missing cards at random thousands of times, comparing the hands, and weighting the results by how often each part of the range can actually occur.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Requirements and setup

- Python 3.8+ and `matplotlib` (`pip install -r requirements.txt`)
- macOS: the Python side loads the engine as `logic/equity_engine/poker.dylib`

The compiled library is not in the repository: build it once before the first run.

```bash
clang -O2 -shared -fPIC -o logic/equity_engine/poker.dylib logic/equity_engine/poker.c
python3 main.py
```

---

## How the engine works

It runs a full Monte Carlo simulation of Hero's hand against a villain range, accounting for blockers, board texture, and combo frequency.

### Range parsing

The villain range is expressed in standard poker notation and supports:

| Syntax | Meaning |
|--------|---------|
| `QQ` | exactly Queens |
| `QQ+` | Queens, Kings, Aces |
| `77-99` | Sevens, Eights, Nines |
| `AKs` | Ace-King suited (4 combos) |
| `AKo` | Ace-King offsuit (12 combos) |
| `AK` | both suited and offsuit (16 combos) |
| `AJs+` | AJs, AQs, AKs |
| `QQ+, AKs, 77-99` | comma-separated combinations |

The parser converts each entry into a list of concrete card pairs (as integers 0–51, encoded as `suit × 13 + rank`). Before adding a combo to the list it checks for **blockers**: any combo that uses a card already present in Hero's hand or on the board is discarded. This matters especially post-flop — if Hero holds `Ah` and the board has `Kh`, all combos of AK or suited hands using those specific cards are automatically removed.

Each hand type generates a fixed number of combos:
- Pairs: **6** combos — C(4,2), one for each suit combination
- Suited: **4** combos — one per suit
- Offsuit: **12** combos — 4 suits × 3 different suits for the second card

### Monte Carlo simulation

For each combo group the C engine runs 20,000 simulations:

1. Build a clean deck of the 52 cards minus all known cards (Hero + Villain + Board)
2. Shuffle it with Fisher-Yates using XorShift128 as RNG
3. Deal the remaining board cards from the top of the shuffled deck to complete 7 cards for each player
4. Evaluate both 7-card hands and compare

The hand evaluator encodes the result as a single 32-bit integer:

```
result = (hand_type << 24) | (rank1 << 20) | (rank2 << 16) | ...

hand_type: 0 = High Card
           1 = Pair
           2 = Two Pair
           3 = Three of a Kind
           4 = Straight
           5 = Flush
           6 = Full House
           7 = Quads
           8 = Straight Flush
```

This means two hands can be compared with a single integer comparison — no branching logic needed. Kickers and secondary ranks are packed into the lower bits, so ties are broken correctly within the same hand type.

The engine also tracks how often Hero makes each hand type across simulations, which feeds the hand distribution table in the UI.

### Weighted equity

Running one simulation per combo group (using the first combo as representative) is fast but naive — different combo groups appear with different frequencies. QQ has 6 combos, AKs has 4. If you average their equities without accounting for this, the result is wrong.

The final equity is computed as a **frequency-weighted average**:

```
final_equity = Σ(equity_i × num_combos_i) / Σ(num_combos_i)
```

Example — Hero holds `AhKh`, villain range is `QQ+`:

| Group | Combos | Equity vs AK |
|-------|--------|-------------|
| QQ    | 6      | ~46%        |
| KK    | 3*     | ~30%        |
| AA    | 6      | ~12%        |

*KK loses one combo because `Kh` is in Hero's hand*

```
final = (46×6 + 30×3 + 12×6) / (6+3+6) = (276+90+72) / 15 ≈ 29.2%
```

A simple average of 46, 30, 12 would give 29.3% — close here, but the gap grows significantly with unbalanced ranges.

### Output

After all simulations complete, the worker thread sends the results back to the main thread via `root.after()` (thread-safe Tkinter callback) and updates three things simultaneously:

- **Bar chart**: one bar per combo group, green if equity ≥ 50%, red otherwise, with a dashed 50% reference line
- **Hand distribution table**: frequency of each hand type Hero achieves, sorted descending, also weighted by combo count
- **Range grid heatmap**: the 13×13 interactive grid gets colored using a red → yellow → green gradient based on the equity of each cell

## Also in the app

The interface has three smaller tabs around the engine, written as exercises: a pre-flop chart by position, a pot-odds check with the outs rule (×2 / ×4), and a classifier of playing styles from three summary statistics.

---

## Project structure

```
├── main.py
├── gui/
│   ├── range_selector.py          # the 13×13 hand grid
│   └── tabs/                      # the engine's tab (sim_tab.py) and the three smaller ones
└── logic/
    ├── equity_engine/
    │   ├── poker.c                # the Monte Carlo engine and the hand evaluator
    │   ├── range_parser.py        # range notation → concrete card pairs, without blocked combos
    │   └── simulation_core.py     # the ctypes bridge to poker.dylib
    ├── entry_strategy/, investment_calc/, player_profiler.py   # the smaller tabs
```

---

## License

MIT
