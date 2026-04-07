"""
Typing engine: tracks keypresses, calculates WPM and accuracy in real time.
"""
import time


class TypingEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.target_text = ""
        self.typed_chars = []       # list of (char, correct: bool)
        self.current_index = 0
        self.start_time = None
        self.end_time = None
        self.finished = False
        self.error_positions = set()

    def load_text(self, text: str):
        self.reset()
        self.target_text = text

    def start(self):
        """Call when the user starts typing (first keypress)."""
        if self.start_time is None:
            self.start_time = time.time()

    def process_key(self, char: str) -> dict:
        """
        Process a single character keypress.
        Returns a state dict with: index, correct, wpm, accuracy, finished.
        """
        if self.finished:
            return self._state()

        if self.start_time is None:
            self.start()

        expected = self.target_text[self.current_index]
        correct = (char == expected)

        self.typed_chars.append((char, correct))
        if not correct:
            self.error_positions.add(self.current_index)

        self.current_index += 1

        if self.current_index >= len(self.target_text):
            self.finished = True
            self.end_time = time.time()

        return self._state()

    def process_backspace(self) -> dict:
        """Undo the last character."""
        if self.current_index == 0 or self.finished:
            return self._state()

        self.current_index -= 1
        if self.typed_chars:
            self.typed_chars.pop()
        # Keep error_positions as-is (position stays wrong until retyped correctly)
        return self._state()

    def _state(self) -> dict:
        return {
            "index": self.current_index,
            "correct_count": self._correct_count(),
            "error_count": len(self.error_positions),
            "total_typed": len(self.typed_chars),
            "wpm": self.get_wpm(),
            "accuracy": self.get_accuracy(),
            "finished": self.finished,
        }

    def _correct_count(self) -> int:
        return sum(1 for _, ok in self.typed_chars if ok)

    def get_wpm(self) -> float:
        """Words per minute: (chars typed / 5) / minutes elapsed."""
        elapsed = self._elapsed()
        if elapsed < 0.5:
            return 0.0
        words = len(self.typed_chars) / 5.0
        minutes = elapsed / 60.0
        return round(words / minutes, 1)

    def get_accuracy(self) -> float:
        """Percentage of correctly typed characters."""
        total = len(self.typed_chars)
        if total == 0:
            return 100.0
        return round(self._correct_count() / total * 100, 1)

    def get_net_wpm(self) -> float:
        """Net WPM = gross WPM minus error penalty."""
        elapsed = self._elapsed()
        if elapsed < 0.5:
            return 0.0
        errors_per_minute = len(self.error_positions) / (elapsed / 60.0)
        gross = self.get_wpm()
        net = max(0.0, gross - errors_per_minute)
        return round(net, 1)

    def _elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_elapsed_seconds(self) -> float:
        return self._elapsed()

    def get_char_states(self) -> list:
        """
        Returns a list of states for each character in target_text:
        'correct', 'incorrect', 'current', 'pending'
        """
        states = []
        for i, ch in enumerate(self.target_text):
            if i < len(self.typed_chars):
                _, ok = self.typed_chars[i]
                states.append("correct" if ok else "incorrect")
            elif i == self.current_index:
                states.append("current")
            else:
                states.append("pending")
        return states

    def get_results(self) -> dict:
        return {
            "wpm": self.get_wpm(),
            "net_wpm": self.get_net_wpm(),
            "accuracy": self.get_accuracy(),
            "errors": len(self.error_positions),
            "correct": self._correct_count(),
            "total_chars": len(self.target_text),
            "elapsed_seconds": self._elapsed(),
        }
