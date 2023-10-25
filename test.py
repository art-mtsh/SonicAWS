import time
from datetime import datetime
from multiprocessing import Process, Manager
import requests
import telebot
# from screenshoter import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

message = ("12321 \t1212\n"
          "122 \t1\n"
          "323412 \t233")

bot1.send_message(662482931, message)