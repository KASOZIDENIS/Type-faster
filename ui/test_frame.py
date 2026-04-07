"""
Timed typing test frame: choose duration, type, see results.
"""
import tkinter as tk
from tkinter import ttk
import random
import theme
from ui.keyboard_widget import KeyboardWidget


# Built-in word pool for random tests
WORD_POOL = (
    "the and to a of it is in that was he she for on are with as at his "
    "they be this from had not but what all were when there can an said each "
    "which do their time if will how each about up out many then them these "
    "so some her would make like him into has look two more write go see "
    "number no way could people my than first water been call who oil sit "
    "now find long down day did get come made may part over new sound take only "
    "little work know place years live me back give most very after thing our "
    "just name good sentence man think say great where help through much before "
    "line right too mean old any same tell boy follow came want show also around "
    "form three small set put end does another well large must big even such "
    "because turn here why asked went men read need land different home us move "
    "try kind hand picture again change off play spell air away animal house point"
).split()


def generate_random_text(word_count: int = 60) -> str:
    words = random.choices(WORD_POOL, k=word_count)
    return " ".join(words)


DURATIONS = [30, 60, 120]
DURATION_LABELS = ["30s", "60s", "2 min"]


class TestFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="TFrame")
        self._duration = 60
        self._timer_id = None
        self._remaining = 0
        self._test_active = False
        self._custom_text = ""
        self._build()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x", padx=24, pady=(16, 8))

        ttk.Button(top, text="← Home", style="Ghost.TButton",
                   command=self._go_home).pack(side="left")
        ttk.Label(top, text="Typing Test", style="Heading.TLabel").pack(
            side="left", padx=16)

        ttk.Separator(self).pack(fill="x", padx=24, pady=4)

        # Controls row
        ctrl = ttk.Frame(self, style="TFrame")
        ctrl.pack(fill="x", padx=24, pady=6)

        ttk.Label(ctrl, text="Duration:", style="TLabel").pack(side="left", padx=(0, 8))
        self._dur_var = tk.IntVar(value=60)
        for dur, lbl in zip(DURATIONS, DURATION_LABELS):
            rb = ttk.Radiobutton(ctrl, text=lbl, variable=self._dur_var, value=dur,
                                 command=self._on_duration_change)
            rb.pack(side="left", padx=4)

        ttk.Separator(ctrl, orient="vertical").pack(side="left", padx=12, fill="y")

        ttk.Label(ctrl, text="Text:", style="TLabel").pack(side="left", padx=(0, 8))
        self._text_mode = tk.StringVar(value="random")
        ttk.Radiobutton(ctrl, text="Random", variable=self._text_mode,
                        value="random", command=self._on_mode_change).pack(side="left", padx=4)
        ttk.Radiobutton(ctrl, text="Custom", variable=self._text_mode,
                        value="custom", command=self._on_mode_change).pack(side="left", padx=4)

        ttk.Button(ctrl, text="New Text", style="Secondary.TButton",
                   command=self._new_text, padding=(10, 4)).pack(side="left", padx=8)

        # Timer display
        timer_frame = ttk.Frame(self, style="TFrame")
        timer_frame.pack(pady=4)
        self._timer_var = tk.StringVar(value="60")
        tk.Label(timer_frame, textvariable=self._timer_var,
                 bg=theme.BG_ROOT, fg=theme.ACCENT,
                 font=(theme.FONT_FAMILY_UI, 42, "bold")).pack()
        tk.Label(timer_frame, text="seconds",
                 bg=theme.BG_ROOT, fg=theme.TEXT_SECOND,
                 font=theme.FONT_SMALL).pack()

        # Live stats
        stats_row = ttk.Frame(self, style="TFrame")
        stats_row.pack(fill="x", padx=24, pady=4)

        self._wpm_var  = tk.StringVar(value="0")
        self._acc_var  = tk.StringVar(value="100%")
        self._err_var  = tk.StringVar(value="0")
        self._chars_var = tk.StringVar(value="0")

        for var, lbl, col in [
            (self._wpm_var,   "Live WPM",  0),
            (self._acc_var,   "Accuracy",  1),
            (self._err_var,   "Errors",    2),
            (self._chars_var, "Chars",     3),
        ]:
            cell = ttk.Frame(stats_row, style="Card.TFrame")
            cell.grid(row=0, column=col, padx=6, sticky="ew")
            stats_row.columnconfigure(col, weight=1)
            ttk.Label(cell, textvariable=var, style="StatSm.TLabel").pack(pady=(6, 0))
            ttk.Label(cell, text=lbl, style="StatLbl.TLabel").pack(pady=(0, 6))

        # Custom text entry (hidden by default)
        self._custom_frame = ttk.Frame(self, style="TFrame")
        self._custom_entry = tk.Text(
            self._custom_frame,
            height=3,
            font=theme.FONT_TYPE_SM,
            bg=theme.BG_INPUT,
            fg=theme.TEXT_PRIMARY,
            insertbackground=theme.ACCENT,
            wrap="word",
            relief="flat",
            bd=0,
            padx=12, pady=8,
        )
        self._custom_entry.pack(fill="x", padx=24, pady=4)
        ttk.Button(self._custom_frame, text="Use This Text",
                   style="Secondary.TButton",
                   command=self._use_custom_text,
                   **theme.BTN_PAD).pack(anchor="e", padx=24, pady=4)

        # Typing text display
        txt_frame = tk.Frame(self, bg=theme.BG_INPUT)
        txt_frame.pack(fill="both", padx=24, pady=6, expand=True)

        self._text_widget = tk.Text(
            txt_frame,
            font=theme.FONT_TYPE,
            bg=theme.BG_INPUT,
            fg=theme.PENDING,
            insertbackground=theme.ACCENT,
            wrap="word",
            cursor="none",
            state="disabled",
            relief="flat", bd=0,
            padx=20, pady=20,
            height=5,
        )
        self._text_widget.pack(fill="both", expand=True)
        self._text_widget.tag_configure("correct",   foreground=theme.CORRECT)
        self._text_widget.tag_configure("incorrect", foreground=theme.INCORRECT,
                                        underline=True)
        self._text_widget.tag_configure("current",   background=theme.CURRENT_BG,
                                        foreground=theme.CURRENT_FG)
        self._text_widget.tag_configure("pending",   foreground=theme.PENDING)

        # Keyboard
        kb_frame = ttk.Frame(self, style="TFrame")
        kb_frame.pack(pady=4)
        self._keyboard = KeyboardWidget(kb_frame)
        self._keyboard.pack()

        # Hint label
        self._hint_var = tk.StringVar(value="Start typing to begin the timer.")
        ttk.Label(self, textvariable=self._hint_var,
                  style="Muted.TLabel").pack(pady=4)

        # Load initial text
        self._load_text()

    # ── Text loading ──────────────────────────────────────────────────────────

    def _load_text(self):
        self._cancel_timer()
        self._test_active = False
        self._remaining = self._dur_var.get()
        self._timer_var.set(str(self._remaining))
        self._hint_var.set("Start typing to begin the timer.")

        if self._text_mode.get() == "custom" and self._custom_text.strip():
            text = self._custom_text.strip()
        else:
            text = generate_random_text(80)

        engine = self.app.engine
        engine.load_text(text)
        self._render_text()
        self._update_stats()
        if text:
            self._keyboard.highlight_key(text[0])

    def _new_text(self):
        self._load_text()

    def _on_duration_change(self):
        self._load_text()

    def _on_mode_change(self):
        if self._text_mode.get() == "custom":
            self._custom_frame.pack(fill="x", padx=0, pady=0,
                                    before=self._text_widget.master)
        else:
            self._custom_frame.pack_forget()
            self._load_text()

    def _use_custom_text(self):
        self._custom_text = self._custom_entry.get("1.0", "end").strip()
        self._load_text()

    # ── Key handling ──────────────────────────────────────────────────────────

    def activate(self):
        root = self.app.root
        root.bind("<Key>", self._on_key, add=True)

    def deactivate(self):
        try:
            self.app.root.unbind("<Key>")
        except Exception:
            pass
        self._cancel_timer()
        self._test_active = False

    def _on_key(self, event):
        engine = self.app.engine
        if engine.finished:
            return

        char = event.char
        keysym = event.keysym

        if keysym == "Escape":
            self._load_text()
            return

        if not self._test_active:
            if char and len(char) == 1:
                self._start_timer()
            else:
                return

        if keysym == "BackSpace":
            engine.process_backspace()
        elif char and len(char) == 1:
            state = engine.process_key(char)
            if state["finished"]:
                self._on_test_end()
        else:
            return

        self._render_text()
        self._update_stats()

        idx = engine.current_index
        if idx < len(engine.target_text):
            self._keyboard.highlight_key(engine.target_text[idx])
        else:
            self._keyboard.clear()

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _start_timer(self):
        self._test_active = True
        self._remaining = self._dur_var.get()
        self._hint_var.set("Typing… press Escape to restart.")
        self._tick()

    def _tick(self):
        if not self._test_active:
            return
        self._remaining -= 1
        self._timer_var.set(str(self._remaining))
        if self._remaining <= 0:
            self._on_test_end()
        else:
            self._timer_id = self.after(1000, self._tick)

    def _cancel_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    # ── Render / stats ────────────────────────────────────────────────────────

    def _render_text(self):
        engine = self.app.engine
        text = engine.target_text
        states = engine.get_char_states()
        tw = self._text_widget
        tw.config(state="normal")
        tw.delete("1.0", "end")
        for ch, state in zip(text, states):
            tw.insert("end", ch, state)
        tw.config(state="disabled")

    def _update_stats(self):
        engine = self.app.engine
        self._wpm_var.set(f"{engine.get_wpm():.0f}")
        self._acc_var.set(f"{engine.get_accuracy():.0f}%")
        self._err_var.set(str(len(engine.error_positions)))
        self._chars_var.set(str(engine.current_index))

    # ── Test complete ─────────────────────────────────────────────────────────

    def _on_test_end(self):
        self._cancel_timer()
        self._test_active = False
        self._keyboard.clear()

        engine = self.app.engine
        results = engine.get_results()
        duration = self._dur_var.get()

        self.app.progress.record_test(
            wpm=results["wpm"],
            net_wpm=results["net_wpm"],
            accuracy=results["accuracy"],
            errors=results["errors"],
            duration=duration,
            text_snippet=engine.target_text[:60],
        )

        self._show_results(results, duration)

    def _show_results(self, results, duration):
        overlay = tk.Toplevel(self)
        overlay.title("Test Results")
        overlay.configure(bg=theme.BG_PANEL)
        overlay.resizable(False, False)
        overlay.grab_set()

        rx = self.app.root.winfo_x() + self.app.root.winfo_width() // 2 - 220
        ry = self.app.root.winfo_y() + self.app.root.winfo_height() // 2 - 180
        overlay.geometry(f"440x360+{rx}+{ry}")

        tk.Label(overlay, text="Test Results",
                 bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY,
                 font=theme.FONT_TITLE).pack(pady=(20, 8))

        # Big WPM
        tk.Label(overlay, text=f"{results['wpm']:.0f}",
                 bg=theme.BG_PANEL, fg=theme.ACCENT,
                 font=(theme.FONT_FAMILY_UI, 56, "bold")).pack()
        tk.Label(overlay, text="WPM",
                 bg=theme.BG_PANEL, fg=theme.TEXT_SECOND,
                 font=theme.FONT_BODY).pack()

        info = tk.Frame(overlay, bg=theme.BG_PANEL)
        info.pack(pady=10)

        best = self.app.progress.get_best_wpm()
        rows = [
            ("Net WPM",    f"{results['net_wpm']:.1f}"),
            ("Accuracy",   f"{results['accuracy']:.1f}%"),
            ("Errors",     str(results["errors"])),
            ("Duration",   f"{duration}s"),
            ("All-Time Best", f"{best:.0f} WPM"),
        ]
        for label, value in rows:
            row = tk.Frame(info, bg=theme.BG_PANEL)
            row.pack(fill="x", padx=30, pady=2)
            tk.Label(row, text=label, bg=theme.BG_PANEL,
                     fg=theme.TEXT_SECOND, font=theme.FONT_BODY,
                     width=16, anchor="w").pack(side="left")
            colour = theme.CORRECT if label == "All-Time Best" and results["wpm"] >= best else theme.TEXT_PRIMARY
            tk.Label(row, text=value, bg=theme.BG_PANEL,
                     fg=colour, font=theme.FONT_HEADING).pack(side="left")

        btn_row = tk.Frame(overlay, bg=theme.BG_PANEL)
        btn_row.pack(pady=14)

        tk.Button(btn_row, text="Try Again",
                  bg=theme.ACCENT, fg="#fff",
                  font=theme.FONT_BODY, bd=0, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=lambda: [overlay.destroy(), self._load_text()]
                  ).pack(side="left", padx=6)
        tk.Button(btn_row, text="Home",
                  bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY,
                  font=theme.FONT_BODY, bd=0, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=lambda: [overlay.destroy(), self._go_home()]
                  ).pack(side="left", padx=6)
        tk.Button(btn_row, text="View Progress",
                  bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY,
                  font=theme.FONT_BODY, bd=0, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=lambda: [overlay.destroy(), self.app.show_frame("progress")]
                  ).pack(side="left", padx=6)

    def _go_home(self):
        self.app.show_frame("home")

    def on_show(self):
        """Called when this frame becomes visible."""
        self._load_text()
