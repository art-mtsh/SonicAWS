import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

symbol_status = True
symbol = "BTCUSDT"
framt = "1h"
pin_direction
total_range
body_percent
volume_scheme
buy_volume_power
sell_volume_power
density_scheme
density

bot1.send_message(662482931, f"{'🟢' if symbol_status else '🔴'} #{symbol} ({frame})\n"
                             f"{'🟢' if pin_direction else '🔴'} pin: {total_range}% ({int(body_percent)}/100)\n"
                             f"{volume_scheme} volume, b.{buy_volume_power}/s.{sell_volume_power}\n"
                             f"{density_scheme} density ({int(density)})")