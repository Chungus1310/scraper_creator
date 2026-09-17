@echo off
setlocal enabledelayedexpansion

title Kitten Scraper
echo ======================================================
echo           Kitten Scraper - Setup and Launch
echo ======================================================
echo.

cd /d "%~dp0"

:: 1. Clean previous lingering scraper or pythonw processes
echo [1/5] Cleaning up lingering processes and cache...
taskkill /F /FI "WINDOWTITLE eq Kitten Scraper*" >nul 2>&1

:: Clean bytecode cache
for /d /r %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d" >nul 2>&1
)

:: 2. Check Python availability
echo [2/5] Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not found in your PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

:: 3. Setup Virtual Environment
if not exist "venv\Scripts\python.exe" (
    echo [3/5] Creating virtual environment in .\venv ...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [3/5] Virtual environment is ready.
)

:: 4. Verify & Install Dependencies
echo [4/5] Checking dependencies from requirements.txt...
.\venv\Scripts\python.exe -c "import requests, docx, google.generativeai, ttkbootstrap, customtkinter" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing or updating dependencies...
    .\venv\Scripts\pip.exe install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install requirements!
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
) else (
    echo [SUCCESS] Dependencies already satisfied.
)

:: 5. Launch Application
echo [5/5] Launching Kitten Scraper...
echo ======================================================
echo Kitten Scraper is running. Close the app window to exit.
echo ======================================================
echo.

.\venv\Scripts\python.exe main.py

echo.
echo [INFO] Kitten Scraper exited.
pause
