"""
Progress frame: displays stats summary, lesson completion, and test history.
"""
import tkinter as tk
from tkinter import ttk
import time
import theme


class ProgressFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="TFrame")
        self._build()

    def _build(self):
        # Top bar
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x", padx=24, pady=(16, 8))
        ttk.Button(top, text="← Home", style="Ghost.TButton",
                   command=lambda: self.app.show_frame("home")).pack(side="left")
        ttk.Label(top, text="Progress & Stats", style="Heading.TLabel").pack(
            side="left", padx=16)

        ttk.Separator(self).pack(fill="x", padx=24, pady=4)

        # Notebook: Overview / History
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=8)

        self._overview_tab = ttk.Frame(nb, style="TFrame")
        self._history_tab  = ttk.Frame(nb, style="TFrame")
        nb.add(self._overview_tab, text="Overview")
        nb.add(self._history_tab,  text="Test History")

        self._build_overview()
        self._build_history()

    # ── Overview tab ──────────────────────────────────────────────────────────

    def _build_overview(self):
        tab = self._overview_tab

        # Summary cards
        cards = ttk.Frame(tab, style="TFrame")
        cards.pack(fill="x", pady=10)

        self._ov_vars = {}
        stat_defs = [
            ("best_wpm",  "Best WPM",       "0"),
            ("avg_wpm",   "Avg WPM",        "0"),
            ("avg_acc",   "Avg Accuracy",   "0%"),
            ("sessions",  "Sessions",       "0"),
            ("total_chars","Total Chars",   "0"),
            ("lessons",   "Lessons Done",   "0 / ?"),
        ]
        for col, (key, label, default) in enumerate(stat_defs):
            cell = ttk.Frame(cards, style="Card.TFrame")
            cell.grid(row=0, column=col, padx=6, pady=10, sticky="ew")
            cards.columnconfigure(col, weight=1)
            var = tk.StringVar(value=default)
            self._ov_vars[key] = var
            ttk.Label(cell, textvariable=var, style="Stat.TLabel").pack(pady=(10, 0))
            ttk.Label(cell, text=label, style="StatLbl.TLabel").pack(pady=(0, 10))

        # Lesson progress bars
        ttk.Label(tab, text="Lesson Completion", style="Heading.TLabel").pack(
            anchor="w", pady=(8, 4))

        container = tk.Frame(tab, bg=theme.BG_ROOT)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=theme.BG_ROOT, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._lesson_list = ttk.Frame(canvas, style="TFrame")
        win = canvas.create_window((0, 0), window=self._lesson_list, anchor="nw")
        self._lesson_list.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    def _build_history(self):
        tab = self._history_tab

        # Header row
        hdr = ttk.Frame(tab, style="Card.TFrame")
        hdr.pack(fill="x", padx=0, pady=(4, 0))
        for col, (text, w) in enumerate([
            ("Date/Time", 18), ("WPM", 8), ("Net WPM", 8),
            ("Accuracy", 10), ("Errors", 8), ("Duration", 10),
        ]):
            tk.Label(hdr, text=text, width=w,
                     bg=theme.BG_CARD, fg=theme.TEXT_SECOND,
                     font=theme.FONT_SMALL,
                     anchor="w").grid(row=0, column=col, padx=6, pady=6, sticky="w")

        # Scrollable list
        container = tk.Frame(tab, bg=theme.BG_ROOT)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=theme.BG_ROOT, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._history_list = ttk.Frame(canvas, style="TFrame")
        win = canvas.create_window((0, 0), window=self._history_list, anchor="nw")
        self._history_list.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        pt = self.app.progress
        lm = self.app.lesson_manager
        all_lessons = lm.get_all_lessons()
        completed = pt.get_completed_lessons()

        self._ov_vars["best_wpm"].set(f"{pt.get_best_wpm():.0f}")
        self._ov_vars["avg_wpm"].set(f"{pt.get_average_wpm():.0f}")
        self._ov_vars["avg_acc"].set(f"{pt.get_average_accuracy():.0f}%")
        self._ov_vars["sessions"].set(str(pt.get_total_sessions()))
        total = pt.get_total_chars()
        self._ov_vars["total_chars"].set(
            f"{total//1000}k" if total >= 1000 else str(total))
        self._ov_vars["lessons"].set(f"{len(completed)} / {len(all_lessons)}")

        # Rebuild lesson bars
        for w in self._lesson_list.winfo_children():
            w.destroy()

        for lesson in all_lessons:
            lid = lesson["id"]
            done = lid in completed
            best = pt.get_lesson_best(lid)
            unlocked = lm.is_unlocked(lid)
            self._lesson_row(lesson, done, best, unlocked)

        # Rebuild history
        for w in self._history_list.winfo_children():
            w.destroy()

        history = list(reversed(pt.get_test_history()))
        if not history:
            ttk.Label(self._history_list,
                      text="No tests completed yet.",
                      style="Muted.TLabel").pack(pady=20)
        for record in history:
            self._history_row(record)

    def _lesson_row(self, lesson, done, best, unlocked):
        row = tk.Frame(self._lesson_list, bg=theme.BG_PANEL)
        row.pack(fill="x", padx=0, pady=2)

        # Status dot
        dot_colour = theme.CORRECT if done else (theme.PENDING if unlocked else theme.TEXT_MUTED)
        dot = tk.Label(row, text="●", bg=theme.BG_PANEL, fg=dot_colour,
                       font=theme.FONT_BODY)
        dot.grid(row=0, column=0, padx=(8, 4), pady=6)

        # Title
        tk.Label(row, text=f"Lesson {lesson['id']}: {lesson['title']}",
                 bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY if unlocked else theme.TEXT_MUTED,
                 font=theme.FONT_BODY, anchor="w", width=35).grid(
                     row=0, column=1, padx=4, pady=6, sticky="w")

        # Category
        tk.Label(row, text=lesson.get("category", ""),
                 bg=theme.BG_PANEL, fg=theme.TEXT_SECOND,
                 font=theme.FONT_SMALL, width=12).grid(row=0, column=2, padx=4)

        # Best WPM bar
        target = lesson.get("target_wpm", 30)
        pct = min(100, (best["wpm"] / target * 100)) if done else 0
        bar_frame = tk.Frame(row, bg=theme.BG_PANEL)
        bar_frame.grid(row=0, column=3, padx=8, pady=8, sticky="ew")
        row.columnconfigure(3, weight=1)

        bar_bg = tk.Frame(bar_frame, bg=theme.BG_CARD, height=8)
        bar_bg.pack(fill="x")
        if pct > 0:
            fill_w = max(4, int(pct * 2))
            tk.Frame(bar_bg, bg=theme.CORRECT if pct >= 100 else theme.ACCENT,
                     height=8, width=fill_w).place(x=0, y=0, relheight=1)

        if done:
            tk.Label(row, text=f"{best['wpm']:.0f} WPM  {best['accuracy']:.0f}%",
                     bg=theme.BG_PANEL, fg=theme.CORRECT,
                     font=theme.FONT_SMALL).grid(row=0, column=4, padx=8)
        elif not unlocked:
            tk.Label(row, text="Locked", bg=theme.BG_PANEL,
                     fg=theme.TEXT_MUTED, font=theme.FONT_SMALL).grid(
                         row=0, column=4, padx=8)

    def _history_row(self, record):
        ts = record.get("timestamp", 0)
        dt = time.strftime("%m/%d %H:%M", time.localtime(ts)) if ts else "-"
        wpm = f"{record['wpm']:.1f}"
        net = f"{record.get('net_wpm', record['wpm']):.1f}"
        acc = f"{record['accuracy']:.1f}%"
        errs = str(record.get("errors", 0))
        dur = f"{record.get('duration', 0)}s"

        row = tk.Frame(self._history_list, bg=theme.BG_PANEL)
        row.pack(fill="x", padx=0, pady=1)

        for col, (text, w) in enumerate([
            (dt, 18), (wpm, 8), (net, 8), (acc, 10), (errs, 8), (dur, 10),
        ]):
            tk.Label(row, text=text, width=w,
                     bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY,
                     font=theme.FONT_SMALL,
                     anchor="w").grid(row=0, column=col, padx=6, pady=4, sticky="w")
