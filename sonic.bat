@echo off
mode con: cols=120 lines=30
call W:\SonicAWS\venv\Scripts\activate
cd W:\SonicAWS\base.py
python base.py
pause
