"""
Lesson frame: instruction view + typing exercise with real-time feedback.
"""
import tkinter as tk
from tkinter import ttk
import theme
from ui.keyboard_widget import KeyboardWidget


class LessonFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="TFrame")
        self._lesson = None
        self._exercise_index = 0
        self._active = False
        self._after_id = None
        self._build()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x", padx=24, pady=(16, 8))

        ttk.Button(top, text="← Home", style="Ghost.TButton",
                   command=self._go_home).pack(side="left")

        self._title_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self._title_var,
                  style="Heading.TLabel").pack(side="left", padx=16)

        # Lesson nav buttons
        nav = ttk.Frame(top, style="TFrame")
        nav.pack(side="right")
        self._prev_btn = ttk.Button(nav, text="◀ Prev Exercise",
                                    style="Ghost.TButton",
                                    command=self._prev_exercise)
        self._prev_btn.pack(side="left", padx=4)
        self._next_btn = ttk.Button(nav, text="Next Exercise ▶",
                                    style="Ghost.TButton",
                                    command=self._next_exercise)
        self._next_btn.pack(side="left", padx=4)

        ttk.Separator(self).pack(fill="x", padx=24, pady=4)

        # Instruction card
        self._instr_frame = tk.Frame(self, bg=theme.BG_PANEL)
        self._instr_frame.pack(fill="x", padx=24, pady=4)
        self._instr_var = tk.StringVar(value="")
        tk.Label(self._instr_frame,
                 textvariable=self._instr_var,
                 bg=theme.BG_PANEL, fg=theme.TEXT_SECOND,
                 font=theme.FONT_BODY,
                 wraplength=900, justify="left").pack(
                     anchor="w", padx=16, pady=10)

        # Stats row
        stats_row = ttk.Frame(self, style="TFrame")
        stats_row.pack(fill="x", padx=24, pady=4)

        self._wpm_var = tk.StringVar(value="0")
        self._acc_var = tk.StringVar(value="100%")
        self._err_var = tk.StringVar(value="0")
        self._prog_var = tk.StringVar(value="0%")

        for var, lbl, col in [
            (self._wpm_var,  "WPM",      0),
            (self._acc_var,  "Accuracy", 1),
            (self._err_var,  "Errors",   2),
            (self._prog_var, "Progress", 3),
        ]:
            cell = ttk.Frame(stats_row, style="Card.TFrame")
            cell.grid(row=0, column=col, padx=6, sticky="ew")
            stats_row.columnconfigure(col, weight=1)
            ttk.Label(cell, textvariable=var, style="StatSm.TLabel").pack(pady=(6, 0))
            ttk.Label(cell, text=lbl, style="StatLbl.TLabel").pack(pady=(0, 6))

        # Progress bar
        self._progress_bar = ttk.Progressbar(
            self, style="Accent.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate", maximum=100)
        self._progress_bar.pack(fill="x", padx=24, pady=4)

        # Typing text area
        txt_frame = tk.Frame(self, bg=theme.BG_INPUT)
        txt_frame.pack(fill="both", padx=24, pady=8)

        self._text_widget = tk.Text(
            txt_frame,
            font=theme.FONT_TYPE,
            bg=theme.BG_INPUT,
            fg=theme.PENDING,
            insertbackground=theme.ACCENT,
            wrap="word",
            cursor="none",
            state="disabled",
            relief="flat",
            bd=0,
            padx=20, pady=20,
            height=5,
        )
        self._text_widget.pack(fill="both")

        # Tags for coloring
        self._text_widget.tag_configure("correct",   foreground=theme.CORRECT)
        self._text_widget.tag_configure("incorrect", foreground=theme.INCORRECT,
                                        underline=True)
        self._text_widget.tag_configure("current",   background=theme.CURRENT_BG,
                                        foreground=theme.CURRENT_FG)
        self._text_widget.tag_configure("pending",   foreground=theme.PENDING)

        # Keyboard widget
        kb_frame = ttk.Frame(self, style="TFrame")
        kb_frame.pack(pady=8)
        self._keyboard = KeyboardWidget(kb_frame)
        self._keyboard.pack()

        # Bottom buttons
        bottom = ttk.Frame(self, style="TFrame")
        bottom.pack(pady=10)
        ttk.Button(bottom, text="Restart Exercise", style="Secondary.TButton",
                   command=self._restart_exercise,
                   **theme.BTN_PAD).pack(side="left", padx=6)
        self._skip_btn = ttk.Button(bottom, text="Skip to Next Lesson →",
                                    style="Ghost.TButton",
                                    command=self._skip_lesson)
        self._skip_btn.pack(side="left", padx=6)

        # Key bindings — capture from parent window
        self._bindings = []

    # ── Load / navigate ───────────────────────────────────────────────────────

    def load_lesson(self, lesson: dict):
        self._lesson = lesson
        self._exercise_index = 0
        self._title_var.set(f"Lesson {lesson['id']}: {lesson['title']}")
        self._instr_var.set(lesson.get("instructions", ""))
        self._load_exercise()

    def _load_exercise(self):
        self._cancel_after()
        lm = self.app.lesson_manager
        text = lm.get_exercise_text(self._lesson, self._exercise_index)
        engine = self.app.engine
        engine.load_text(text)
        self._active = True
        self._render_text()
        self._update_stats()
        self._update_nav_buttons()
        if text:
            self._keyboard.highlight_key(text[0])

    def _render_text(self):
        engine = self.app.engine
        text = engine.target_text
        states = engine.get_char_states()
        tw = self._text_widget
        tw.config(state="normal")
        tw.delete("1.0", "end")
        for i, (ch, state) in enumerate(zip(text, states)):
            tw.insert("end", ch, state)
        tw.config(state="disabled")

    def _update_stats(self):
        engine = self.app.engine
        self._wpm_var.set(f"{engine.get_wpm():.0f}")
        self._acc_var.set(f"{engine.get_accuracy():.0f}%")
        self._err_var.set(str(len(engine.error_positions)))
        total = len(engine.target_text)
        pct = (engine.current_index / total * 100) if total else 0
        self._prog_var.set(f"{pct:.0f}%")
        self._progress_bar["value"] = pct

    def _update_nav_buttons(self):
        exercises = self._lesson.get("exercises", [])
        self._prev_btn.configure(
            state="normal" if self._exercise_index > 0 else "disabled")
        self._next_btn.configure(
            state="normal" if self._exercise_index < len(exercises) - 1 else "disabled")

    # ── Key handling ──────────────────────────────────────────────────────────

    def activate(self):
        """Bind keys when this frame is visible."""
        root = self.app.root
        self._bindings.append(root.bind("<Key>", self._on_key, add=True))

    def deactivate(self):
        """Unbind keys when leaving this frame."""
        root = self.app.root
        try:
            root.unbind("<Key>")
        except Exception:
            pass
        self._bindings.clear()
        self._cancel_after()
        self._active = False

    def _on_key(self, event):
        if not self._active:
            return
        engine = self.app.engine
        if engine.finished:
            return

        char = event.char
        keysym = event.keysym

        if keysym == "BackSpace":
            engine.process_backspace()
        elif keysym == "Escape":
            self._restart_exercise()
            return
        elif char and len(char) == 1:
            state = engine.process_key(char)
            if state["finished"]:
                self._on_exercise_complete()
        else:
            return

        self._render_text()
        self._update_stats()

        # Highlight next expected key
        idx = engine.current_index
        if idx < len(engine.target_text):
            self._keyboard.highlight_key(engine.target_text[idx])
        else:
            self._keyboard.clear()

    # ── Exercise complete ─────────────────────────────────────────────────────

    def _on_exercise_complete(self):
        self._active = False
        self._keyboard.clear()
        engine = self.app.engine
        results = engine.get_results()
        target = self._lesson.get("target_wpm", 0)
        target_acc = self._lesson.get("target_accuracy", 80)

        passed = (results["wpm"] >= target and results["accuracy"] >= target_acc)

        # Save progress for last exercise of the lesson
        exercises = self._lesson.get("exercises", [])
        is_last = self._exercise_index == len(exercises) - 1
        if is_last:
            self.app.progress.complete_lesson(
                self._lesson["id"],
                results["wpm"],
                results["accuracy"],
                results["total_chars"],
            )

        self._show_result_overlay(results, passed, is_last)

    def _show_result_overlay(self, results, passed, is_last):
        overlay = tk.Toplevel(self)
        overlay.title("Exercise Complete")
        overlay.configure(bg=theme.BG_PANEL)
        overlay.resizable(False, False)
        overlay.grab_set()

        # Centre over main window
        self.app.root.update_idletasks()
        rx = self.app.root.winfo_x() + self.app.root.winfo_width() // 2 - 220
        ry = self.app.root.winfo_y() + self.app.root.winfo_height() // 2 - 160
        overlay.geometry(f"440x320+{rx}+{ry}")

        status = "🎉 Exercise Complete!" if passed else "Exercise Complete"
        tk.Label(overlay, text=status,
                 bg=theme.BG_PANEL, fg=theme.CORRECT if passed else theme.ACCENT,
                 font=theme.FONT_TITLE).pack(pady=(20, 8))

        info = tk.Frame(overlay, bg=theme.BG_PANEL)
        info.pack(pady=8)
        for label, value in [
            ("WPM",      f"{results['wpm']:.1f}"),
            ("Accuracy", f"{results['accuracy']:.1f}%"),
            ("Errors",   str(results["errors"])),
        ]:
            row = tk.Frame(info, bg=theme.BG_PANEL)
            row.pack(fill="x", padx=30, pady=2)
            tk.Label(row, text=label, bg=theme.BG_PANEL,
                     fg=theme.TEXT_SECOND, font=theme.FONT_BODY,
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=theme.BG_PANEL,
                     fg=theme.TEXT_PRIMARY, font=theme.FONT_HEADING).pack(side="left")

        target = self._lesson.get("target_wpm", 0)
        t_acc  = self._lesson.get("target_accuracy", 80)
        if not passed:
            msg = f"Keep practicing! Target: {target} WPM, {t_acc}% accuracy"
            tk.Label(overlay, text=msg, bg=theme.BG_PANEL,
                     fg=theme.TEXT_SECOND, font=theme.FONT_SMALL).pack(pady=4)

        btn_row = tk.Frame(overlay, bg=theme.BG_PANEL)
        btn_row.pack(pady=16)

        tk.Button(btn_row, text="Retry",
                  bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY,
                  font=theme.FONT_BODY, bd=0, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=lambda: [overlay.destroy(), self._restart_exercise()]
                  ).pack(side="left", padx=6)

        exercises = self._lesson.get("exercises", [])
        if self._exercise_index < len(exercises) - 1:
            tk.Button(btn_row, text="Next Exercise →",
                      bg=theme.ACCENT, fg="#fff",
                      font=theme.FONT_BODY, bd=0, relief="flat",
                      padx=14, pady=6, cursor="hand2",
                      command=lambda: [overlay.destroy(), self._next_exercise()]
                      ).pack(side="left", padx=6)

        if is_last:
            next_lesson = self.app.lesson_manager.get_next_lesson(self._lesson["id"])
            if next_lesson:
                tk.Button(btn_row, text=f"Lesson {next_lesson['id']} →",
                          bg=theme.CORRECT, fg="#fff",
                          font=theme.FONT_BODY, bd=0, relief="flat",
                          padx=14, pady=6, cursor="hand2",
                          command=lambda: [overlay.destroy(),
                                           self.app.start_lesson(next_lesson["id"])]
                          ).pack(side="left", padx=6)
            tk.Button(btn_row, text="Home",
                      bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY,
                      font=theme.FONT_BODY, bd=0, relief="flat",
                      padx=14, pady=6, cursor="hand2",
                      command=lambda: [overlay.destroy(), self._go_home()]
                      ).pack(side="left", padx=6)

    # ── Navigation helpers ────────────────────────────────────────────────────

    def _prev_exercise(self):
        if self._exercise_index > 0:
            self._exercise_index -= 1
            self._load_exercise()

    def _next_exercise(self):
        exercises = self._lesson.get("exercises", [])
        if self._exercise_index < len(exercises) - 1:
            self._exercise_index += 1
            self._load_exercise()

    def _restart_exercise(self):
        self._load_exercise()

    def _skip_lesson(self):
        next_lesson = self.app.lesson_manager.get_next_lesson(self._lesson["id"])
        if next_lesson:
            self.app.start_lesson(next_lesson["id"])
        else:
            self._go_home()

    def _go_home(self):
        self.app.show_frame("home")

    def _cancel_after(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
