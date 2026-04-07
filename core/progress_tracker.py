"""
Progress tracker: persists user stats, lesson completion, and history to JSON.
"""
import json
import os
import time


PROGRESS_PATH = os.path.join(
    os.path.expanduser("~"), ".typefaster", "progress.json"
)


class ProgressTracker:
    def __init__(self):
        self._ensure_dir()
        self.data = self._load()

    def _ensure_dir(self):
        d = os.path.dirname(PROGRESS_PATH)
        os.makedirs(d, exist_ok=True)

    def _load(self) -> dict:
        if os.path.exists(PROGRESS_PATH):
            try:
                with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_data()

    def _default_data(self) -> dict:
        return {
            "completed_lessons": [],
            "lesson_bests": {},        # lesson_id -> {wpm, accuracy}
            "test_history": [],        # list of test result dicts
            "best_wpm": 0.0,
            "total_sessions": 0,
            "total_chars_typed": 0,
        }

    def save(self):
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # --- Lesson progress ---

    def get_completed_lessons(self) -> list:
        return self.data.get("completed_lessons", [])

    def complete_lesson(self, lesson_id: int, wpm: float, accuracy: float, chars: int):
        completed = self.data.setdefault("completed_lessons", [])
        if lesson_id not in completed:
            completed.append(lesson_id)

        bests = self.data.setdefault("lesson_bests", {})
        key = str(lesson_id)
        prev = bests.get(key, {"wpm": 0.0, "accuracy": 0.0})
        bests[key] = {
            "wpm": max(prev["wpm"], wpm),
            "accuracy": max(prev["accuracy"], accuracy),
        }

        self.data["total_chars_typed"] = self.data.get("total_chars_typed", 0) + chars
        self.data["best_wpm"] = max(self.data.get("best_wpm", 0.0), wpm)
        self.save()

    def get_lesson_best(self, lesson_id: int) -> dict:
        return self.data.get("lesson_bests", {}).get(str(lesson_id), {"wpm": 0.0, "accuracy": 0.0})

    # --- Test history ---

    def record_test(self, wpm: float, net_wpm: float, accuracy: float,
                    errors: int, duration: int, text_snippet: str = ""):
        result = {
            "timestamp": int(time.time()),
            "wpm": wpm,
            "net_wpm": net_wpm,
            "accuracy": accuracy,
            "errors": errors,
            "duration": duration,
            "text": text_snippet[:60],
        }
        history = self.data.setdefault("test_history", [])
        history.append(result)
        # Keep last 100 tests
        if len(history) > 100:
            self.data["test_history"] = history[-100:]

        self.data["best_wpm"] = max(self.data.get("best_wpm", 0.0), wpm)
        self.data["total_sessions"] = self.data.get("total_sessions", 0) + 1
        self.save()

    def get_test_history(self) -> list:
        return self.data.get("test_history", [])

    def get_best_wpm(self) -> float:
        return self.data.get("best_wpm", 0.0)

    def get_average_wpm(self) -> float:
        history = self.get_test_history()
        if not history:
            return 0.0
        return round(sum(r["wpm"] for r in history) / len(history), 1)

    def get_average_accuracy(self) -> float:
        history = self.get_test_history()
        if not history:
            return 0.0
        return round(sum(r["accuracy"] for r in history) / len(history), 1)

    def get_total_sessions(self) -> int:
        return self.data.get("total_sessions", 0)

    def get_total_chars(self) -> int:
        return self.data.get("total_chars_typed", 0)

    def reset_all(self):
        self.data = self._default_data()
        self.save()
