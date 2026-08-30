@echo off
TITLE Haroon Tailor Shop Manager - Initializing...
color 0A

echo ===================================================
echo     HAROON TAILOR SHOP MANAGER - STARTUP SCRIPT
echo ===================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11+ and ensure "Add Python to PATH" is checked.
    pause
    exit /b
)

:: 2. Check if Node.js is installed
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js (v18+) for WhatsApp functionality.
    pause
    exit /b
)

:: 3. Setup Virtual Environment
IF NOT EXIST "venv" (
    echo [INFO] Creating Python Virtual Environment (this happens only once)...
    python -m venv venv
)

:: 4. Activate Virtual Environment
echo [INFO] Activating Virtual Environment...
call venv\Scripts\activate.bat

:: 5. Install Python Dependencies
echo [INFO] Checking Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python dependencies. Please check your internet connection.
    pause
    exit /b
)

:: 6. Install Node.js Dependencies (for WhatsApp)
IF NOT EXIST "node_modules" (
    echo [INFO] Installing WhatsApp dependencies (this happens only once, please wait)...
    call npm install
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install Node.js dependencies. WhatsApp might not work.
    )
)

:: 7. Start the Application
echo [INFO] Starting Haroon Tailor Application...
echo Please do not close this black window while using the app!
python main.py

:: 8. Deactivate when done
deactivate
exit
