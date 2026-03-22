# Poker Suite Pro

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

Parses the villain range string into individual combos (e.g. `QQ+, AKs, 77-99`), filters out blockers from the hero hand and board, then runs the C Monte Carlo engine for each combo group. The final equity is a weighted average by number of combos:

```
final_equity = Σ(equity_i × combos_i) / Σ(combos_i)
```

The C engine uses XorShift128 as RNG and a 7-card hand evaluator that encodes hand strength into a single 32-bit integer for fast comparison.

### Player Analysis

Derives two metrics from HUD stats:

- **Gap** (`VPIP − PFR`): high gap = player calls a lot instead of raising (passive)
- **Aggro Ratio** (`PFR / VPIP`): close to 1 = raises almost everything they play

These feed a decision tree that classifies players into archetypes: NIT, Weak Tight, TAG variants, LAG, Bad Reg, Whale/Station, Maniac, and Loose Passive — each with specific counter-strategies.

---

## License

MIT
