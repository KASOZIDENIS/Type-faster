"""
Virtual keyboard widget: shows QWERTY layout with finger-colour zones
and highlights the currently expected key.
"""
import tkinter as tk
from theme import (
    FINGER_LEFT_PINKY, FINGER_LEFT_RING, FINGER_LEFT_MIDDLE, FINGER_LEFT_INDEX,
    FINGER_RIGHT_INDEX, FINGER_RIGHT_MIDDLE, FINGER_RIGHT_RING, FINGER_RIGHT_PINKY,
    FINGER_THUMB, FINGER_NEUTRAL, BG_INPUT, TEXT_PRIMARY, CURRENT_BG,
)

# Key → finger colour
FINGER_MAP = {
    # Numbers row
    "`": FINGER_LEFT_PINKY,  "1": FINGER_LEFT_PINKY,
    "2": FINGER_LEFT_RING,   "3": FINGER_LEFT_MIDDLE,
    "4": FINGER_LEFT_INDEX,  "5": FINGER_LEFT_INDEX,
    "6": FINGER_RIGHT_INDEX, "7": FINGER_RIGHT_INDEX,
    "8": FINGER_RIGHT_MIDDLE,"9": FINGER_RIGHT_RING,
    "0": FINGER_RIGHT_PINKY, "-": FINGER_RIGHT_PINKY, "=": FINGER_RIGHT_PINKY,
    # Top row
    "q": FINGER_LEFT_PINKY,  "w": FINGER_LEFT_RING,
    "e": FINGER_LEFT_MIDDLE, "r": FINGER_LEFT_INDEX,  "t": FINGER_LEFT_INDEX,
    "y": FINGER_RIGHT_INDEX, "u": FINGER_RIGHT_INDEX,
    "i": FINGER_RIGHT_MIDDLE,"o": FINGER_RIGHT_RING,  "p": FINGER_RIGHT_PINKY,
    "[": FINGER_RIGHT_PINKY, "]": FINGER_RIGHT_PINKY, "\\": FINGER_RIGHT_PINKY,
    # Home row
    "a": FINGER_LEFT_PINKY,  "s": FINGER_LEFT_RING,
    "d": FINGER_LEFT_MIDDLE, "f": FINGER_LEFT_INDEX,  "g": FINGER_LEFT_INDEX,
    "h": FINGER_RIGHT_INDEX, "j": FINGER_RIGHT_INDEX,
    "k": FINGER_RIGHT_MIDDLE,"l": FINGER_RIGHT_RING,  ";": FINGER_RIGHT_PINKY,
    "'": FINGER_RIGHT_PINKY,
    # Bottom row
    "z": FINGER_LEFT_PINKY,  "x": FINGER_LEFT_RING,
    "c": FINGER_LEFT_MIDDLE, "v": FINGER_LEFT_INDEX,  "b": FINGER_LEFT_INDEX,
    "n": FINGER_RIGHT_INDEX, "m": FINGER_RIGHT_INDEX,
    ",": FINGER_RIGHT_MIDDLE,".": FINGER_RIGHT_RING,  "/": FINGER_RIGHT_PINKY,
    # Special
    " ": FINGER_THUMB,
}

# Shift-to-base mapping for capital / symbol characters
SHIFT_MAP = {
    "~": "`", "!": "1", "@": "2", "#": "3", "$": "4", "%": "5",
    "^": "6", "&": "7", "*": "8", "(": "9", ")": "0", "_": "-", "+": "=",
    "Q": "q", "W": "w", "E": "e", "R": "r", "T": "t",
    "Y": "y", "U": "u", "I": "i", "O": "o", "P": "p",
    "{": "[", "}": "]", "|": "\\",
    "A": "a", "S": "s", "D": "d", "F": "f", "G": "g",
    "H": "h", "J": "j", "K": "k", "L": "l", ":": ";", '"': "'",
    "Z": "z", "X": "x", "C": "c", "V": "v", "B": "b",
    "N": "n", "M": "m", "<": ",", ">": ".", "?": "/",
}

ROWS = [
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","⌫"],
    ["⇥","q","w","e","r","t","y","u","i","o","p","[","]","\\"],
    ["⇪","a","s","d","f","g","h","j","k","l",";","'","↵"],
    ["⇧","z","x","c","v","b","n","m",",",".","/","⇧"],
    ["SPACE"],
]

# Wide keys: (row_idx, col_idx) → width multiplier
WIDE = {
    (0, 13): 2.0,   # backspace
    (1,  0): 1.5,   # tab
    (1, 13): 1.5,   # backslash col
    (2,  0): 1.8,   # caps
    (2, 12): 2.2,   # enter
    (3,  0): 2.5,   # left shift
    (3, 11): 2.5,   # right shift
    (4,  0): 9.0,   # space
}

KEY_W = 38
KEY_H = 36
KEY_GAP = 4


class KeyboardWidget(tk.Canvas):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", BG_INPUT)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bd", 0)
        # Calculate canvas size
        total_w = int(14 * (KEY_W + KEY_GAP) + KEY_GAP + 10)
        total_h = int(5 * (KEY_H + KEY_GAP) + KEY_GAP + 10)
        kwargs.setdefault("width", total_w)
        kwargs.setdefault("height", total_h)
        super().__init__(parent, **kwargs)
        self._key_items: dict[str, int] = {}  # label → canvas rect id
        self._draw_keyboard()
        self._current_key = None

    def _draw_keyboard(self):
        x0, y0 = 6, 6
        for row_i, row in enumerate(ROWS):
            x = x0
            y = y0 + row_i * (KEY_H + KEY_GAP)
            if row_i == 4:  # space row — centre it
                x = x0 + int(3.5 * (KEY_W + KEY_GAP))
            for col_i, label in enumerate(row):
                mult = WIDE.get((row_i, col_i), 1.0)
                w = int(KEY_W * mult + KEY_GAP * (mult - 1))
                base = label.lower()
                colour = FINGER_MAP.get(base, FINGER_NEUTRAL)
                self._draw_key(x, y, w, KEY_H, label, colour)
                x += w + KEY_GAP

    def _draw_key(self, x, y, w, h, label, colour):
        r = 5  # corner radius
        rid = self._round_rect(x, y, x + w, y + h, r, fill=colour,
                               outline="#000000", width=1)
        tid = self.create_text(
            x + w // 2, y + h // 2,
            text=label,
            fill=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"),
        )
        key = label.lower()
        if label == "SPACE":
            key = " "
        elif label in ("⌫", "⇥", "⇪", "↵", "⇧"):
            key = label
        self._key_items[key] = (rid, tid, colour)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def highlight_key(self, char: str):
        """Highlight the key for the given character."""
        self._clear_highlight()
        if not char:
            return
        # Map shifted chars back to base key
        base = SHIFT_MAP.get(char, char.lower())
        if base == " ":
            base = " "
        self._set_highlight(base, CURRENT_BG)
        # If uppercase/symbol, also highlight shift
        if char in SHIFT_MAP:
            self._set_highlight("⇧", CURRENT_BG)
        self._current_key = base

    def _set_highlight(self, key: str, colour: str):
        items = self._key_items.get(key)
        if items:
            rid, tid, _ = items
            self.itemconfig(rid, fill=colour)
            self.itemconfig(tid, fill="#1a1a2e")

    def _clear_highlight(self):
        if self._current_key:
            # Restore left shift, right shift, and current key
            for k in (self._current_key, "⇧"):
                items = self._key_items.get(k)
                if items:
                    rid, tid, orig_colour = items
                    self.itemconfig(rid, fill=orig_colour)
                    self.itemconfig(tid, fill=TEXT_PRIMARY)
            self._current_key = None

    def clear(self):
        self._clear_highlight()
