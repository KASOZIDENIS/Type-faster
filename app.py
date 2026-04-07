"""
Main application class: manages frame navigation and shared state.
"""
import tkinter as tk
from tkinter import ttk

import theme
from core.typing_engine import TypingEngine
from core.lesson_manager import LessonManager
from core.progress_tracker import ProgressTracker
from ui.settings_frame import SettingsFrame, load_settings


class TypingTutorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()

        # Shared state
        self.engine   = TypingEngine()
        self.progress = ProgressTracker()
        self.lesson_manager = LessonManager(self.progress)

        # Apply saved settings
        self._settings = load_settings()

        # Apply theme
        theme.apply_theme(root)

        # Build frames (lazy-loaded on first show)
        self._frames: dict = {}
        self._current_frame_name: str | None = None

        # Show home on start
        self.show_frame("home")

    # ── Window configuration ──────────────────────────────────────────────────

    def _configure_root(self):
        self.root.title("TypeFaster — Typing Tutor")
        self.root.geometry("1100x760")
        self.root.minsize(900, 640)
        self.root.configure(bg="#1a1a2e")

        # Centre on screen
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Frame management ──────────────────────────────────────────────────────

    def _get_frame(self, name: str):
        if name not in self._frames:
            self._frames[name] = self._create_frame(name)
        return self._frames[name]

    def _create_frame(self, name: str):
        from ui.home_frame     import HomeFrame
        from ui.lesson_frame   import LessonFrame
        from ui.test_frame     import TestFrame
        from ui.progress_frame import ProgressFrame

        constructors = {
            "home":     lambda: HomeFrame(self.root, self),
            "lesson":   lambda: LessonFrame(self.root, self),
            "test":     lambda: TestFrame(self.root, self),
            "progress": lambda: ProgressFrame(self.root, self),
            "settings": lambda: SettingsFrame(self.root, self),
        }
        return constructors[name]()

    def show_frame(self, name: str):
        """Hide current frame, show the named one."""
        # Deactivate current
        if self._current_frame_name:
            old = self._frames.get(self._current_frame_name)
            if old:
                if hasattr(old, "deactivate"):
                    old.deactivate()
                old.pack_forget()

        frame = self._get_frame(name)
        frame.pack(fill="both", expand=True)
        self._current_frame_name = name

        # Activate / refresh
        if hasattr(frame, "activate"):
            frame.activate()
        if hasattr(frame, "refresh"):
            frame.refresh()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # ── Lesson navigation ─────────────────────────────────────────────────────

    def start_lesson(self, lesson_id: int):
        lesson = self.lesson_manager.get_lesson(lesson_id)
        if lesson is None:
            return
        if not self.lesson_manager.is_unlocked(lesson_id):
            return

        self.show_frame("lesson")
        lesson_frame = self._frames["lesson"]
        lesson_frame.load_lesson(lesson)

    # ── Settings ──────────────────────────────────────────────────────────────

    def apply_settings(self, settings: dict):
        self._settings = settings
        # Font size affects typing widget — rebuild frames that are affected
        for name in ("lesson", "test"):
            if name in self._frames:
                old = self._frames.pop(name)
                old.destroy()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _on_close(self):
        self.root.destroy()
