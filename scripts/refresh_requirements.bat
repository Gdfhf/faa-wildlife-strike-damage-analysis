@echo off
setlocal

REM Reinstall/update packages using the repository requirements.txt.
REM This does not recreate the virtual environment.

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
python -m pip install --upgrade -r "%PROJECT_ROOT%\requirements.txt"

if errorlevel 1 (
    echo [ERROR] Requirements refresh failed.
    pause
    exit /b 1
)

 echo Requirements refreshed successfully.
pause
endlocal
