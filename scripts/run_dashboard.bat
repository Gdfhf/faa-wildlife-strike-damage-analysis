@echo off
setlocal

REM ============================================================
REM Launch the Streamlit dashboard using the repository .venv.
REM Expected entry point: dashboard\app.py
REM ============================================================

cd /d "%~dp0.."
set "PROJECT_ROOT=%CD%"
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "APP_FILE=%PROJECT_ROOT%\dashboard\app.py"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] .venv was not found.
    echo Run scripts\setup_windows.bat first.
    pause
    exit /b 1
)

if not exist "%APP_FILE%" (
    echo [ERROR] Dashboard entry point was not found:
    echo %APP_FILE%
    echo.
    echo Create dashboard\app.py before launching the app.
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Could not activate .venv.
    pause
    exit /b 1
)

 echo Starting Streamlit...
 echo Press Ctrl+C in this window to stop the dashboard.
 echo.
python -m streamlit run "%APP_FILE%"

endlocal
