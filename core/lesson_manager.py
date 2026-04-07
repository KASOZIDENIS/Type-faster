"""
Lesson manager: loads lesson data from JSON and handles progression logic.
"""
import json
import os


LESSONS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lessons.json")


class LessonManager:
    def __init__(self, progress_tracker):
        self.progress = progress_tracker
        self.lessons = self._load_lessons()

    def _load_lessons(self) -> list:
        path = os.path.normpath(LESSONS_PATH)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["lessons"]

    def get_all_lessons(self) -> list:
        return self.lessons

    def get_lesson(self, lesson_id: int) -> dict | None:
        for lesson in self.lessons:
            if lesson["id"] == lesson_id:
                return lesson
        return None

    def is_unlocked(self, lesson_id: int) -> bool:
        """Lesson 1 is always unlocked; others unlock when previous is completed."""
        if lesson_id == 1:
            return True
        completed = self.progress.get_completed_lessons()
        return (lesson_id - 1) in completed

    def get_exercise_text(self, lesson: dict, exercise_index: int) -> str:
        exercises = lesson.get("exercises", [])
        if not exercises:
            return ""
        idx = exercise_index % len(exercises)
        return exercises[idx]

    def get_categories(self) -> list:
        seen = []
        for lesson in self.lessons:
            cat = lesson.get("category", "General")
            if cat not in seen:
                seen.append(cat)
        return seen

    def get_lessons_by_category(self, category: str) -> list:
        return [l for l in self.lessons if l.get("category") == category]

    def get_next_lesson(self, current_id: int) -> dict | None:
        for lesson in self.lessons:
            if lesson["id"] == current_id + 1:
                return lesson
        return None
