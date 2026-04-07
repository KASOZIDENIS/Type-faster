"""
Visual theme constants for the TypeFaster application.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


# ── Palette ──────────────────────────────────────────────────────────────────
BG_ROOT      = "#1a1a2e"   # main window background
BG_PANEL     = "#16213e"   # side panels / cards
BG_CARD      = "#0f3460"   # card surfaces
BG_INPUT     = "#0d0d1a"   # typing text background

ACCENT       = "#e94560"   # primary accent (red-pink)
ACCENT_HOVER = "#c73652"
ACCENT_ALT   = "#533483"   # secondary accent (purple)

TEXT_PRIMARY  = "#eaeaea"
TEXT_SECOND   = "#8888aa"
TEXT_MUTED    = "#555577"

CORRECT      = "#4caf50"   # green
INCORRECT    = "#f44336"   # red
CURRENT_BG   = "#ffeb3b"   # yellow cursor highlight
CURRENT_FG   = "#1a1a2e"
PENDING      = "#6666aa"   # not yet typed

# Finger colours (keyboard visualisation)
FINGER_LEFT_PINKY  = "#9c27b0"
FINGER_LEFT_RING   = "#2196f3"
FINGER_LEFT_MIDDLE = "#4caf50"
FINGER_LEFT_INDEX  = "#ff9800"
FINGER_RIGHT_INDEX = "#ff9800"
FINGER_RIGHT_MIDDLE= "#4caf50"
FINGER_RIGHT_RING  = "#2196f3"
FINGER_RIGHT_PINKY = "#9c27b0"
FINGER_THUMB       = "#607d8b"
FINGER_NEUTRAL     = "#2a2a4a"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_FAMILY_UI   = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_TITLE   = (FONT_FAMILY_UI,   22, "bold")
FONT_HEADING = (FONT_FAMILY_UI,   14, "bold")
FONT_BODY    = (FONT_FAMILY_UI,   11)
FONT_SMALL   = (FONT_FAMILY_UI,    9)
FONT_TYPE    = (FONT_FAMILY_MONO, 18)   # typing text
FONT_TYPE_SM = (FONT_FAMILY_MONO, 14)
FONT_STAT    = (FONT_FAMILY_UI,   28, "bold")
FONT_STAT_SM = (FONT_FAMILY_UI,   16, "bold")

# ── Button style helper ───────────────────────────────────────────────────────
BTN_PAD = {"padding": (18, 8)}


def apply_theme(root: tk.Tk):
    """Configure ttk styles and root background."""
    root.configure(bg=BG_ROOT)
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frame / LabelFrame
    style.configure("TFrame",      background=BG_ROOT)
    style.configure("Card.TFrame", background=BG_PANEL)
    style.configure("Dark.TFrame", background=BG_INPUT)

    # Labels
    style.configure("TLabel",
                    background=BG_ROOT,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)
    style.configure("Title.TLabel",
                    background=BG_ROOT,
                    foreground=TEXT_PRIMARY,
                    font=FONT_TITLE)
    style.configure("Heading.TLabel",
                    background=BG_ROOT,
                    foreground=TEXT_PRIMARY,
                    font=FONT_HEADING)
    style.configure("Muted.TLabel",
                    background=BG_ROOT,
                    foreground=TEXT_SECOND,
                    font=FONT_BODY)
    style.configure("Stat.TLabel",
                    background=BG_PANEL,
                    foreground=ACCENT,
                    font=FONT_STAT)
    style.configure("StatSm.TLabel",
                    background=BG_PANEL,
                    foreground=ACCENT,
                    font=FONT_STAT_SM)
    style.configure("StatLbl.TLabel",
                    background=BG_PANEL,
                    foreground=TEXT_SECOND,
                    font=FONT_SMALL)
    style.configure("Card.TLabel",
                    background=BG_PANEL,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)
    style.configure("CardH.TLabel",
                    background=BG_PANEL,
                    foreground=TEXT_PRIMARY,
                    font=FONT_HEADING)

    # Buttons
    style.configure("Accent.TButton",
                    background=ACCENT,
                    foreground="#ffffff",
                    font=FONT_HEADING,
                    borderwidth=0,
                    focusthickness=0,
                    relief="flat")
    style.map("Accent.TButton",
              background=[("active", ACCENT_HOVER), ("disabled", "#444466")],
              foreground=[("disabled", "#888888")])

    style.configure("Secondary.TButton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY,
                    borderwidth=0,
                    relief="flat")
    style.map("Secondary.TButton",
              background=[("active", ACCENT_ALT)])

    style.configure("Ghost.TButton",
                    background=BG_ROOT,
                    foreground=TEXT_SECOND,
                    font=FONT_BODY,
                    borderwidth=0,
                    relief="flat")
    style.map("Ghost.TButton",
              background=[("active", BG_PANEL)],
              foreground=[("active", TEXT_PRIMARY)])

    # Separator
    style.configure("TSeparator", background=BG_CARD)

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=BG_CARD,
                    troughcolor=BG_ROOT,
                    borderwidth=0,
                    arrowsize=0)

    # Notebook (tabs)
    style.configure("TNotebook",
                    background=BG_ROOT,
                    borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BG_PANEL,
                    foreground=TEXT_SECOND,
                    padding=[12, 6],
                    font=FONT_BODY)
    style.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", TEXT_PRIMARY)])

    # Progressbar
    style.configure("Accent.Horizontal.TProgressbar",
                    troughcolor=BG_PANEL,
                    background=ACCENT,
                    borderwidth=0,
                    thickness=8)
    style.configure("Green.Horizontal.TProgressbar",
                    troughcolor=BG_PANEL,
                    background=CORRECT,
                    borderwidth=0,
                    thickness=8)
