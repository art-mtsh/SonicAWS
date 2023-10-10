import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

symbol_status = True
symbol = "BTCUSDT"
frame = "1h"
pin_direction = True
total_range = 2.12
body_percent = 30
volume_scheme = "✅✅"
buy_volume_power = 49
sell_volume_power = 51
density_scheme = "✅✅"
density = 200

bot1.send_message(662482931, f"{'🟢' if symbol_status else '🔴'} #{symbol} ({frame})\n"
                             f"{'🟢' if pin_direction else '🔴'} pin: {total_range}% ({int(body_percent)}/100)\n"
                             f"{volume_scheme} volume, b_{buy_volume_power}/{sell_volume_power}_s\n"
                             f"{density_scheme} density ({int(density)})")