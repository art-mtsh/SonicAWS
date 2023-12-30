import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot
from bbs.module_get_pairs_binanceV3 import binance_pairs
from screenshoter import screenshoter_send

'''

Donchian

'''


TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(
		filtered_symbols,
		frame,
		gap_filter,
		density_filter,
):

	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		# frame = "5m"
		request_limit_length = 100


		# ==== DATA REQUEST ====
		futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
		spot_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
		klines = requests.get(futures_klines)
		if klines.status_code == 200:
			response_length = len(klines.json()) if klines.json() != None else 0
			if response_length == request_limit_length:
				binance_candle_data = klines.json()
				open = list(float(i[1]) for i in binance_candle_data)
				high = list(float(i[2]) for i in binance_candle_data)
				low = list(float(i[3]) for i in binance_candle_data)
				close = list(float(i[4]) for i in binance_candle_data)
				volume = list(float(i[5]) for i in binance_candle_data)
				buy_volume = list(float(i[9]) for i in binance_candle_data)
				sell_volume = [volume[0] - buy_volume[0]]
				max_gap = 0

				# ==== GAP AND SELL VOLUME ====
				for curr_index in range(1, len(close)):
					gap = abs(open[curr_index] - close[curr_index - 1])
					gap_p = 0
					if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
					if gap_p > max_gap: max_gap = gap_p

					s_v = volume[curr_index] - buy_volume[curr_index]
					sell_volume.append(s_v)
				max_gap = float('{:.3f}'.format(max_gap))
				density = (high[-1] - low[-1]) / tick_size

				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and density >= density_filter and len(high) == len(low) == request_limit_length:

					atr_len = 30
					atr_mpl = 3
					risk = 0.2
					fee_perc = 0.09
					avg_atr = [high[-c] - low[-c] for c in range(atr_len)]
					avg_atr = sum(avg_atr) / len(avg_atr)
					super_atr = avg_atr * atr_mpl
					super_atr_perc = super_atr / (close[-1] / 100)
					super_atr_perc = float('{:.2f}'.format(super_atr_perc))
					super_atr_perc_fee = super_atr_perc + fee_perc
					size_dollars = risk / (super_atr_perc_fee / 100)

					donchian_list = []
					donchian_length = 30

					for i in range(1, 31):

						local_max = max(high[-i:-i-donchian_length:-1])
						local_min = min(low[-i:-i-donchian_length:-1])

						donchian_range = local_max - local_min
						donchian_list.append(donchian_range)

					current_donchian_range = donchian_list[0]
					minimal_donchian_range = min(donchian_list)

					if current_donchian_range >= minimal_donchian_range * 3 and (
						close[-1] >= (max(high[-1:-donchian_length:-1]) - current_donchian_range / 3)
						or
						close[-1] <= (min(low[-1:-donchian_length:-1]) + current_donchian_range / 3)
					):

						msg = (f"{symbol}, cur/min: {int(current_donchian_range/minimal_donchian_range)}, 3xATR {super_atr_perc}%, size ${int(size_dollars)}")# ({current_donchian_range}/{minimal_donchian_range})")

						bot1.send_message(662482931, msg)
						# screenshoter_send(symbol, open, high, low, close, f"{symbol} ({frame}), BBSh, density: {int(density)}")
						print(msg)

		elif klines.status_code == 418 or klines.status_code == 429:
			print(f"ERROR. Returned code: {klines.status_code} with {symbol}")
			print(futures_klines)

		else:
			print(f"Some shit happened with {symbol}!")

if __name__ == '__main__':
	# print("PARAMETERS:")

	# timeframes = []
	#
	# while True:
	# 	value = input("Frames: ")
	# 	if value.lower() == 's':
	# 		break
	# 	timeframes.append(value)

	proc = 16
	day_range_filter = 2
	density_filter = 25
	tick_size_filter = 0.05
	gap_filter = 0.5

	print("")

	# def waiting(timeframes):
	#
	# 	while True:
	# 		now = datetime.now()
	# 		last_hour_digit = int(now.strftime('%H'))
	# 		last_minute_digit = now.strftime('%M')
	# 		last_second_digit = now.strftime('%S')
	# 		time.sleep(0.1)
	#
	# 		# Перевірка в 04:20 , 05:20 , 06:20 ....
	# 		if "1m" in timeframes and (int(last_second_digit)) == 0:
	# 			return "1m"
	#
	# 		# Перевірка в 04:20 , 09:20 , 14:20 ....
	# 		if "5m" in timeframes and (int(last_minute_digit) + 1) % 5 == 0:
	# 			if int(last_second_digit) == 20:
	# 				return "5m"
	#
	# 		# Перевірка в 13:40 , 28:40 , 43:40 , 58:40
	# 		if "15m" in timeframes and (int(last_minute_digit) + 2) % 15 == 0:
	# 			if int(last_second_digit) == 40:
	# 				return "15m"
	#
	# 		# Перевірка в 28:00 , 58:00
	# 		if "30m" in timeframes and (int(last_minute_digit) + 2) % 30 == 0:
	# 			if int(last_second_digit) == 0:
	# 				return "30m"
	#
	# 		# Перевірка в 57:20
	# 		if "1h" in timeframes and (int(last_minute_digit) + 3) == 60:
	# 			if int(last_second_digit) == 20:
	# 				return "1h"
	#
	# 		# Перевірка в 16:56:40
	# 		if "2h" in timeframes and int(last_hour_digit) % 2 == 0:
	# 			if (int(last_minute_digit) + 4) == 60:
	# 				if int(last_second_digit) == 40:
	# 					return "2h"

	while True:


		frame = "1m"
		# frame = waiting(timeframes)
		time1 = time.perf_counter()

		pairs = binance_pairs(
			chunks=proc,
			quote_assets=["USDT"],
			day_range_filter=day_range_filter,
			day_density_filter=density_filter,
			tick_size_filter=tick_size_filter
		)

		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs on {frame}")
		print(f">>>")

		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search,
								args=(pairs[proc_number],
								frame,
								gap_filter,
								density_filter,
								)
							)
			the_processes.append(process)

		for pro in the_processes:
			pro.start()

		for pro in the_processes:
			pro.join()

		for pro in the_processes:
			pro.close()

		time2 = time.perf_counter()
		time3 = time2 - time1

		print(f"<<<")
		print(f"Finished search in {int(time3)} seconds")
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print("")

		time.sleep(30)