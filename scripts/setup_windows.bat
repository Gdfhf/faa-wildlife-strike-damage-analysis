@echo off
setlocal

REM ============================================================
REM FAA Wildlife Strike Damage Analysis - Windows Environment Setup
REM
REM Supported runtime: Python 3.12.x
REM Run this file from anywhere inside the repository.
REM It resolves the project root as the parent of this scripts folder.
REM ============================================================

cd /d "%~dp0.."

set "PROJECT_ROOT=%CD%"
set "VENV_DIR=%PROJECT_ROOT%\.venv"

echo.
echo ================================================
echo FAA Wildlife Strike - Environment Setup
echo Project: %PROJECT_ROOT%
echo Supported Python: 3.12.x
echo ================================================
echo.

REM ------------------------------------------------------------
REM Check Python launcher
REM ------------------------------------------------------------

where py >nul 2>nul

if errorlevel 1 (
    echo [ERROR] Python Launcher ^(py.exe^) was not found.
    echo.
    echo Install Python 3.12.x and ensure the Python Launcher
    echo is available, then rerun this script.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Check Python 3.12 specifically
REM ------------------------------------------------------------

py -3.12 --version >nul 2>nul

if errorlevel 1 (
    echo [ERROR] Python 3.12 was not found.
    echo.
    echo This project is tested and supported with Python 3.12.x.
    echo.
    echo Python installations currently detected:
    py -0p
    echo.
    echo Install Python 3.12.x and rerun this script.
    pause
    exit /b 1
)

echo [OK] Python 3.12 detected:
py -3.12 --version
echo.

REM ------------------------------------------------------------
REM Create virtual environment
REM ------------------------------------------------------------

if not exist "%VENV_DIR%\Scripts\python.exe" (

    echo [1/5] Creating .venv using Python 3.12...

    py -3.12 -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo.
        echo [ERROR] Could not create the Python 3.12 environment.
        pause
        exit /b 1
    )

) else (

    echo [1/5] Existing .venv found - checking Python version...

    "%VENV_DIR%\Scripts\python.exe" -c ^
    "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,12) else 1)"

    if errorlevel 1 (
        echo.
        echo [ERROR] Existing .venv was not created with Python 3.12.
        echo.
        echo Delete the following directory and rerun setup:
        echo %VENV_DIR%
        pause
        exit /b 1
    )

    echo Existing environment uses Python 3.12 - keeping it.
)

REM ------------------------------------------------------------
REM Use environment Python directly
REM ------------------------------------------------------------

echo [2/5] Verifying environment...
"%VENV_DIR%\Scripts\python.exe" --version

echo [3/5] Updating pip tooling...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel

if errorlevel 1 goto :install_error

echo [4/5] Installing project requirements...
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%PROJECT_ROOT%\requirements.txt"

if errorlevel 1 goto :install_error

REM ------------------------------------------------------------
REM Verify important dependencies
REM ------------------------------------------------------------

echo [5/5] Verifying project dependencies...

"%VENV_DIR%\Scripts\python.exe" -c ^
"import numpy,pandas,scipy,sklearn,xgboost,joblib,streamlit,plotly,shap; print('Core imports: OK')"

if errorlevel 1 goto :verify_error

echo.
echo ================================================
echo Setup completed successfully.
echo.
echo Environment:
echo %VENV_DIR%
echo.
"%VENV_DIR%\Scripts\python.exe" --version

echo.
echo Next:
echo   scripts\run_dashboard.bat
echo   scripts\run_jupyter.bat
echo ================================================
echo.

pause
exit /b 0

:install_error
echo.
echo [ERROR] Dependency installation failed.
echo Review the error above.
echo The existing environment has NOT been deleted.
echo.
pause
exit /b 1

:verify_error
echo.
echo [ERROR] Dependencies were installed, but one or more
echo required libraries could not be imported.
echo Review the error above.
echo.
pause
exit /b 1