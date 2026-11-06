@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3.11 -m venv .venv
if not exist .venv\Scripts\python.exe (
  echo Instal.la Python 3.11 i torna a executar aquest fitxer.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py
pause
