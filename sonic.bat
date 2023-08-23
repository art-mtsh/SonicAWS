@echo off
mode con: cols=120 lines=30
call W:\TradingBots\venv\Scripts\activate
cd W:\TradingBots\Sonic\base.py
python base.py
pause
