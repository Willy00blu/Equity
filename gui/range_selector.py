import tkinter as tk

class EmbeddedRangeSelector(tk.Frame):
    def __init__(self, parent, string_var=None, cell_size=30):
        super().__init__(parent)
        self.string_var = string_var
        self.cell_size = cell_size

        self.grid_size = 13
        self.width = self.grid_size * self.cell_size
        self.height = self.grid_size * self.cell_size

        self.COLOR_BG = "#FFFFFF"
        self.COLOR_EMPTY = "#F0F0F0"
        self.COLOR_SELECTED = "#64B5F6"
        self.COLOR_TEXT = "#333333"
        self.COLOR_GRID = "#CCCCCC"

        self.rects = {}
        self.texts = {}
        self.selected_hands = set()

        self.canvas = tk.Canvas(self, width=self.width, height=self.height,
                                bg=self.COLOR_BG, highlightthickness=0)
        self.canvas.pack(pady=(0, 5))

        self._draw_grid()
        self.canvas.bind("<Button-1>", self._on_click)

        self._create_controls()

        if self.string_var:
            self.load_from_string(self.string_var.get())
            self.string_var.trace_add("write", lambda *args: self.load_from_string(self.string_var.get()))

    def _create_controls(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x")

        style = {"font": ("Arial", 9), "width": 8, "bg": "#e1e1e1", "relief": "groove"}

        tk.Button(btn_frame, text="Pairs", command=lambda: self.apply_preset("pairs"), **style).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Broadways", command=lambda: self.apply_preset("broadways"), **style).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Premium", command=lambda: self.apply_preset("premium"), **style).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Clear", command=lambda: self.apply_preset("clear"), **style).pack(side="right", padx=2)

    def apply_preset(self, mode):
        if mode == "clear":
            self.selected_hands.clear()
        else:
            ranks = "AKQJT98765432"
            for r in range(13):
                for c in range(13):
                    hand = self._get_hand_name(r, c)
                    should_select = False

                    if mode == "pairs":
                        if r == c:
                            should_select = True
                    elif mode == "broadways":
                        if r <= 4 and c <= 4:
                            should_select = True
                    elif mode == "premium":
                        if r == c and r <= 3:
                            should_select = True
                        elif r < c and r == 0 and c <= 2:
                            should_select = True
                        elif r > c and c == 0 and r == 1:
                            should_select = True

                    if should_select:
                        self.selected_hands.add(hand)

        self._update_string_var()
        self.load_from_string(self.string_var.get() if self.string_var else "")

    def _get_hand_name(self, r, c, ranks="AKQJT98765432"):
        rank_r = ranks[r]
        rank_c = ranks[c]
        if r < c:
            return f"{rank_r}{rank_c}s"
        elif r > c:
            return f"{rank_c}{rank_r}o"
        else:
            return f"{rank_r}{rank_c}"

    def _draw_grid(self):
        for r in range(13):
            for c in range(13):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                hand = self._get_hand_name(r, c)

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.COLOR_EMPTY, outline=self.COLOR_GRID
                )
                text_id = self.canvas.create_text(
                    x1 + self.cell_size / 2, y1 + self.cell_size / 2,
                    text=hand, font=("Arial", 8), fill=self.COLOR_TEXT
                )

                self.rects[hand] = rect_id
                self.texts[hand] = text_id

    def _on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= col < 13 and 0 <= row < 13:
            hand = self._get_hand_name(row, col)
            self.toggle_hand(hand)

    def toggle_hand(self, hand):
        if hand in self.selected_hands:
            self.selected_hands.remove(hand)
            self.canvas.itemconfig(self.rects[hand], fill=self.COLOR_EMPTY)
        else:
            self.selected_hands.add(hand)
            self.canvas.itemconfig(self.rects[hand], fill=self.COLOR_SELECTED)
        self._update_string_var()

    def _update_string_var(self):
        if self.string_var:
            text = ", ".join(sorted(list(self.selected_hands)))
            if self.string_var.get() != text:
                self.string_var.set(text)

    def load_from_string(self, text):
        for hand, rect_id in self.rects.items():
            self.canvas.itemconfig(rect_id, fill=self.COLOR_EMPTY)

        parts = [p.strip() for p in text.split(',') if p.strip()]
        current_hands = set()

        for p in parts:
            if p in self.rects:
                current_hands.add(p)
                self.canvas.itemconfig(self.rects[p], fill=self.COLOR_SELECTED)

        self.selected_hands = current_hands

    def apply_heatmap(self, equity_data):
        for hand, rect_id in self.rects.items():
            self.canvas.itemconfig(rect_id, fill=self.COLOR_EMPTY)

        for raw_hand, equity in equity_data.items():
            hand_str = str(raw_hand).strip()
            color = self._get_gradient_color(equity)

            if hand_str in self.rects:
                self.canvas.itemconfig(self.rects[hand_str], fill=color)
            else:
                # alcune label dal breakdown sono senza suffisso (es. "AK"), coloriamo entrambe le celle
                suited = hand_str + "s"
                offsuit = hand_str + "o"
                if suited in self.rects:
                    self.canvas.itemconfig(self.rects[suited], fill=color)
                if offsuit in self.rects:
                    self.canvas.itemconfig(self.rects[offsuit], fill=color)

        self.canvas.update_idletasks()

    def _get_gradient_color(self, equity):
        """Mappa l'equity a un colore: rosso (svantaggio) -> giallo (parita) -> verde (vantaggio)."""
        equity = max(0, min(100, equity))
        if 45 <= equity <= 55:
            return "#FFD700"
        elif equity < 45:
            ratio = equity / 45.0
            r = 255
            g = int(140 * ratio)
            b = 0
        else:
            ratio = (equity - 55) / 45.0
            r = int(180 * (1 - ratio))
            g = int(255 - (100 * ratio))
            b = 0
        return f"#{r:02x}{g:02x}{b:02x}"
