@echo off
setlocal

REM ============================================================
REM Launch JupyterLab from the repository root using .venv.
REM ============================================================

cd /d "%~dp0.."
set "PROJECT_ROOT=%CD%"
set "VENV_DIR=%PROJECT_ROOT%\.venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] .venv was not found.
    echo Run scripts\setup_windows.bat first.
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Could not activate .venv.
    pause
    exit /b 1
)

 echo Starting JupyterLab from:
 echo %PROJECT_ROOT%
 echo.
python -m jupyter lab

endlocal
