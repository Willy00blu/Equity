import tkinter as tk
from tkinter import messagebox

try:
    from logic import player_profiler
except ImportError:
    print("Errore: Impossibile importare logic.player_profiler")

class AnalysisTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent

        self.var_vpip = tk.StringVar(value="25")
        self.var_pfr = tk.StringVar(value="20")
        self.var_3bet = tk.StringVar(value="6")
        self.var_hands = tk.StringVar(value="100")

        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left_frame = tk.LabelFrame(self, text="Statistiche HUD", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))

        inputs = [
            ("VPIP %", self.var_vpip),
            ("PFR %", self.var_pfr),
            ("3-Bet %", self.var_3bet),
            ("Totale Mani", self.var_hands)
        ]

        for label_text, var in inputs:
            lbl = tk.Label(left_frame, text=label_text, font=("Arial", 9, "bold"), anchor="w")
            lbl.pack(fill="x", pady=(10, 0))
            entry = tk.Entry(left_frame, textvariable=var, font=("Courier", 12),
                             bg="white", fg="black", insertbackground="black")
            entry.pack(fill="x", pady=(2, 0))

        btn_analyze = tk.Button(left_frame, text="ANALIZZA PROFILO",
                                command=self.on_analyze_click,
                                bg="#2196F3", fg="black", font=("Arial", 11, "bold"))
        btn_analyze.pack(fill="x", pady=25, side="bottom")

        right_frame = tk.LabelFrame(self, text="Report Strategico", padx=10, pady=10, bg="white")
        right_frame.grid(row=0, column=1, sticky="nswe")

        self.lbl_profile_name = tk.Label(right_frame, text="?", font=("Arial", 22, "bold"), bg="white", fg="#ccc")
        self.lbl_profile_name.pack(pady=(10, 5))

        self.lbl_desc = tk.Label(right_frame, text="Inserisci i dati per l'analisi.", font=("Arial", 10, "italic"), bg="white", fg="#555")
        self.lbl_desc.pack(pady=(0, 15))

        self.txt_strategy = tk.Text(right_frame, font=("Arial", 10), wrap="word", height=15, bd=0,
                                    bg="white", fg="black", padx=5)
        self.txt_strategy.pack(fill="both", expand=True)
        self.txt_strategy.config(state="disabled")

    def on_analyze_click(self):
        try:
            vpip = float(self.var_vpip.get())
            pfr = float(self.var_pfr.get())
            bet3 = float(self.var_3bet.get())
            hands = int(self.var_hands.get())
        except ValueError:
            messagebox.showerror("Errore Input", "Inserisci solo numeri validi (usa il punto per i decimali).")
            return

        try:
            result = player_profiler.analyze_stats(vpip, pfr, bet3, hands)
        except NameError:
            messagebox.showerror("Errore", "Modulo logica non trovato. Assicurati di aver creato logic/player_profiler.py")
            return

        self.lbl_profile_name.config(text=result["name"], fg=result["color"])
        self.lbl_desc.config(text=result["desc"])

        final_text = ""

        if result["reliability"]:
            final_text += f"{result['reliability']}\n\n"

        final_text += "STRATEGIA CONSIGLIATA:\n"
        for point in result["strategy"]:
            final_text += f"• {point}\n"

        self.txt_strategy.config(state="normal")
        self.txt_strategy.delete("1.0", "end")
        self.txt_strategy.insert("1.0", final_text)
        self.txt_strategy.config(state="disabled")
