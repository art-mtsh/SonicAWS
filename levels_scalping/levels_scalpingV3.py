import time
from datetime import datetime
from multiprocessing import Process, Manager
import requests
import telebot
# from module_get_pairs_binanceV3 import binance_pairs
# from screenshoter import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(
		symbol,
		frame,
		gap_filter,
		density_filter,
		atr_per_filter,
		trades_k_filter,
		s_queue,
		search_distance,
		levels_scatter
		):
	
	while True:
		
		request_limit_length = 500
		
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
		
			distance_1 = abs(close - combined_list[-1][0]) / (close / 100)
			distance_2 = abs(close - combined_list[-2][0]) / (close / 100)
			distance_3 = abs(close - combined_list[-3][0]) / (close / 100)
			
			distance_1 = float('{:.2f}'.format(distance_1))
			distance_2 = float('{:.2f}'.format(distance_2))
			distance_3 = float('{:.2f}'.format(distance_3))
			
			# print(f"{symbol}: {distance_1}, {distance_2}, {distance_3}")
			
			search_distance = 1
			max_minimum_candle = 4
			multiplier = 2
			
			if min([distance_1, distance_2, distance_3]) <= search_distance:
				
				minimum_dist = min([distance_1, distance_2, distance_3])
				
				if distance_1 == minimum_dist and \
					combined_list[-1][1] >= combined_list[-max_minimum_candle][1] * multiplier:
					
					decimal_x = len(str(combined_list[-1][1]).split('.')[-1].rstrip('0'))
					
					msg = f"\n{symbol}: {combined_list[-1][0]} {decimal_x}/{max_decimal} {int(combined_list[-1][1])} >= {int(combined_list[-max_minimum_candle][1])} in {distance_1}%"
					print(msg)
					bot1.send_message(662482931, msg)
	
				elif distance_2 == minimum_dist and \
					combined_list[-2][1] >= combined_list[-max_minimum_candle][1] * multiplier:
					
					decimal_x = len(str(combined_list[-2][1]).split('.')[-1].rstrip('0'))
					
					msg = f"\n{symbol}: {combined_list[-2][0]} {decimal_x}/{max_decimal} {int(combined_list[-2][1])} >= {int(combined_list[-max_minimum_candle][1])} in {distance_2}%"
					print(msg)
					bot1.send_message(662482931, msg)
					
				elif distance_3 == minimum_dist and \
					combined_list[-3][1] >= combined_list[-max_minimum_candle][1] * multiplier:
					
					decimal_x = len(str(combined_list[-3][1]).split('.')[-1].rstrip('0'))
					
					msg = f"\n{symbol}: {combined_list[-3][0]} {decimal_x}/{max_decimal} {int(combined_list[-3][1])} >= {int(combined_list[-max_minimum_candle][1])} in {distance_3}%"
					print(msg)
					bot1.send_message(662482931, msg)
					
				# else:
				# 	print(f"\n{symbol}: {combined_list[-1][1]} >= {combined_list[-max_minimum_candle][1]} in {distance_1}%\n")

		print(".", end="")
		time.sleep(2)
		
if __name__ == '__main__':
	
	proc = 14
	gap_filter = 0.5 # float(input("Max gap filter (def. 0.2%): ") or 0.2)
	density_filter = 25 # int(input("Density filter (def. 30): ") or 30)
	tick_size_filter = 0.1 # float(input("Ticksize filter (def. 0.03%): ") or 0.03)
	atr_per_filter = 0.20 # float(input("ATR% filter (def. 0.3%): ") or 0.3)
	trades_k_filter = 100 # int(input("Trades filter (def. 100): ") or 100)
	search_distance = 1.0
	levels_scatter = 0.03 / 100
	
	# def waiting():
	#
	# 	while True:
	# 		now = datetime.now()
	# 		last_hour_digit = int(now.strftime('%H'))
	# 		last_minute_digit = now.strftime('%M')
	# 		last_second_digit = now.strftime('%S')
	# 		time.sleep(1)
	#
	# 		if int(last_second_digit) == 0:
	# 			break

	if True:
		
		manager = Manager()
		shared_queue = manager.Queue()

		time1 = time.perf_counter()
		pairs = ['GASUSDT', 'NEOUSDT', 'ARKUSDT', 'XVSUSDT', 'GMTUSDT']
		
		print(f">>> {datetime.now().strftime('%H:%M:%S')}")
		
		the_processes = []
		for pair in pairs:
			process = Process(target=search,
			                  args=(
				                  pair,
			                      "1m",
			                      gap_filter,
			                      density_filter,
			                      atr_per_filter,
				                  trades_k_filter,
			                      shared_queue,
				                  search_distance,
				                  levels_scatter,
			                      ))
			the_processes.append(process)

		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()
		
		# printer(shared_queue)
			
		time2 = time.perf_counter()
		time3 = time2 - time1

		# print(f"<<< {datetime.now().strftime('%H:%M:%S')} / {int(time3)} seconds")
		print("Process ended.")
		# waiting()
		