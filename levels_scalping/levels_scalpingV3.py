import time
from datetime import datetime
from multiprocessing import Process, Manager
import telebot
from modules import order_book, three_distances

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

	
def search(
		symbol,
		reload_time,
		display_on_tg,
		request_limit_length,
		search_distance,
		multiplier,
		size_filter,
		time_log
):
	
	levels_check_futures = []
	levels_check_spot = []
	
	while True:
		
		time1 = time.perf_counter()
		# ==== DATA REQUEST ====
		futures_order_book = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit={request_limit_length}"
		spot_order_book = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={request_limit_length}"
		
		futures_data = order_book(futures_order_book)
		spot_data = order_book(spot_order_book)
		
		if futures_data != None:
		
			f_close = futures_data[0]
			f_combined_list = futures_data[1]
			f_max_decimal = futures_data[2]
			
			f_max_avg_size = f_combined_list[-4][1] * multiplier
			f_distances = three_distances(symbol, f_combined_list, f_max_avg_size, f_close)
		
			min_distance = min(f_distances)
			
			if min_distance <= search_distance:
				
				min_index = f_distances.index(min_distance)
				min_index = min_index + 1
				
				decimal_x = len(str(f_combined_list[-min_index][0]).split('.')[-1].rstrip('0'))
				size_price = f_combined_list[-min_index][0]
				size_in_thousands = int(f_combined_list[-min_index][1] / 1000)
				size_in_dollars = int((f_combined_list[-min_index][0] * f_combined_list[-min_index][1]) / 1000)
				zero_addition = (f_max_decimal - decimal_x) * '0'
				last_size_in_thousands = int(f_combined_list[-4][1] / 1000)
				
				msg = (f"{min_distance}% FUT #{symbol}: #{size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K")
				
				if size_in_dollars >= size_filter:
					
					levels_check_futures.append(size_price)
					
					if levels_check_futures.count(size_price) >= 5:
						
						print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
						print(f"{size_price} is repeated 5 times!")
						levels_check_futures.clear()
						
						if display_on_tg == 1:
							bot1.send_message(662482931, msg + "\nRepeated 5 times!")
					
					else:
						
						print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
						
						if display_on_tg == 1:
							bot1.send_message(662482931, msg)
	
		# else:
		# 	print(f"Some shit with {symbol} futures data!")
			
		if spot_data != None:
			
			s_close = spot_data[0]
			s_combined_list = spot_data[1]
			s_max_decimal = spot_data[2]
	
			s_max_avg_size = s_combined_list[-4][1] * multiplier
			s_distances = three_distances(symbol, s_combined_list, s_max_avg_size, s_close)
			
			min_distance = min(s_distances)
			
			if min_distance <= search_distance:
				min_index = s_distances.index(min_distance)
				min_index = min_index + 1
				
				decimal_x = len(str(s_combined_list[-min_index][0]).split('.')[-1].rstrip('0'))
				size_price = s_combined_list[-min_index][0]
				size_in_thousands = int(s_combined_list[-min_index][1] / 1000)
				size_in_dollars = int((s_combined_list[-min_index][0] * s_combined_list[-min_index][1]) / 1000)
				zero_addition = (s_max_decimal - decimal_x) * '0'
				last_size_in_thousands = int(s_combined_list[-4][1] / 1000)
		
				msg = (f"{min_distance}% SPOT #{symbol}: #{size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K")
				
				if size_in_dollars >= size_filter:
					
					levels_check_spot.append(size_price)
					
					if levels_check_spot.count(size_price) >= 5:
						
						print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
						print(f"{size_price} is repeated 5 times!")
						levels_check_spot.clear()
						
						if display_on_tg == 1:
							bot1.send_message(662482931, msg + "\nRepeated 5 times!")
						
					else:
						
						print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
						
						if display_on_tg == 1:
							bot1.send_message(662482931, msg)
			
		# else:
		# 	print(f"Some shit with {symbol} spot data!")
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{time3} s")
			# print(f"{symbol} {datetime.now().strftime('%H:%M:%S')} / done in {time3} seconds")
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	

	request_limit_length = 100
	
	pairs = (input('Pairs: ')).split(', ')
	search_distance = float(input("Search distance (def. 1.0%): ") or 1.0)
	size_filter = int(input("Size filter in K (def. 100): ") or 100)
	multiplier = int(input("Multiplier (def. x3): ") or 3)
	
	display_on_tg = int(input("Telegram alert? (def. 1): ") or 1)
	time_log = int(input("Print time log? (def. 0): ") or 0)
	reload_time = 60 / ((1100 / 11) / len(pairs)) - 2.5

	if True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		print(f"START at {datetime.now().strftime('%H:%M:%S')}, {len(pairs)} pairs, {int(reload_time + 2.5)} s. reload period")

		the_processes = []
		for pair in pairs:
			process = Process(target=search,
			                  args=(
				                  pair,
				                  reload_time,
				                  display_on_tg,
				                  request_limit_length,
				                  search_distance,
				                  multiplier,
				                  size_filter,
				                  time_log,
			                      ))
			the_processes.append(process)

		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()

		print("Process ended.")
		