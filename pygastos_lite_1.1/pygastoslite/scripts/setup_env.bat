@echo off
IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
)
call .venv\Scripts\activate.bat
IF EXIST "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
    echo Requirements installed.
)
