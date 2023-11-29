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

	
def search(
		symbol,
		reload_time,
		display_on_tg,
		request_limit_length,
		search_distance,
		multiplier,
		level_repeat,
		futures_size_filter,
		spot_size_filter,
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
			
			f_distances = three_distances(symbol, f_close, f_combined_list, f_max_avg_size, search_distance, futures_size_filter)
			
			f_fifth_distance = 100
			f_fifth_level = 0
			f_fifth_size = 0
			
			if len(f_distances) != 0:
				for i in f_distances:
					levels_check_futures.append(i[1])

					if levels_check_futures.count(i[1]) >= level_repeat and i[0] < f_fifth_distance:
						# print(f"Futures levels list: {levels_check_futures}")
						f_fifth_distance = i[0]
						f_fifth_level = i[1]
						f_fifth_size = i[2]
			
			if f_fifth_distance != 100:
				
				decimal_x = len(str(f_fifth_level).split('.')[-1].rstrip('0'))
				size_price = f_fifth_level
				size_in_thousands = int(f_fifth_size / 1000)
				size_in_dollars = int((f_fifth_level * f_fifth_size) / 1000)
				zero_addition = (f_max_decimal - decimal_x) * '0'
				# direction = f"\nSupport with {level_repeat} repeats!" if f_close > size_price else f"\nResistance with {level_repeat} repeats!"
				
				msg = f"{f_fifth_distance}% FUT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
				levels_check_futures.clear()
				sys.stdout.flush()
				
				if display_on_tg == 1:
					bot1.send_message(662482931, msg)
					title = f"{f_fifth_distance}% FUT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K"
					screenshoter_send(symbol, "f", size_price, title)
			
		if spot_data != None:
			
			s_close = spot_data[0]
			s_combined_list = spot_data[1]
			s_max_decimal = spot_data[2]
			s_max_avg_size = s_combined_list[-4][1] * multiplier
			
			s_distances = three_distances(symbol, s_close, s_combined_list, s_max_avg_size, search_distance, spot_size_filter)
			
			s_fifth_distance = 100
			s_fifth_level = 0
			s_fifth_size = 0
			
			if len(s_distances) != 0:
				for i in s_distances:
					levels_check_spot.append(i[1])
					
					if levels_check_spot.count(i[1]) >= level_repeat and i[0] < s_fifth_distance:
						# print(f"Spot levels list: {levels_check_spot}")
						s_fifth_distance = i[0]
						s_fifth_level = i[1]
						s_fifth_size = i[2]
			
			if s_fifth_distance != 100:
				
				decimal_x = len(str(s_fifth_level).split('.')[-1].rstrip('0'))
				size_price = s_fifth_level
				size_in_thousands = int(s_fifth_size / 1000)
				size_in_dollars = int((s_fifth_level * s_fifth_size) / 1000)
				zero_addition = (s_max_decimal - decimal_x) * '0'
				# direction = f"\nSupport with {level_repeat} repeats!" if s_close > size_price else f"\nResistance with {level_repeat} repeats!"
				
				msg = f"{s_fifth_distance}% 🔥 SPOT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
				levels_check_spot.clear()
				sys.stdout.flush()
				
				if display_on_tg == 1:
					bot1.send_message(662482931, msg)
					title = f"{s_fifth_distance}% SPOT #{symbol}: {size_price}{zero_addition} x {size_in_thousands}K = ${size_in_dollars}K"
					screenshoter_send(symbol, "s", size_price, title)
					
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{symbol}: {time3} s , went to sleep on {float('{:.2f}'.format(reload_time))} s.")
			sys.stdout.flush()
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	
	request_limit_length = 100
	
	print("\nPairs section:")
	daily_volume_filter = int(input("Daily volume, millions (def. 0): ") or 0)
	daily_trades_filter = int(input("Daily trades, thousands (def. 0): ") or 0)
	avg_atr_per_filter = float(input("ATR% filter (def. 0.8%): ") or 0.8)
	ts_percent_filter = float(input("Ticksize filter (def. 0.1%): ") or 0.1)

	print("\nSizes section:")
	search_distance = float(input("Search distance (def. 1.0%): ") or 1.0)
	futures_size_filter = int(input("Futures size filter in K (def. 150): ") or 150)
	spot_size_filter = int(input("Spot size filter in K (def. 10): ") or 10)
	multiplier = int(input("Multiplier (def. x4): ") or 4)
	display_on_tg = int(input("Telegram alert? (def. 1): ") or 1)
	time_log = int(input("Print time log? (def. 1): ") or 1)
	
	print("\nGetting pairs...")
	pairs = get_pairs(
		daily_volume_filter=daily_volume_filter,
		daily_trades_filter=daily_trades_filter,
		avg_atr_per_filter=avg_atr_per_filter,
		ts_percent_filter=ts_percent_filter
	)
	print(pairs)
	print("")
	
	reload = 60 / ((1100 / 11) / len(pairs)) - 1.5
	reload_time = reload if reload >= 1 else 1
	level_repeat = int(60 / (reload_time + 1.5))
	
	if display_on_tg == 1:
		bot1.send_message(662482931, str(pairs))
			
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
			                  display_on_tg,
			                  request_limit_length,
			                  search_distance,
			                  multiplier,
			                  level_repeat,
			                  futures_size_filter,
			                  spot_size_filter,
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
		