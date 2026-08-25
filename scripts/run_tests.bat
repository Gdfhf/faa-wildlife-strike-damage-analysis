@echo off
echo ==========================================
echo CAPSTONE AIRSTRIKE - RUNNING TESTS
echo ==========================================
echo.

python -m pytest tests -v --tb=short

echo.
echo ==========================================
echo TEST RUN COMPLETE
echo ==========================================
pause