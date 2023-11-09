import time
from datetime import datetime
from multiprocessing import Process, Manager
import requests
import telebot

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def extremum(symbol, frame, request_limit_length):
	futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
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
			trades = list(int(i[8]) for i in binance_candle_data)
			buy_volume = list(float(i[9]) for i in binance_candle_data)
			sell_volume = [volume[0] - buy_volume[0]]
			
			return [max(high), min(low)]
		
	else:
		print(f"TROUBLES WITH {symbol} DATA")
		
	
def search(
		symbol,
		reload_time,
		display_on_tg,
		request_limit_length,
		search_distance,
		max_minimum_candle,
		multiplier,
):
	
	while True:
		
		# ==== DATA REQUEST ====
		order_book = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit={request_limit_length}"
		response = requests.get(order_book)
		response.raise_for_status()
		
		if response.status_code != 200:
			print(f"Received status code: {response.status_code}")
			
		else:
			response_data = response.json()
	
			bids = response_data.get('bids')
			asks = response_data.get('asks')
			close = float(asks[0][0])
			
			combined_list = bids + asks
			combined_list = list(combined_list)
			combined_list = [[float(item[0]), float(item[1])] for item in combined_list]
			combined_list = sorted(combined_list, key=lambda x: x[1])
			
			decimal_1 = len(str(combined_list[12][0]).split('.')[-1].rstrip('0'))
			decimal_2 = len(str(combined_list[34][0]).split('.')[-1].rstrip('0'))
			decimal_3 = len(str(combined_list[23][0]).split('.')[-1].rstrip('0'))
			max_decimal = max([decimal_1, decimal_2, decimal_3])
		
			distance_1 = abs(close - combined_list[-1][0]) / (close / 100) if combined_list[-1][1] >= combined_list[-max_minimum_candle][1] * multiplier else 100
			distance_2 = abs(close - combined_list[-2][0]) / (close / 100) if combined_list[-2][1] >= combined_list[-max_minimum_candle][1] * multiplier else 100
			distance_3 = abs(close - combined_list[-3][0]) / (close / 100) if combined_list[-3][1] >= combined_list[-max_minimum_candle][1] * multiplier else 100
			
			distance_1 = float('{:.2f}'.format(distance_1))
			distance_2 = float('{:.2f}'.format(distance_2))
			distance_3 = float('{:.2f}'.format(distance_3))

			
			if min([distance_1, distance_2, distance_3]) <= search_distance:
				
				minimum_dist = min([distance_1, distance_2, distance_3])
				
				if minimum_dist <= search_distance / 4:
					dist_marker = "🟩 "
				elif minimum_dist <= search_distance / 4 * 2:
					dist_marker = "🟨 "
				elif minimum_dist <= search_distance / 4 * 3:
					dist_marker = "🟧 "
				else:
					dist_marker = "🟥 "
					
				if distance_1 == minimum_dist:
					
					distance = distance_1
					decimal_x = len(str(combined_list[-1][0]).split('.')[-1].rstrip('0'))
					size_price = combined_list[-1][0]
					size_in_thousands = int(combined_list[-1][1] / 1000)
					size_in_dollars = int((combined_list[-1][0] * combined_list[-1][1]) / 1000)
					zero_addition = (max_decimal-decimal_x)*'0'
					last_size_in_thousands = int(combined_list[-max_minimum_candle][1] / 1000)
					msg = (f"\n{distance}% {symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K \n"
					      f"{size_in_thousands}K > {last_size_in_thousands}K")
					
					max_min = extremum(symbol, '1m', 10)
					max_of_range = max_min[0]
					min_of_range = max_min[1]
					
					if size_price >= max_of_range and min_of_range >= size_price:
						print(msg)
						if display_on_tg == 1: bot1.send_message(662482931, dist_marker+msg)
	
				elif distance_2 == minimum_dist:
					
					distance = distance_2
					decimal_x = len(str(combined_list[-2][0]).split('.')[-1].rstrip('0'))
					size_price = combined_list[-2][0]
					size_in_thousands = int(combined_list[-2][1] / 1000)
					size_in_dollars = int((combined_list[-2][0] * combined_list[-2][1]) / 1000)
					zero_addition = (max_decimal - decimal_x) * '0'
					last_size_in_thousands = int(combined_list[-max_minimum_candle][1] / 1000)
					msg = (f"\n{distance}% {symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K \n"
					      f"{size_in_thousands}K > {last_size_in_thousands}K")
					
					max_min = extremum(symbol, '1m', 10)
					max_of_range = max_min[0]
					min_of_range = max_min[1]
					
					if size_price >= max_of_range and min_of_range >= size_price:
						print(msg)
						if display_on_tg == 1: bot1.send_message(662482931, dist_marker+msg)
				
				elif distance_3 == minimum_dist:
					
					distance = distance_3
					decimal_x = len(str(combined_list[-3][0]).split('.')[-1].rstrip('0'))
					size_price = combined_list[-3][0]
					size_in_thousands = int(combined_list[-3][1] / 1000)
					size_in_dollars = int((combined_list[-3][0] * combined_list[-3][1]) / 1000)
					zero_addition = (max_decimal - decimal_x) * '0'
					last_size_in_thousands = int(combined_list[-max_minimum_candle][1] / 1000)
					msg = (f"\n{distance}% {symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K \n"
					      f"{size_in_thousands}K > {last_size_in_thousands}K")
					
					max_min = extremum(symbol, '1m', 10)
					max_of_range = max_min[0]
					min_of_range = max_min[1]
					
					if size_price >= max_of_range and min_of_range >= size_price:
						print(msg)
						if display_on_tg == 1: bot1.send_message(662482931, dist_marker+msg)
			# 	else:
			# 		print(".")
			# else:
			# 	print(".")
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	
	pairs = (input('Pairs: ')).split(',')
	reload_time = float(input("Reload seconds (def. 1): ") or 1)
	display_on_tg = int(input("Telegram alert? (def. 0): ") or 0)
	request_limit_length = int(input("Request length (def. 100): ") or 100)
	search_distance = float(input("Search distance (def. 1.0%): ") or 1.0)
	max_minimum_candle = int(input("Start avg candle (def. 4): ") or 4)
	multiplier = int(input("Multiplier (def. x3): ") or 3)

	if True:
		
		manager = Manager()
		shared_queue = manager.Queue()

		time1 = time.perf_counter()
		
		print(f">>> {datetime.now().strftime('%H:%M:%S')}")

		the_processes = []
		for pair in pairs:
			process = Process(target=search,
			                  args=(
				                  pair,
				                  reload_time,
				                  display_on_tg,
				                  request_limit_length,
				                  search_distance,
				                  max_minimum_candle,
				                  multiplier,
			                      ))
			the_processes.append(process)

		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()
			
		time2 = time.perf_counter()
		time3 = time2 - time1

		# print(f"<<< {datetime.now().strftime('%H:%M:%S')} / {int(time3)} seconds")
		print("Process ended.")
		