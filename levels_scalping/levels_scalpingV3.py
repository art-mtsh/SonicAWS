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
		search_distance,
		max_minimum_candle,
		multiplier,
):
	
	while True:
		
		request_limit_length = 100
		
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
			# distance_4 = abs(close - combined_list[-4][0]) / (close / 100) if combined_list[-4][1] >= combined_list[-max_minimum_candle][1] * multiplier else 100
			
			distance_1 = float('{:.2f}'.format(distance_1))
			distance_2 = float('{:.2f}'.format(distance_2))
			distance_3 = float('{:.2f}'.format(distance_3))
			# distance_4 = float('{:.2f}'.format(distance_4))

			
			if min([distance_1, distance_2, distance_3]) <= search_distance:
				
				minimum_dist = min([distance_1, distance_2, distance_3])
				
				if minimum_dist <= search_distance / 4:
					dist_marker = "🟩"
				elif minimum_dist <= search_distance / 4 * 2:
					dist_marker = "🟨"
				elif minimum_dist <= search_distance / 4 * 3:
					dist_marker = "🟧"
				else:
					dist_marker = "🟥"
					
				if distance_1 == minimum_dist:
					
					decimal_x = len(str(combined_list[-1][0]).split('.')[-1].rstrip('0'))

					msg = f"\n{dist_marker} {symbol}: {combined_list[-1][0]} ({decimal_x}/{max_decimal}), {int(combined_list[-1][1] / 1000)}K > {int(combined_list[-max_minimum_candle][1] / 1000)}K in {distance_1}%"
					print(msg)
					bot1.send_message(662482931, msg)
	
				elif distance_2 == minimum_dist:
					
					decimal_x = len(str(combined_list[-2][0]).split('.')[-1].rstrip('0'))
				
					msg = f"\n{dist_marker} {symbol}: {combined_list[-2][0]} ({decimal_x}/{max_decimal}), {int(combined_list[-2][1] / 1000)}K > {int(combined_list[-max_minimum_candle][1] / 1000)}K in {distance_2}%"
					print(msg)
					bot1.send_message(662482931, msg)
				
				elif distance_3 == minimum_dist:
					
					decimal_x = len(str(combined_list[-3][0]).split('.')[-1].rstrip('0'))
					
					msg = f"\n{dist_marker} {symbol}: {combined_list[-3][0]} ({decimal_x}/{max_decimal}), {int(combined_list[-3][1] / 1000)}K > {int(combined_list[-max_minimum_candle][1] / 1000)}K in {distance_3}%"
					print(msg)
					bot1.send_message(662482931, msg)
				
				# elif distance_4 == minimum_dist:
				#
				# 	decimal_x = len(str(combined_list[-4][0]).split('.')[-1].rstrip('0'))
				#
				# 	msg = f"\n{dist_marker} {symbol}: {combined_list[-4][0]} ({decimal_x}/{max_decimal}), {int(combined_list[-4][1] / 1000)}K > {int(combined_list[-max_minimum_candle][1] / 1000)}K in {distance_4}%"
				# 	print(msg)
				# 	bot1.send_message(662482931, msg)
					
				else:
					print(".")
			else:
				print(".")
		time.sleep(1)
		
if __name__ == '__main__':

	search_distance = 2.0
	max_minimum_candle = 4
	multiplier = 3

	if True:
		
		manager = Manager()
		shared_queue = manager.Queue()

		time1 = time.perf_counter()
		pairs = ['BLURUSDT', 'GMTUSDT', 'XVSUSDT', 'GASUSDT', 'TWTUSDT', "YGGUSDT"]
		
		print(f">>> {datetime.now().strftime('%H:%M:%S')}")
		
		the_processes = []
		for pair in pairs:
			process = Process(target=search,
			                  args=(
				                  pair,
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
		
		# printer(shared_queue)
			
		time2 = time.perf_counter()
		time3 = time2 - time1

		# print(f"<<< {datetime.now().strftime('%H:%M:%S')} / {int(time3)} seconds")
		print("Process ended.")
		