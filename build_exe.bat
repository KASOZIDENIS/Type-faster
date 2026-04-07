@echo off
echo TypeFaster - Build Standalone EXE
echo ==================================
cd /d "%~dp0"

:: Check PyInstaller is available
python -m pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

:: Clean previous build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build single-directory executable (faster startup than --onefile)
python -m pyinstaller ^
    --name "TypeFaster" ^
    --windowed ^
    --noconfirm ^
    --add-data "data;data" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.font" ^
    main.py

echo.
if exist dist\TypeFaster\TypeFaster.exe (
    echo Build SUCCESS: dist\TypeFaster\TypeFaster.exe
) else (
    echo Build FAILED - check output above
)
pause
