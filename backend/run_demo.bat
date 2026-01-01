@echo off
REM Run the integrated generator demo with virtual environment

echo ========================================
echo Integrated MIDI Generator Demo
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create it first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate venv and run demo
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running demo...
echo.

python examples\integrated_generator_demo.py

echo.
echo Demo complete!
pause
