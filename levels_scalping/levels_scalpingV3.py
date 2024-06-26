import time
from datetime import datetime
from multiprocessing import Process, Manager
import telebot
from modules import order_book, three_distances
import sys
from get_pairsV4 import get_pairs
from screenshoterV2 import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

DIV_TOKEN = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot2 = telebot.TeleBot(DIV_TOKEN)
	
def search(
		symbol,
		reload_time,
		request_limit_length,
		search_distance,
		multiplier,
		level_repeat,
		time_log
):
	
	levels_check_futures = []
	levels_check_spot = []
	
	while True:
		
		time1 = time.perf_counter()
		# ==== DATA REQUEST ====
		futures_data = order_book(symbol, request_limit_length, "f")
		spot_data = order_book(symbol, request_limit_length, "s")
		
		if futures_data != None:
		
			f_close = futures_data[0]
			f_combined_list = futures_data[2]
			f_max_decimal = futures_data[3]
			f_max_avg_size = f_combined_list[-4][1] * multiplier
			
			f_distances = three_distances(symbol, f_close, f_combined_list, f_max_avg_size, search_distance, "f")
			
			f_fifth_distance = 100
			f_fifth_level = 0
			f_fifth_size = 0
			f_bigger_than = 0
			
			if len(f_distances) != 0:
				for i in f_distances:
					levels_check_futures.append(i[1])

					if levels_check_futures.count(i[1]) >= level_repeat and i[0] < f_fifth_distance:
						# print(f"Futures levels list: {levels_check_futures}")
						f_fifth_distance = i[0]
						f_fifth_level = i[1]
						f_fifth_size = i[2]
						f_bigger_than = i[3]
			
			if f_fifth_distance <= search_distance:
				
				decimal_x = len(str(f_fifth_level).split('.')[-1].rstrip('0'))
				size_price = f_fifth_level
				size_in_thousands = int(f_fifth_size / 1000)
				size_in_dollars = int((f_fifth_level * f_fifth_size) / 1000)
				zero_addition = (f_max_decimal - decimal_x) * '0'
				
				msg = f"{f_fifth_distance}% FUT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K (1/{f_bigger_than})"
				title = f"{f_fifth_distance}% FUT {symbol}"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)

				screenshoter_send(symbol, "f", size_price, title, msg)
			
				levels_check_futures.clear()
				sys.stdout.flush()
			
		if spot_data != None:
			
			s_close = spot_data[0]
			s_combined_list = spot_data[2]
			s_max_decimal = spot_data[3]
			s_max_avg_size = s_combined_list[-4][1] * multiplier
			
			s_distances = three_distances(symbol, s_close, s_combined_list, s_max_avg_size, search_distance, "s")
			
			s_fifth_distance = 100
			s_fifth_level = 0
			s_fifth_size = 0
			s_bigger_than = 0

			if len(s_distances) != 0:
				for i in s_distances:
					levels_check_spot.append(i[1])
					
					if levels_check_spot.count(i[1]) >= level_repeat and i[0] < s_fifth_distance:
						# print(f"Spot levels list: {levels_check_spot}")
						s_fifth_distance = i[0]
						s_fifth_level = i[1]
						s_fifth_size = i[2]
						s_bigger_than = i[3]

			if s_fifth_distance <= 1:
				
				decimal_x = len(str(s_fifth_level).split('.')[-1].rstrip('0'))
				size_price = s_fifth_level
				size_in_thousands = int(s_fifth_size / 1000)
				size_in_dollars = int((s_fifth_level * s_fifth_size) / 1000)
				zero_addition = (s_max_decimal - decimal_x) * '0'
				# direction = f"\nSupport with {level_repeat} repeats!" if s_close > size_price else f"\nResistance with {level_repeat} repeats!"
				
				msg = f"{s_fifth_distance}% 🔥 SPOT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K (1/{s_bigger_than})"
				title = f"{s_fifth_distance}% SPOT {symbol}"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)

				screenshoter_send(symbol, "s", size_price, title, msg)
				
				levels_check_spot.clear()
				sys.stdout.flush()
				
		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{symbol}: {time3} + {float('{:.2f}'.format(reload_time))} s, levels: {len(levels_check_futures)}/{len(levels_check_spot)}")
			sys.stdout.flush()
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	
	request_limit_length = 100

	search_distance = 1 # float(input(Search distance (def. 1.0%): ") or 1.0)
	multiplier = 4 # int(input("Multiplier (def. x4): ") or 4)
	seconds_approve = 30 # int(input(Lifetime of size, seconds (def. 30): ") or 30)
	time_log = int(input("Print time log? (def. 0): ") or 0)
	
	msg_parameters = (
		f"search_distance = {search_distance}\n"
		f"multiplier = {multiplier}\n"
		f"seconds_approve = {seconds_approve}\n"
	)
	
	bot1.send_message(662482931, msg_parameters)
	
	print("\nGetting pairs...")
	pairs = get_pairs()
	print(pairs)
	print("")
	
	reload = seconds_approve / ((1100 / 14) / len(pairs)) - 3
	reload_time = reload if reload >= 1 else 1
	level_repeat = int(seconds_approve / (reload_time + 3))
			
	manager = Manager()
	shared_queue = manager.Queue()
	
	print(f"START at {datetime.now().strftime('%H:%M:%S')}, {len(pairs)} pairs, level repeat: {level_repeat}, sleep time {float('{:.2f}'.format(reload_time))} s.")
	print("Sleep 20 seconds...")
	time.sleep(20)

	the_processes = []
	for pair in pairs:
		process = Process(target=search,
		                  args=(
			                  pair,
			                  reload_time,
			                  request_limit_length,
			                  search_distance,
			                  multiplier,
			                  level_repeat,
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
		