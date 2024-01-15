import time
from datetime import datetime
from multiprocessing import Process, Manager
import requests
import telebot
# from modules import order_book, three_distances
# import sys
from get_pairsV4 import get_pairs
# from screenshoterV2 import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

DIV_TOKEN = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot2 = telebot.TeleBot(DIV_TOKEN)

def search(symbol, request_limit_length):

	while True:

		if int(datetime.now().strftime('%S')) in [10, 20, 30]:

			print(".")

			frame = "1m"
			market_type = "f"

			futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
			spot_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'

			url = futures_klines if market_type == "f" else spot_klines
			response = requests.get(url)

			if response.status_code == 200:

				response_length = len(response.json()) if response.json() != None else 0

				if response_length == request_limit_length:
					binance_candle_data = response.json()
					c_open = list(float(i[1]) for i in binance_candle_data)
					c_high = list(float(i[2]) for i in binance_candle_data)
					c_low = list(float(i[3]) for i in binance_candle_data)
					c_close = list(float(i[4]) for i in binance_candle_data)
					c_volume = list(float(i[5]) for i in binance_candle_data)
					trades = list(int(i[8]) for i in binance_candle_data)
					buy_volume = list(float(i[9]) for i in binance_candle_data)
					sell_volume = [c_volume[0] - buy_volume[0]]


					cumulative_delta = [int(buy_volume[0] - (c_volume[0] - buy_volume[0]))]
					for i in range(1, len(c_close)):
						b_vol = buy_volume[i]
						s_vol = c_volume[i] - buy_volume[i]
						new_delta = b_vol - s_vol
						new_delta = cumulative_delta[-1] + new_delta
						sell_volume.append(s_vol)
						cumulative_delta.append(int(new_delta))

					if c_high[-1] >= max(c_high[-1:-181:-1]) and cumulative_delta[-1] <= min(cumulative_delta[-1:-181:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BEARISH 180")  # , c_high[-3]: {c_high[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_high[-1] >= max(c_high[-1:-121:-1]) and cumulative_delta[-1] <= min(cumulative_delta[-1:-121:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BEARISH 120")  # c_high[-3]: {c_high[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_high[-1] >= max(c_high[-1:-61:-1]) and cumulative_delta[-1] <= min(cumulative_delta[-1:-61:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BEARISH 60")  # , c_high[-3]: {c_high[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_high[-1] >= max(c_high[-1:-31:-1]) and cumulative_delta[-1] <= min(cumulative_delta[-1:-31:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BEARISH 30")  # , c_high[-3]: {c_high[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_high[-1] >= max(c_high[-1:-11:-1]) and cumulative_delta[-1] <= min(cumulative_delta[-1:-11:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BEARISH 10")  # , c_high[-3]: {c_high[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")

					elif c_low[-1] <= min(c_low[-1:-181:-1]) and cumulative_delta[-1] >= max(cumulative_delta[-1:-181:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BULLISH 180")  # , c_low[-3]: {c_low[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_low[-1] <= min(c_low[-1:-121:-10]) and cumulative_delta[-1] >= max(cumulative_delta[-1:-121:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BULLISH 120")  # , c_low[-3]: {c_low[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_low[-1] <= min(c_low[-1:-61:-1]) and cumulative_delta[-1] >= max(cumulative_delta[-1:-61:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BULLISH 60")  # , c_low[-3]: {c_low[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_low[-1] <= min(c_low[-1:-31:-1]) and cumulative_delta[-1] >= max(cumulative_delta[-1:-31:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BULLISH 30")  # , c_low[-3]: {c_low[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")
					elif c_low[-1] <= min(c_low[-1:-11:-1]) and cumulative_delta[-1] >= max(cumulative_delta[-1:-11:-1]):
						bot2.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')} {symbol} BULLISH 10")  # , c_low[-3]: {c_low[-1]}: {int(buy_vol[-1])}, {int(sell_vol[-1])}")

					time.sleep(5)
		else:
			time.sleep(0.2)
		
if __name__ == '__main__':
	
	request_limit_length = 190
	pairs = get_pairs()
	print(pairs)
	print("")

	manager = Manager()
	shared_queue = manager.Queue()
	
	print(f"START at {datetime.now().strftime('%H:%M:%S')}, {len(pairs)} pairs")

	the_processes = []
	for pair in pairs:
		process = Process(target=search, args=(pair, request_limit_length,))
		the_processes.append(process)

	for pro in the_processes:
		pro.start()
	
	for pro in the_processes:
		pro.join()
		
	for pro in the_processes:
		pro.close()

	print("Process ended.")
		