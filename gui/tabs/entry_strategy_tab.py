import tkinter as tk
from logic.entry_strategy import decision_maker

class RangeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.parent = parent
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self, text="RANGE MANAGER (6-Max)", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(self, text="1. Posizione:", font=("Arial", 10, "bold")).pack()
        frame_pos = tk.Frame(self)
        frame_pos.pack(pady=5)
        self.selected_pos = tk.StringVar(value="EP")
        for pos in ["EP", "MP", "CO", "BTN", "SB"]:
            tk.Radiobutton(frame_pos, text=pos, variable=self.selected_pos, value=pos,
                           command=self.fai_analisi_range).pack(side="left")

        tk.Label(self, text="2. Tipologia:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        frame_suit = tk.Frame(self)
        frame_suit.pack(pady=5)
        self.selected_suit = tk.StringVar(value="s")

        tk.Radiobutton(frame_suit, text="Suited (s)", variable=self.selected_suit, value="s",
                       fg="white", selectcolor="black", command=self.fai_analisi_range).pack(side="left")
        tk.Radiobutton(frame_suit, text="Offsuit (o)", variable=self.selected_suit, value="o",
                       fg="white", selectcolor="black", command=self.fai_analisi_range).pack(side="left")

        tk.Label(self, text="3. Carte (es. AK, 77):", font=("Arial", 10)).pack(pady=(15, 0))
        self.entry_hand = tk.Entry(self, font=("Courier", 24), width=6, justify="center")
        self.entry_hand.pack(pady=5)
        self.entry_hand.bind('<Return>', self.fai_analisi_range)

        tk.Button(self, text="ANALIZZA", command=self.fai_analisi_range,
                  bg="black", fg="black", highlightbackground="black",
                  font=("Arial", 11, "bold"), width=20).pack(pady=15)

        self.res_range_frame = tk.LabelFrame(self, text="Esito", height=130)
        self.res_range_frame.pack(pady=10, fill="x")
        self.res_range_frame.pack_propagate(False)
        self.lbl_range_title = tk.Label(self.res_range_frame, text="...", font=("Helvetica", 14, "bold"))
        self.lbl_range_title.pack(pady=15)
        self.lbl_range_desc = tk.Label(self.res_range_frame, text="", wraplength=350)
        self.lbl_range_desc.pack()

    def fai_analisi_range(self, event=None):
        pos = self.selected_pos.get()
        raw = self.entry_hand.get().strip().upper()[:2]
        if not raw:
            return
        seme = self.selected_suit.get()

        res = decision_maker.calcola_azione(pos, raw + seme)

        bg = res.get("bg", "#f0f0f0")
        fg = res.get("fg", "black")
        self.res_range_frame.config(bg=bg)
        self.lbl_range_title.config(text=res["titolo"], bg=bg, fg=fg)
        self.lbl_range_desc.config(text=res["desc"], bg=bg, fg=fg)
        if event and event.keysym == 'Return':
            self.entry_hand.select_range(0, tk.END)
