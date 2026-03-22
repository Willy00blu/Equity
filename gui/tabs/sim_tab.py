import tkinter as tk
from tkinter import ttk, messagebox
import threading

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from logic.equity_engine import simulation_core
from logic.equity_engine import range_parser
from gui.range_selector import EmbeddedRangeSelector

class SimTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.parent = parent
        self.canvas = None
        self.lbl_chart_placeholder = None
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=6)
        self.rowconfigure(0, weight=1)

        left_panel = tk.Frame(self)
        left_panel.grid(row=0, column=0, sticky="nswe", padx=(0, 10))

        tk.Label(left_panel, text="CONFIGURAZIONE", font=("Arial", 10, "bold"), fg="#333").pack(anchor="w", pady=5)

        input_frame = tk.Frame(left_panel)
        input_frame.pack(fill="x", pady=5)

        tk.Label(input_frame, text="Tua Mano:").grid(row=0, column=0, sticky="w")
        self.entry_hero = tk.Entry(input_frame, font=("Courier", 12), width=10, bg="#000000")
        self.entry_hero.grid(row=0, column=1, padx=5, sticky="w")
        self.entry_hero.insert(0, "Ah Kh")

        tk.Label(input_frame, text="Board:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_board = tk.Entry(input_frame, font=("Courier", 12), width=10)
        self.entry_board.grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(left_panel, text="Range Avversario:", font=("Arial", 10, "bold"), fg="#333").pack(anchor="w", pady=(15, 2))

        self.villain_range_var = tk.StringVar()
        self.entry_villain = tk.Entry(left_panel, textvariable=self.villain_range_var, font=("Arial", 9), fg="#555")
        self.entry_villain.pack(fill="x", pady=(0, 5))
        self.entry_villain.insert(0, "QQ++, 55-77")

        self.range_grid = EmbeddedRangeSelector(left_panel, self.villain_range_var)
        self.range_grid.pack(anchor="center", pady=5, fill="both", expand=True)

        self.btn_run = tk.Button(left_panel, text="CALCOLA EQUITY", command=self.avvia_simulazione,
                                 bg="#4CAF50", fg="black", font=("Arial", 12, "bold"), height=2)
        self.btn_run.pack(fill="x", pady=20, side="bottom")

        right_panel = tk.Frame(self, bg="white", relief="sunken", bd=1)
        right_panel.grid(row=0, column=1, sticky="nswe")

        self.frame_top = tk.Frame(right_panel, bg="white")
        self.frame_top.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        tk.Label(self.frame_top, text="Equity vs Range", font=("Arial", 10, "bold"), bg="white").pack(anchor="w")

        self.frame_chart = tk.Frame(self.frame_top, bg="white")
        self.frame_chart.pack(fill="both", expand=True)

        self.lbl_chart_placeholder = tk.Label(self.frame_chart, text="In attesa di simulazione...", bg="white", fg="gray")
        self.lbl_chart_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self.frame_bottom = tk.Frame(right_panel, bg="#f9f9f9", height=200)
        self.frame_bottom.pack(side="bottom", fill="x", padx=5, pady=5)

        tk.Label(self.frame_bottom, text="Probabilita Punto Hero (Media)", font=("Arial", 10, "bold"), bg="#000000").pack(anchor="w", pady=(5, 0))

        columns = ("punto", "freq")
        self.stats_tree = ttk.Treeview(self.frame_bottom, columns=columns, show="headings", height=6)

        self.stats_tree.heading("punto", text="Punto")
        self.stats_tree.heading("freq", text="Frequenza (%)")

        self.stats_tree.column("punto", width=150)
        self.stats_tree.column("freq", width=100, anchor="center")

        sb = ttk.Scrollbar(self.frame_bottom, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscroll=sb.set)

        self.stats_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def avvia_simulazione(self):
        hero = self.entry_hero.get().strip()
        board = self.entry_board.get().strip()
        villain_range = self.entry_villain.get().strip()

        if not hero or not villain_range:
            messagebox.showwarning("Dati Mancanti", "Inserisci Mano Hero e seleziona un Range.")
            return

        self.btn_run.config(state="disabled", text="Calcolo in corso...")
        self.range_grid.load_from_string(villain_range)

        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        t = threading.Thread(target=self.thread_worker, args=(hero, board, villain_range), daemon=True)
        t.start()

    def thread_worker(self, hero, board, villain_range):
        breakdown = range_parser.parse_range_breakdown(villain_range, hero, board)

        if not breakdown:
            self.parent.after(0, lambda: messagebox.showerror("Errore", "Range non valido o carte duplicate."))
            self.parent.after(0, lambda: self.btn_run.config(state="normal", text="CALCOLA EQUITY"))
            return

        total_equity_sum = 0.0
        total_combos_count = 0
        results_equity = {}
        aggregated_hand_stats = {}

        sims_per_hand = 20000

        for label, combos_list in breakdown.items():
            num_combos = len(combos_list)
            if not combos_list:
                continue

            # usiamo la prima combo come rappresentativa del gruppo: per mani suited
            # il seme non cambia l'equity in modo significativo preflop
            first_combo = combos_list[0]
            res = simulation_core.run_simulation(hero, board, sims_per_hand, villain_ints_pair=first_combo)

            if "error" in res:
                continue

            equity = res["equity"]
            results_equity[label] = equity

            # media ponderata: le combo più frequenti pesano di più sull'equity finale
            total_equity_sum += equity * num_combos
            total_combos_count += num_combos

            stats = res.get("hand_stats", {})
            for h_type, pct in stats.items():
                if h_type not in aggregated_hand_stats:
                    aggregated_hand_stats[h_type] = 0.0
                aggregated_hand_stats[h_type] += pct * num_combos

        final_aggregate_equity = 0.0
        final_avg_stats = {}

        if total_combos_count > 0:
            final_aggregate_equity = total_equity_sum / total_combos_count
            for k, v in aggregated_hand_stats.items():
                final_avg_stats[k] = round(v / total_combos_count, 2)

        self.parent.after(0, lambda: self.aggiorna_interfaccia(results_equity, final_aggregate_equity, final_avg_stats))

    def aggiorna_interfaccia(self, equity_data, avg_equity, hand_stats):
        self.btn_run.config(state="normal", text="CALCOLA EQUITY")

        self.disegna_grafico(equity_data, avg_equity)

        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        if hand_stats:
            sorted_stats = sorted(hand_stats.items(), key=lambda x: x[1], reverse=True)
            for k, v in sorted_stats:
                if v > 0.1:
                    self.stats_tree.insert("", "end", values=(k, f"{v}%"))
        else:
            self.stats_tree.insert("", "end", values=("Nessun dato", "-"))

        self.range_grid.apply_heatmap(equity_data)

    def disegna_grafico(self, data, final_aggregate_equity):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.lbl_chart_placeholder:
            self.lbl_chart_placeholder.destroy()

        if not data:
            return

        filtered_data = {k: v for k, v in data.items() if v > 0}
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())

        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=100)

        colors = ['#66BB6A' if v >= 50 else '#EF5350' for v in values]
        bars = ax.bar(labels, values, color=colors)

        ax.axhline(50, linestyle="--", linewidth=1, color='gray', alpha=0.5)

        for bar in bars:
            height = bar.get_height()
            if height > 10:
                ax.text(bar.get_x() + bar.get_width() / 2., height - 5,
                        f'{height:.0f}%', ha='center', va='bottom', fontsize=8, color='white', fontweight='bold')

        ax.set_ylim(0, 105)
        ax.set_ylabel("Equity %")
        ax.set_title(f"Totale vs Range: {final_aggregate_equity:.1f}%", color="#333", fontweight="bold")

        if len(labels) > 6:
            plt.xticks(rotation=45, ha='right', fontsize=8)

        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_chart)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
