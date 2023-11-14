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
		max_minimum_candle,
		multiplier,
		size_filter,
		time_log
):
	
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
			
			f_max_avg_size = f_combined_list[-max_minimum_candle][1] * multiplier
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
				last_size_in_thousands = int(f_combined_list[-max_minimum_candle][1] / 1000)
				
				# print(
				# 	f"FUTURES {symbol}, "
				# 	f"min_distance {min_distance}%, "
				# 	f"min_index {min_index}, "
				# 	f"decimal_x {decimal_x}, "
				# 	f"size_price {size_price}, "
				# 	f"size_in_thousands {size_in_thousands}, "
				# 	f"size_in_dollars {size_in_dollars}, "
				# 	f"zero_addition {zero_addition}, "
				# 	f"last_size_in_thousands {last_size_in_thousands}"
				# )
				
				msg = (f"{min_distance}% FUT #{symbol}: #{size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K")
				
				if size_in_dollars >= size_filter:
					print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
					if display_on_tg == 1:
						bot1.send_message(662482931, msg)
	
		# else:
		# 	print(f"Some shit with {symbol} futures data!")
			
		if spot_data != None:
			
			s_close = spot_data[0]
			s_combined_list = spot_data[1]
			s_max_decimal = spot_data[2]
	
			s_max_avg_size = s_combined_list[-max_minimum_candle][1] * multiplier
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
				last_size_in_thousands = int(s_combined_list[-max_minimum_candle][1] / 1000)
			
				# print(
				# 	f"SPOT {symbol}, "
				# 	f"min_distance {min_distance}%, "
				# 	f"min_index {min_index}, "
				# 	f"decimal_x {decimal_x}, "
				# 	f"size_price {size_price}, "
				# 	f"size_in_thousands {size_in_thousands}, "
				# 	f"size_in_dollars {size_in_dollars}, "
				# 	f"zero_addition {zero_addition}, "
				# 	f"last_size_in_thousands {last_size_in_thousands}"
				# )
		
				msg = (f"{min_distance}% SPOT #{symbol}: #{size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K")
				
				if size_in_dollars >= size_filter:
					print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
					if display_on_tg == 1:
						bot1.send_message(662482931, msg)
			
		# else:
		# 	print(f"Some shit with {symbol} spot data!")
		
		# if minimum_dist <= search_distance:
		#
		# 	if minimum_dist <= search_distance / 4:
		# 		dist_marker = "🟩 "
		# 	elif minimum_dist <= search_distance / 4 * 2:
		# 		dist_marker = "🟨 "
		# 	elif minimum_dist <= search_distance / 4 * 3:
		# 		dist_marker = "🟧 "
		# 	else:
		# 		dist_marker = "🟥 "
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{time3} s")
			# print(f"{symbol} {datetime.now().strftime('%H:%M:%S')} / done in {time3} seconds")
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	

	request_limit_length = 100
	max_minimum_candle = 4
	
	pairs = (input('Pairs: ')).split(', ')
	search_distance = float(input("Search distance (def. 1.0%): ") or 1.0)
	size_filter = int(input("Size filter in K (def. 100): ") or 100)
	multiplier = int(input("Multiplier (def. x3): ") or 3)
	
	display_on_tg = int(input("Telegram alert? (def. 0): ") or 0)
	time_log = int(input("Print time log? (def. 0): ") or 0)
	reload_time = 60 / ((1150 / 11) / len(pairs)) - 2.5

	if True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		print(f">>> {datetime.now().strftime('%H:%M:%S')} {len(pairs)} pairs, {int(reload_time + 2.5)} reload period")

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
		