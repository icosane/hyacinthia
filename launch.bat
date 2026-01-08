@echo off
cd "%~dp0"

echo Starting the application
echo Please wait
echo.

call ".venv\Scripts\activate.bat"
python main.py
pause

