import tkinter as tk
from logic.investment_calc import risk_evaluator

class OddsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.parent = parent
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self, text="CALCOLATORE ODDS", font=("Arial", 12, "bold")).pack(pady=10)

        frame_input_odds = tk.Frame(self)
        frame_input_odds.pack(pady=5)

        tk.Label(frame_input_odds, text="Piatto Totale ($):").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_pot = tk.Entry(frame_input_odds, width=10, font=("Arial", 12))
        self.entry_pot.grid(row=0, column=1, padx=5)
        self.entry_pot.bind('<Return>', self.calcola_odds)

        tk.Label(frame_input_odds, text="Bet Avversario ($):").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_bet = tk.Entry(frame_input_odds, width=10, font=("Arial", 12))
        self.entry_bet.grid(row=1, column=1, padx=5)

        tk.Label(frame_input_odds, text="I tuoi Outs (n):", fg="#ff5555", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="e", pady=5)
        self.entry_outs = tk.Entry(frame_input_odds, width=10, font=("Arial", 12), fg="#d32f2f")
        self.entry_outs.grid(row=2, column=1, padx=5)
        self.entry_outs.bind('<Return>', self.calcola_odds)

        self.var_allin = tk.BooleanVar()
        chk_allin = tk.Checkbutton(self, text="Sono All-In (Vedo 2 carte)", variable=self.var_allin,
                                   font=("Arial", 10, "bold"), fg="orange", command=self.calcola_odds)
        chk_allin.pack(pady=5)

        tk.Label(self, text="Scenari Comuni (Outs):", font=("Arial", 9, "bold")).pack(pady=(10, 5))
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=5)

        buttons_data = [
            ("Incastro (4)", 4), ("Overcards (6)", 6),
            ("Bilaterale (8)", 8), ("Colore (9)", 9),
            ("Incastro+Colore (12)", 12), ("Monster (15)", 15)
        ]

        row_idx = 0
        col_idx = 0
        for text, val in buttons_data:
            btn = tk.Button(frame_buttons, text=text, width=14,
                            command=lambda v=val: self.imposta_outs_e_calcola(v))
            btn.grid(row=row_idx, column=col_idx, padx=3, pady=3)
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        tk.Button(self, text="CALCOLA ODDS", command=self.calcola_odds,
                  bg="black", fg="white", highlightbackground="black",
                  font=("Arial", 11, "bold"), width=25).pack(pady=15)

        self.res_odds_frame = tk.LabelFrame(self, text="Decisione Matematica", height=130)
        self.res_odds_frame.pack(pady=5, fill="x")
        self.res_odds_frame.pack_propagate(False)

        self.lbl_odds_decision = tk.Label(self.res_odds_frame, text="...", font=("Helvetica", 16, "bold"))
        self.lbl_odds_decision.pack(pady=15)
        self.lbl_odds_detail = tk.Label(self.res_odds_frame, text="", bg=None)
        self.lbl_odds_detail.pack()

    def imposta_outs_e_calcola(self, valore):
        self.entry_outs.delete(0, tk.END)
        self.entry_outs.insert(0, str(valore))
        self.calcola_odds()

    def calcola_odds(self, event=None):
        pot = self.entry_pot.get()
        bet = self.entry_bet.get()
        outs = self.entry_outs.get()
        is_allin = self.var_allin.get()

        res = risk_evaluator.calcola_pot_odds(pot, bet, outs, is_allin)

        if res["status"] == "ERROR":
            self.lbl_odds_decision.config(text="Errore", fg="red", bg="SystemButtonFace")
            self.lbl_odds_detail.config(text=res["msg"], bg="SystemButtonFace")
            return

        bg = res["bg"]
        self.res_odds_frame.config(bg=bg)
        self.lbl_odds_decision.config(text=res["decision"], bg=bg, fg="#333")
        self.lbl_odds_detail.config(text=res["msg"], bg=bg, fg="#333")
