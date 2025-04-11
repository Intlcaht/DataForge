@echo off
:: Enable basic error handling
setlocal enabledelayedexpansion

:: Define the project directory (adjust if necessary)
set "PROJECT_DIR=app"

:: Check if the directory exists
if not exist "%PROJECT_DIR%" (
    echo Error: Directory '%PROJECT_DIR%' does not exist.
    pause
    exit /b 1
)

:: Navigate to the project directory
echo Changing directory to %PROJECT_DIR%...
cd /d "%PROJECT_DIR%"

:: Check if the virtual environment exists
set "VENV_PATH=venv\Scripts\activate.bat"
if not exist "%VENV_PATH%" (
    echo Error: Virtual environment not found in '%VENV_PATH%'.
    pause
    exit /b 1
)

:: Activate the virtual environment
echo Activating the virtual environment...
call "%VENV_PATH%"

:: Check if main.py exists
set "SCRIPT_PATH=main.py"
if not exist "%SCRIPT_PATH%" (
    echo Error: Script '%SCRIPT_PATH%' not found.
    pause
    exit /b 1
)

:: Run the Python script with Uvicorn directly to see logs
echo Starting FastAPI application...
echo ========================================
python -m uvicorn main:app --reload
echo ========================================
echo Application stopped.

:: Keep window open to see any error messages
pause