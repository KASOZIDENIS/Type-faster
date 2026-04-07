"""
Home / dashboard frame: shows stats summary and lesson grid.
"""
import tkinter as tk
from tkinter import ttk
import theme


class HomeFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="TFrame")
        self._build()

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=30, pady=(24, 6))

        ttk.Label(hdr, text="TypeFaster", style="Title.TLabel").pack(side="left")

        btn_frame = ttk.Frame(hdr, style="TFrame")
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="Test Mode", style="Accent.TButton",
                   command=lambda: self.app.show_frame("test"),
                   **theme.BTN_PAD).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Progress", style="Secondary.TButton",
                   command=lambda: self.app.show_frame("progress"),
                   **theme.BTN_PAD).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Settings", style="Ghost.TButton",
                   command=lambda: self.app.show_frame("settings"),
                   **theme.BTN_PAD).pack(side="left")

        ttk.Separator(self).pack(fill="x", padx=30, pady=4)

        # ── Stats strip ───────────────────────────────────────────────────────
        stats_outer = ttk.Frame(self, style="Card.TFrame")
        stats_outer.pack(fill="x", padx=30, pady=10)
        self._stat_vars = {}
        stats_data = [
            ("best_wpm",  "Best WPM",      "0"),
            ("avg_wpm",   "Avg WPM",       "0"),
            ("avg_acc",   "Avg Accuracy",  "0%"),
            ("sessions",  "Sessions",      "0"),
            ("lessons",   "Lessons Done",  "0"),
        ]
        for col, (key, label, default) in enumerate(stats_data):
            cell = ttk.Frame(stats_outer, style="Card.TFrame")
            cell.grid(row=0, column=col, padx=24, pady=14, sticky="ew")
            stats_outer.columnconfigure(col, weight=1)
            var = tk.StringVar(value=default)
            self._stat_vars[key] = var
            ttk.Label(cell, textvariable=var, style="StatSm.TLabel").pack()
            ttk.Label(cell, text=label, style="StatLbl.TLabel").pack()

        # ── Lessons heading ───────────────────────────────────────────────────
        ttk.Label(self, text="Lessons", style="Heading.TLabel").pack(
            anchor="w", padx=30, pady=(12, 4))

        # ── Scrollable lesson grid ────────────────────────────────────────────
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill="both", expand=True, padx=26, pady=(0, 16))

        canvas = tk.Canvas(container, bg=theme.BG_ROOT,
                           highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._lesson_inner = ttk.Frame(canvas, style="TFrame")
        self._lesson_window = canvas.create_window(
            (0, 0), window=self._lesson_inner, anchor="nw")

        self._lesson_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._lesson_window, width=e.width))
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._canvas = canvas
        self._lesson_cards = []

    def refresh(self):
        """Called every time the home frame is shown."""
        pt = self.app.progress
        lm = self.app.lesson_manager
        completed = pt.get_completed_lessons()

        self._stat_vars["best_wpm"].set(f"{pt.get_best_wpm():.0f}")
        self._stat_vars["avg_wpm"].set(f"{pt.get_average_wpm():.0f}")
        self._stat_vars["avg_acc"].set(f"{pt.get_average_accuracy():.0f}%")
        self._stat_vars["sessions"].set(str(pt.get_total_sessions()))
        self._stat_vars["lessons"].set(str(len(completed)))

        # Rebuild lesson cards
        for w in self._lesson_inner.winfo_children():
            w.destroy()
        self._lesson_cards.clear()

        lessons = lm.get_all_lessons()
        cols = 3
        for idx, lesson in enumerate(lessons):
            row, col = divmod(idx, cols)
            lid = lesson["id"]
            unlocked = lm.is_unlocked(lid)
            done = lid in completed
            best = pt.get_lesson_best(lid)
            self._make_lesson_card(
                self._lesson_inner, lesson, unlocked, done, best, row, col)

    def _make_lesson_card(self, parent, lesson, unlocked, done, best, row, col):
        lid = lesson["id"]
        card = tk.Frame(parent, bg=theme.BG_PANEL, cursor="hand2" if unlocked else "")
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        # Category badge
        cat = lesson.get("category", "")
        cat_colours = {
            "Beginner":     ("#1b5e20", "#4caf50"),
            "Intermediate": ("#0d47a1", "#42a5f5"),
            "Advanced":     ("#4a148c", "#ce93d8"),
        }
        bg_c, fg_c = cat_colours.get(cat, ("#333", "#aaa"))
        badge = tk.Frame(card, bg=bg_c)
        badge.pack(fill="x")
        tk.Label(badge, text=cat, bg=bg_c, fg=fg_c,
                 font=theme.FONT_SMALL).pack(side="left", padx=6, pady=2)

        if done:
            tk.Label(badge, text="✓ Done", bg=bg_c, fg=theme.CORRECT,
                     font=theme.FONT_SMALL).pack(side="right", padx=6, pady=2)
        elif not unlocked:
            tk.Label(badge, text="🔒 Locked", bg=bg_c, fg=theme.TEXT_MUTED,
                     font=theme.FONT_SMALL).pack(side="right", padx=6, pady=2)

        inner = tk.Frame(card, bg=theme.BG_PANEL)
        inner.pack(fill="both", padx=10, pady=8)

        # Lesson number + title
        tk.Label(inner,
                 text=f"Lesson {lid}",
                 bg=theme.BG_PANEL, fg=theme.TEXT_SECOND,
                 font=theme.FONT_SMALL).pack(anchor="w")
        tk.Label(inner,
                 text=lesson["title"],
                 bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY,
                 font=theme.FONT_HEADING,
                 wraplength=200, justify="left").pack(anchor="w")
        tk.Label(inner,
                 text=lesson.get("description", ""),
                 bg=theme.BG_PANEL, fg=theme.TEXT_SECOND,
                 font=theme.FONT_SMALL,
                 wraplength=200, justify="left").pack(anchor="w", pady=(2, 6))

        # Targets
        targets = tk.Frame(inner, bg=theme.BG_PANEL)
        targets.pack(fill="x", pady=(0, 4))
        tk.Label(targets, text=f"Target: {lesson['target_wpm']} WPM",
                 bg=theme.BG_PANEL, fg=theme.ACCENT,
                 font=theme.FONT_SMALL).pack(side="left", padx=(0, 8))
        tk.Label(targets, text=f"{lesson['target_accuracy']}% acc",
                 bg=theme.BG_PANEL, fg=theme.ACCENT,
                 font=theme.FONT_SMALL).pack(side="left")

        if done and best["wpm"] > 0:
            tk.Label(inner,
                     text=f"Best: {best['wpm']:.0f} WPM  {best['accuracy']:.0f}%",
                     bg=theme.BG_PANEL, fg=theme.CORRECT,
                     font=theme.FONT_SMALL).pack(anchor="w")

        # Start button
        if unlocked:
            btn = tk.Button(
                inner,
                text="Start" if not done else "Retry",
                bg=theme.ACCENT if not done else theme.BG_CARD,
                fg="#ffffff",
                activebackground=theme.ACCENT_HOVER,
                activeforeground="#ffffff",
                font=theme.FONT_BODY,
                bd=0, relief="flat",
                cursor="hand2",
                padx=14, pady=4,
                command=lambda lid=lid: self.app.start_lesson(lid),
            )
            btn.pack(anchor="w", pady=(4, 0))
        else:
            tk.Label(inner,
                     text=f"Complete lesson {lid-1} to unlock",
                     bg=theme.BG_PANEL, fg=theme.TEXT_MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w", pady=(4, 0))
