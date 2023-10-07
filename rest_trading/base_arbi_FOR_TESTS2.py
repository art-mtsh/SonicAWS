from requests import get
from multiprocessing import Process
import telebot
import time
from module_get_pairs_binance import binance_pairs
from datetime import datetime, timedelta


TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

binance_frame = '1m'
bybit_frame = '1'

history_lookback = 720
request_limit_length = 750


def calculation(instr, end_date):
	
	for symbol in instr:
		
		bin_timestamp = []
		byb_timestamp = []
		bin_close = []
		byb_close = []
		
		# # --- BINANCE DATA ---
		binance_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}'
		binance_klines = get(binance_klines)
		
		if binance_klines.status_code == 200:
			response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
	
			if response_length == request_limit_length:
				binance_candle_data = binance_klines.json()
				bin_timestamp = list(float(i[0]) for i in binance_candle_data)
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
				byb_close = list(float(i[4]) for i in bybit_candle_data)[::-1]
				
		if len(bin_close) == request_limit_length and len(byb_close) == request_limit_length:
			divers = []
			for candle in range(history_lookback, 1, -1):
				if byb_timestamp[-candle] == bin_timestamp[-candle]:
					distance_per = abs(bin_close[-candle] - byb_close[-candle]) / (bin_close[-candle] / 100)
					distance_per = float('{:.2f}'.format(distance_per))
					divers.append(distance_per)
				# else:
				# 	print(f"{symbol} {byb_timestamp[-candle]} / {bin_timestamp[-candle]}")

			if max(divers) > 0.7 and (max(divers) - min(divers)) / len(set(divers)) <= 0.02:
				# print(f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}')
				# print(f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame}&limit={request_limit_length}&end={int(end_date)}')
				print(f"{symbol}, {min(divers)}% < {max(divers)}%, {len(set(divers))}/{len(divers)}", end=", ")
				for div in divers:
					print(str(div), end=", ")

		'''
		Розраховувати "чисту" дивергенцію в моменті (за мінусом комісій, тіксайзу і т.д.) - не має сенсу, бо
		нам важлива результуюча різниця між поточною дивергенцією (входу) і майбутньою дивергенцією (виходу)
		від ЯКОЇ ВЖЕ ми і будемо віднімати комісії і т.д.

		Різниця між дивергенцією входу і дивергенцією виходу має бути 0.11% + 0.08% = 0.19% - аби вийти в нуль.
		Усе, що далі - наш прибуток.
		'''


def search_activale():
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.now().strftime('%H:%M:%S')}")
	
	threads = 16
	
	
	instr = binance_pairs(chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins")
	
	time_of_day = [11, 23]
	
	for day in range(1, 31):
		print("")
		print(f"Day {day}")
		
		for hour in time_of_day:
			print(f"--------- till {hour} o'clock")
			the_processes = []
			
			for i in range(threads):
				
				end_date_timestamp = datetime(2023, 10, day).timestamp()
				end_date = datetime.fromtimestamp(end_date_timestamp)
				hours_to_add = hour  # +++++++++++++++++++++++++
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
				
			print("")

	time2 = time.perf_counter()
	time3 = time2 - time1
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.now().strftime('%H:%M:%S')}\n")


# def waiting():
# 	while True:
# 		now = datetime.now()
# 		# last_hour_digit = int(now.strftime('%H'))
# 		last_minute_digit = int(now.strftime('%M'))
# 		last_second_digit = int(now.strftime('%S'))
# 		time.sleep(0.1)
# 		if last_minute_digit % 15 == 0 and last_second_digit == 0:
# 			break


if __name__ == '__main__':
	# while True:
	search_activale()
	# waiting()
