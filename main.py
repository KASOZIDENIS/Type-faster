"""
TypeFaster — Windows Typing Tutor
Entry point.
"""
import sys
import os

# Ensure the app root directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from app import TypingTutorApp


def main():
    root = tk.Tk()

    # High-DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # App icon (optional — silently skip if not found)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass

    app = TypingTutorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
