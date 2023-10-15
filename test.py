import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def waiting_tf():
    while True:
        now = datetime.now()
        last_hour_digit = int(now.strftime('%H'))
        last_minute_digit = now.strftime('%M')
        last_second_digit = now.strftime('%S')
        time.sleep(0.1)
        
        # Перевірка в 04:20 , 09:20 , 14:20 ....
        if (int(last_minute_digit) + 1) % 5 == 0:
            if int(last_second_digit) == 20:
                return "5m"
            
        # Перевірка в 13:40 , 28:40 , 43:40 , 58:40
        if (int(last_minute_digit) + 2) % 15 == 0:
            if int(last_second_digit) == 40:
                return "15m"

        # Перевірка в 28:00 , 58:00
        if (int(last_minute_digit) + 2) % 30 == 0:
            if int(last_second_digit) == 0:
                return "30m"
    
        # Перевірка в 57:20
        if (int(last_minute_digit) + 3) == 60:
            if int(last_second_digit) == 20:
                return "1h"
            
        # Перевірка в 16:56:40
        if int(last_hour_digit) % 2 == 0:
            if (int(last_minute_digit) + 4) == 60:
                if int(last_second_digit) == 40:
                    return "2h"

while True:
    print("Start")
    timeframe = waiting_tf()
    print(timeframe)
    time.sleep(1)