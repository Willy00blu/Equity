import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.tabs.entry_strategy_tab import RangeTab
    from gui.tabs.odds_tab import OddsTab
    from gui.tabs.sim_tab import SimTab
    from gui.tabs.analysis_tab import AnalysisTab
except ImportError as e:
    print(f"Errore Importazione: {e}")
    class RangeTab(tk.Frame): pass
    class OddsTab(tk.Frame): pass
    class SimTab(tk.Frame): pass

class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Suite Pro")

        self.default_size = "500x650"
        self.sim_size = "950x800"

        self.root.geometry(self.default_size)

        style = ttk.Style()
        style.theme_use('clam')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tab_range = RangeTab(self.notebook)
        self.notebook.add(self.tab_range, text="RANGE MANAGER")

        self.tab_odds = OddsTab(self.notebook)
        self.notebook.add(self.tab_odds, text="RISK EVALUATOR")

        self.tab_sim = SimTab(self.notebook)
        self.notebook.add(self.tab_sim, text="EQUITY CALCULATOR")

        self.tab_analysis = AnalysisTab(self.notebook)
        self.notebook.add(self.tab_analysis, text="PLAYER ANALYSIS")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        current_tab_index = self.notebook.index(self.notebook.select())
        tab_text = self.notebook.tab(current_tab_index, "text")

        if "EQUITY CALCULATOR" in tab_text:
            self.root.geometry(self.sim_size)
        else:
            self.root.geometry(self.default_size)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()
