# TypeFaster — Windows Typing Tutor

A lightweight, offline-first desktop typing tutor application for Windows, built with Python and tkinter. Improve your typing speed (WPM) and accuracy through structured lessons, timed tests, and real-time feedback.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Offline](https://img.shields.io/badge/Offline-First-brightgreen)

---

## Features

### Typing Lessons
- **15 structured lessons** progressing from Beginner → Intermediate → Advanced
- Sequential unlock system — complete a lesson to unlock the next
- Categories: Home Row keys → Full keyboard → Punctuation → Speed drills
- Each lesson includes instructions, multiple exercises, and target WPM/accuracy goals

### Timed Typing Tests
- Choose duration: **30s / 60s / 2 minutes**
- Random word pool or **custom text** input
- Live WPM counter updates as you type
- Results: WPM, Net WPM, Accuracy, Errors, and all-time best

### Real-Time Feedback
- Character-by-character color coding:
  - **Green** — correct keystroke
  - **Red** — incorrect keystroke (underlined)
  - **Yellow highlight** — current position cursor
- Backspace support with accurate error recalculation

### Virtual Keyboard
- Full QWERTY keyboard visualization
- **Finger-color zones** showing which finger to use for each key
- Active key highlights as you type

### Progress Tracking
- All stats saved locally to `~/.typefaster/progress.json`
- Tracks: Best WPM, average WPM, average accuracy, total sessions, chars typed
- Per-lesson best WPM and accuracy stored
- Full test history (last 100 tests)

### Settings
- Toggle sound effects
- Toggle keyboard visualization
- Font size selection (Small / Medium / Large)
- Reset all progress option

---

## Requirements

- **Python 3.10+** (uses `tkinter`, standard library only — no pip installs needed)
- **Windows 10 or later** (also runs on macOS/Linux with minor visual differences)

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/KASOZIDENIS/Type-faster.git
cd Type-faster

# Run directly
python main.py
```

Or on Windows, double-click **`run.bat`**.

---

## Build a Standalone EXE

To package as a single Windows executable (no Python installation required on the target machine):

```bash
# Install PyInstaller if needed
pip install pyinstaller

# Build (or just double-click build_exe.bat)
build_exe.bat
```

Output will be in `dist/TypeFaster/TypeFaster.exe`.

---

## Project Structure

```
Type-faster/
├── main.py                 # Entry point
├── app.py                  # Main app class & frame router
├── theme.py                # Dark theme — colors, fonts, ttk styles
├── run.bat                 # Windows launch script
├── build_exe.bat           # PyInstaller build script
│
├── core/
│   ├── typing_engine.py    # WPM/accuracy calculation, char-state tracking
│   ├── lesson_manager.py   # Lesson loading & sequential unlock logic
│   └── progress_tracker.py # JSON-based progress persistence
│
├── data/
│   └── lessons.json        # All 15 lesson definitions
│
└── ui/
    ├── home_frame.py       # Dashboard — stats strip & lesson grid
    ├── lesson_frame.py     # Lesson view — instructions & typing area
    ├── test_frame.py       # Timed typing test
    ├── progress_frame.py   # Stats overview & test history
    ├── settings_frame.py   # App settings
    └── keyboard_widget.py  # QWERTY canvas keyboard widget
```

---

## Lessons Overview

| # | Title | Category | Target WPM |
|---|-------|----------|------------|
| 1 | Home Row - Left Hand | Beginner | 10 |
| 2 | Home Row - Right Hand | Beginner | 10 |
| 3 | Full Home Row | Beginner | 12 |
| 4 | Adding E and I | Beginner | 14 |
| 5 | Adding T and N | Beginner | 15 |
| 6 | Adding R and O | Beginner | 16 |
| 7 | Top Row Introduction | Intermediate | 18 |
| 8 | Bottom Row Introduction | Intermediate | 18 |
| 9 | Common Words | Intermediate | 20 |
| 10 | Capital Letters | Intermediate | 20 |
| 11 | Numbers Row | Intermediate | 18 |
| 12 | Punctuation | Advanced | 22 |
| 13 | Full Sentences | Advanced | 25 |
| 14 | Speed Drill - Short Words | Advanced | 35 |
| 15 | Speed Drill - Paragraphs | Advanced | 40 |

---

## Data Storage

Progress is stored locally at:
```
C:\Users\<YourName>\.typefaster\
├── progress.json   # Lesson completion, WPM bests, test history
└── settings.json   # App preferences
```

No account, no internet, no telemetry.

---

## License

MIT License — free to use, modify, and distribute.
