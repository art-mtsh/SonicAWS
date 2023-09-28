from requests import get
from multiprocessing import Process
import telebot
import time
from module_get_pairs_binance import binance_pairs
from datetime import datetime, timedelta


TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

binance_frame = '1m'
bybit_frame = '1'

price_filter = 100000
ticksize_filter = 100

atr_calculation_length = 0
history_lookback = 960
request_limit_length = 990


def calculation(instr, end_date):
	
	for symbol in instr:
		
		bin_timestamp = []
		byb_timestamp = []
		bin_open = []
		bin_high = []
		bin_low = []
		bin_close = []
		byb_open = []
		byb_high = []
		byb_low = []
		byb_close = []
		
		# # --- BINANCE DATA ---
		binance_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}'
		binance_klines = get(binance_klines)
		
		if binance_klines.status_code == 200:
			response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
	
			if response_length == request_limit_length:
				binance_candle_data = binance_klines.json()
				bin_timestamp = list(float(i[0]) for i in binance_candle_data)
				bin_open = list(float(i[1]) for i in binance_candle_data)
				bin_high = list(float(i[2]) for i in binance_candle_data)
				bin_low = list(float(i[3]) for i in binance_candle_data)
				bin_close = list(float(i[4]) for i in binance_candle_data)
		
		# --- BYBIT DATA ---
		bybit_klines = f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame}&limit={request_limit_length}&end={int(end_date)}'
		bybit_klines = get(bybit_klines)
		
		if bybit_klines.status_code == 200:
			bybit_candle_data = bybit_klines.json().get("result").get("list")
			response_length = len(bybit_candle_data) if bybit_candle_data != None else 0
			
			if response_length == request_limit_length:
				bybit_candle_data = bybit_klines.json().get("result").get("list")
				byb_timestamp = list(float(i[0]) for i in bybit_candle_data)[::-1]
				byb_open = list(float(i[1]) for i in bybit_candle_data)[::-1]
				byb_high = list(float(i[2]) for i in bybit_candle_data)[::-1]
				byb_low = list(float(i[3]) for i in bybit_candle_data)[::-1]
				byb_close = list(float(i[4]) for i in bybit_candle_data)[::-1]
				
		if len(bin_close) == request_limit_length and len(byb_close) == request_limit_length:
			# print(symbol)
			# print(f"{symbol}")
			# print(f"{byb_timestamp}")
			# print(f"{bin_timestamp}")
			# --- COUNTING DIVERGENCES ---
			divers = []
			for candle in range(history_lookback, 1, -1):
				# ==== binance ticksize ====
				# bin_all_ticks = list(bin_open[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(bin_high[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(bin_low[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(bin_close[-candle:-candle - atr_calculation_length:-1])
				# bin_all_ticks = sorted(bin_all_ticks)
				# bin_diffs = 10
				#
				# for u in range(0, len(bin_all_ticks) - 1):
				# 	if 0 < bin_all_ticks[-u] - bin_all_ticks[-u - 1] < bin_diffs:
				# 		bin_diffs = bin_all_ticks[-u] - bin_all_ticks[-u - 1]
				#
				# binance_tick_size = float('{:.4f}'.format(bin_diffs / (bin_close[-candle] / 100)))

				# ==== bybit ticksize ====
				# byb_all_ticks = list(byb_open[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(byb_high[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(byb_low[-candle:-candle - atr_calculation_length:-1]) + \
				#                 list(byb_close[-candle:-candle - atr_calculation_length:-1])
				# byb_all_ticks = sorted(byb_all_ticks)
				# byb_diffs = 10
				#
				# for e in range(0, len(byb_all_ticks) - 1):
				# 	if 0 < byb_all_ticks[-e] - byb_all_ticks[-e - 1] < byb_diffs:
				# 		byb_diffs = byb_all_ticks[-e] - byb_all_ticks[-e - 1]
				#
				# bybit_tick_size = float('{:.4f}'.format(byb_diffs / (byb_close[-candle] / 100)))

				# if binance_tick_size <= 0.06 and bybit_tick_size <= 0.06:
				# 	distance_per = abs(bin_close[-candle] - byb_close[-candle]) / (bin_close[-candle] / 100)
				# 	distance_per = float('{:.2f}'.format(distance_per))
				# 	divers.append(distance_per)
				if byb_timestamp[-candle] == bin_timestamp[-candle]:
					distance_per = abs(bin_close[-candle] - byb_close[-candle]) / (bin_close[-candle] / 100)
					distance_per = float('{:.2f}'.format(distance_per))
					divers.append(distance_per)
				else:
					print(f"{symbol} {byb_timestamp[-candle]} / {bin_timestamp[-candle]}")
			
			fee = 0.18
			spread = 0.14
			slippage = 0.3
			profit = 0.2
			alert = 0.6 #fee + spread + slippage + profit
			
			# trades = []
			# counter = 0
			# for d in range(0, len(divers)-1):
			# 	if d > alert and d == counter:
			# 		for e in range(d+1, len(divers)-1):
			# 			if d - e > alert:
			# 				trades.append(d - e)
			# 				counter = e+1
				
			# print(f"{symbol}: {divers}")
			if max(divers) - min(divers) >= 1.0 and len(set(divers)) >= 30:
				# print(f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}')
				# print(f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame}&limit={request_limit_length}&end={int(end_date)}')
				print(f"{symbol}, minimum divergence: {min(divers)}%, maximum divergence: {max(divers)}%, unique values: {len(set(divers))}/{len(divers)}")
				print(f"{symbol}", end=", ")
				for div in divers:
					print(str(div), end=", ")
					
				# # Calculate the minimum difference
				# min_difference = float('inf')  # Initialize with positive infinity
				#
				# for i in range(1, len(unique_sorted_list)):
				# 	difference = unique_sorted_list[i] - unique_sorted_list[i - 1]
				# 	if difference < min_difference:
				# 		min_difference = difference
				# print(f"Min step: {min_difference}")
				
				print("")
				
			# results = []
			#
			# for d in range(0, len(divers) - 1):
			# 	if divers[d] - divers[d + 1] >= alert:
			# 		results.append(abs(divers[d] - divers[d + 1]))
			#
			# if len(results) != 0:
			# 	print(f"{symbol} : {sum(results)} по сусіднім хвилинам")
			# 	print("")
				
		'''
		Розраховувати "чисту" дивергенцію в моменті (за мінусом комісій, тіксайзу і т.д.) - не має сенсу, бо
		нам важлива результуюча різниця між поточною дивергенцією (входу) і майбутньою дивергенцією (виходу)
		від ЯКОЇ ВЖЕ ми і будемо віднімати комісії і т.д.

		Різниця між дивергенцією входу і дивергенцією виходу має бути 0.11% + 0.08% = 0.19% - аби вийти в нуль.
		Усе, що далі - наш прибуток.
		'''

		# 		bot1.send_message(662482931, f"#{symbol}:\n"
		# 		      f"Current divergence: {current_clean}% > {divergence_filter}\n"
		# 		      f"{bin_close[-1]} - {bybClose[-1]} = {current_price_diff}\n"
		# 		      f"Divs ranges is: {min(divers)} --> {max(divers)}\n")
					

def search_activale(price_filter, ticksize_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.now().strftime('%H:%M:%S')}")
	
	threads = 16
	
	instr = binance_pairs(chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins: Price <= ${price_filter}, Tick <= {ticksize_filter}%")
	print("")
	
	
	
	for day in range(1, 31):
		print(f"Day {day}")
		print("")
		the_processes = []
		
		for i in range(threads):
			
			end_date_timestamp = datetime(2023, 8, day).timestamp()
			end_date = datetime.fromtimestamp(end_date_timestamp)
			hours_to_add = 20  # +++++++++++++++++++++++++
			minutes_to_add = 0  # +++++++++++++++++++++++++
			time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
			new_date = end_date + time_to_add
			end_date = new_date.timestamp() * 1000
			
			process = Process(target=calculation, args=(instr[i], end_date))
			the_processes.append(process)
		
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()

	time2 = time.perf_counter()
	time3 = time2 - time1
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.now().strftime('%H:%M:%S')}\n")


def waiting():
	while True:
		now = datetime.now()
		# last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M'))
		last_second_digit = int(now.strftime('%S'))
		time.sleep(0.1)
		if last_minute_digit % 15 == 0 and last_second_digit == 0:
			break
		# if last_hour_digit in list(range(8, 23)):


if __name__ == '__main__':
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
		)
		waiting()
