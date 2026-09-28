# Equity

A desktop poker analysis tool for 6-max cash games. Built with Python and Tkinter, with a Monte Carlo equity engine written in C.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Range Manager** — pre-flop open-raise decisions by position (EP, MP, CO, BTN, SB)
- **Risk Evaluator** — pot odds calculator with the outs rule (×2 / ×4)
- **Equity Calculator** — Monte Carlo simulation against a villain range, with equity chart and hand distribution table
- **Player Analysis** — opponent profiling from HUD stats (VPIP, PFR, 3-Bet%)

---

## Requirements

- Python 3.8+
- macOS (arm64) — the included `poker.dylib` is compiled for Apple Silicon

```bash
pip install matplotlib
```

To recompile the C engine for a different architecture:
```bash
clang -arch arm64 -shared -fPIC -o logic/equity_engine/poker.dylib logic/equity_engine/poker.c
```

---

## Usage

```bash
python3 main.py
```

---

## Project Structure

```
poker/
├── main.py
├── gui/
│   ├── range_selector.py          # Interactive 13x13 hand grid
│   └── tabs/
│       ├── entry_strategy_tab.py
│       ├── odds_tab.py
│       ├── sim_tab.py
│       └── analysis_tab.py
└── logic/
    ├── entry_strategy/
    │   ├── charts.py              # Pre-flop range database
    │   └── decision_maker.py
    ├── equity_engine/
    │   ├── poker.c                # Monte Carlo engine
    │   ├── poker.dylib            # Compiled C library (arm64)
    │   ├── range_parser.py        # Range notation parser
    │   └── simulation_core.py     # ctypes bridge
    ├── investment_calc/
    │   └── risk_evaluator.py
    └── player_profiler.py
```

---

## How It Works

### Range Manager

Looks up the input hand against a database of GTO-approximate open-raise ranges for each position. Hands are classified as always open, conditional (e.g. open only if BB is weak), or fold.

### Risk Evaluator

Calculates pot odds and compares them against approximated equity via the outs rule:

```
required_equity = bet / (pot + 2 × bet)
actual_equity   = outs × 2   (one card to come)
actual_equity   = outs × 4   (all-in on flop, two cards to come)
```

A call is profitable when `actual_equity >= required_equity`. A margin within 5% is flagged as borderline (implied odds territory).

### Equity Calculator

The most complex module. It runs a full Monte Carlo simulation of Hero's hand against a villain range, accounting for blockers, board texture, and combo frequency.

#### Range parsing

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

#### Monte Carlo simulation

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

#### Weighted equity

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

#### Output

After all simulations complete, the worker thread sends the results back to the main thread via `root.after()` (thread-safe Tkinter callback) and updates three things simultaneously:

- **Bar chart**: one bar per combo group, green if equity ≥ 50%, red otherwise, with a dashed 50% reference line
- **Hand distribution table**: frequency of each hand type Hero achieves, sorted descending, also weighted by combo count
- **Range grid heatmap**: the 13×13 interactive grid gets colored using a red → yellow → green gradient based on the equity of each cell

### Player Analysis

Derives two metrics from HUD stats:

- **Gap** (`VPIP − PFR`): high gap = player calls a lot instead of raising (passive)
- **Aggro Ratio** (`PFR / VPIP`): close to 1 = raises almost everything they play

These feed a decision tree that classifies players into archetypes: NIT, Weak Tight, TAG variants, LAG, Bad Reg, Whale/Station, Maniac, and Loose Passive — each with specific counter-strategies.

---

## License

MIT
