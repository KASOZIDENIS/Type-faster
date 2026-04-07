"""
Settings frame: app preferences saved to ~/.typefaster/settings.json
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import theme


SETTINGS_PATH = os.path.join(
    os.path.expanduser("~"), ".typefaster", "settings.json"
)

DEFAULT_SETTINGS = {
    "sound_enabled": False,
    "keyboard_layout": "QWERTY",
    "show_keyboard": True,
    "font_size": "Large",
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                s = json.load(f)
                # Merge with defaults so new keys are always present
                merged = dict(DEFAULT_SETTINGS)
                merged.update(s)
                return merged
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


class SettingsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="TFrame")
        self.settings = load_settings()
        self._build()

    def _build(self):
        # Top bar
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x", padx=24, pady=(16, 8))
        ttk.Button(top, text="← Home", style="Ghost.TButton",
                   command=lambda: self.app.show_frame("home")).pack(side="left")
        ttk.Label(top, text="Settings", style="Heading.TLabel").pack(
            side="left", padx=16)

        ttk.Separator(self).pack(fill="x", padx=24, pady=4)

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=60, pady=20)

        # ── Sound ─────────────────────────────────────────────────────────────
        self._sound_var = tk.BooleanVar(value=self.settings["sound_enabled"])
        self._add_toggle(content, "Sound Effects",
                         "Play a sound on typing errors",
                         self._sound_var, row=0)

        # ── Keyboard vis ──────────────────────────────────────────────────────
        self._kb_var = tk.BooleanVar(value=self.settings["show_keyboard"])
        self._add_toggle(content, "Show Keyboard",
                         "Display virtual keyboard during lessons and tests",
                         self._kb_var, row=1)

        # ── Font size ─────────────────────────────────────────────────────────
        self._add_label_row(content, "Typing Font Size", row=2)
        font_row = ttk.Frame(content, style="TFrame")
        font_row.grid(row=3, column=0, columnspan=2, pady=(0, 16), sticky="w")
        self._font_var = tk.StringVar(value=self.settings["font_size"])
        for size in ("Small", "Medium", "Large"):
            ttk.Radiobutton(font_row, text=size,
                            variable=self._font_var, value=size).pack(
                                side="left", padx=8)

        # ── Keyboard layout ───────────────────────────────────────────────────
        self._add_label_row(content, "Keyboard Layout", row=4)
        layout_row = ttk.Frame(content, style="TFrame")
        layout_row.grid(row=5, column=0, columnspan=2, pady=(0, 16), sticky="w")
        self._layout_var = tk.StringVar(value=self.settings["keyboard_layout"])
        for layout in ("QWERTY",):   # only QWERTY in v1
            ttk.Radiobutton(layout_row, text=layout,
                            variable=self._layout_var, value=layout).pack(
                                side="left", padx=8)
        ttk.Label(layout_row, text="(more layouts in future versions)",
                  style="Muted.TLabel").pack(side="left", padx=8)

        # ── Data management ───────────────────────────────────────────────────
        ttk.Separator(content, orient="horizontal").grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=16)
        ttk.Label(content, text="Data Management",
                  style="Heading.TLabel").grid(row=7, column=0, columnspan=2,
                                               sticky="w", pady=(0, 8))

        btn_row = ttk.Frame(content, style="TFrame")
        btn_row.grid(row=8, column=0, columnspan=2, sticky="w")
        ttk.Button(btn_row, text="Reset All Progress",
                   style="Secondary.TButton",
                   command=self._reset_progress,
                   **theme.BTN_PAD).pack(side="left", padx=(0, 8))

        data_path = os.path.dirname(SETTINGS_PATH)
        ttk.Label(content, text=f"Data stored at: {data_path}",
                  style="Muted.TLabel").grid(row=9, column=0, columnspan=2,
                                              sticky="w", pady=(8, 0))

        # ── Save button ───────────────────────────────────────────────────────
        ttk.Separator(content, orient="horizontal").grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=16)
        ttk.Button(content, text="Save Settings",
                   style="Accent.TButton",
                   command=self._save,
                   **theme.BTN_PAD).grid(row=11, column=0, sticky="w")

    def _add_toggle(self, parent, title, subtitle, var, row):
        cell = ttk.Frame(parent, style="TFrame")
        cell.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
        text_col = ttk.Frame(cell, style="TFrame")
        text_col.pack(side="left", fill="x", expand=True)
        ttk.Label(text_col, text=title, style="Heading.TLabel").pack(anchor="w")
        ttk.Label(text_col, text=subtitle, style="Muted.TLabel").pack(anchor="w")
        ttk.Checkbutton(cell, variable=var).pack(side="right", padx=12)

    def _add_label_row(self, parent, text, row):
        ttk.Label(parent, text=text,
                  style="Heading.TLabel").grid(
                      row=row, column=0, columnspan=2, sticky="w", pady=(12, 2))

    def _save(self):
        self.settings["sound_enabled"]    = self._sound_var.get()
        self.settings["show_keyboard"]    = self._kb_var.get()
        self.settings["font_size"]        = self._font_var.get()
        self.settings["keyboard_layout"]  = self._layout_var.get()
        save_settings(self.settings)
        self.app.apply_settings(self.settings)
        messagebox.showinfo("Settings", "Settings saved!", parent=self)

    def _reset_progress(self):
        if messagebox.askyesno(
            "Reset Progress",
            "This will permanently delete all your progress, stats, and test history.\n\nAre you sure?",
            parent=self,
        ):
            self.app.progress.reset_all()
            messagebox.showinfo("Reset", "All progress has been reset.", parent=self)

    def get_settings(self) -> dict:
        return self.settings
