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
		only_round: bool,
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
				title = f"{f_fifth_distance}% FUT {symbol}"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
				levels_check_futures.clear()
				sys.stdout.flush()
				
				if display_on_tg == 1:
					if only_round:
						if (f_max_decimal - decimal_x) >= 2:
							screenshoter_send(symbol, "f", size_price, title, msg)
					else:
						screenshoter_send(symbol, "f", size_price, title, msg)
			
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
				title = f"{s_fifth_distance}% SPOT {symbol}"
				
				print(f"{datetime.now().strftime('%H:%M:%S')}\n" + msg)
				levels_check_spot.clear()
				sys.stdout.flush()
				
				if display_on_tg == 1:
					if only_round:
						if (s_max_decimal - decimal_x) >= 2:
							screenshoter_send(symbol, "s", size_price, title, msg)
					else:
						screenshoter_send(symbol, "s", size_price, title, msg)
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{symbol}: {time3} + {float('{:.2f}'.format(reload_time))} s, levels: {len(levels_check_futures)}/{len(levels_check_spot)}")
			sys.stdout.flush()
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	
	request_limit_length = 100
	
	print("\nPairs section:")
	x_range_filter = int(input("4H range, % (def. 0): ") or 0)
	x_change_filter = int(input("4H change, % (def. 0): ") or 0)
	x_volume_filter = int(input("4H volume, millions (def. 1): ") or 1)
	x_trades_filter = int(input("4H trades, thousands (def. 200): ") or 200)
	x_atr_per_filter = float(input("4H avg ATR, % (def. 0.30): ") or 0.30)
	ts_percent_filter = float(input("4H ticksize, % (def. 0.05): ") or 0.05)

	print("\nSizes section:")
	search_distance = float(input("Search distance (def. 1.0%): ") or 1.0)
	futures_size_filter = int(input("Futures size filter in K (def. 150): ") or 150)
	spot_size_filter = int(input("Spot size filter in K (def. 15): ") or 15)
	multiplier = int(input("Multiplier (def. x4): ") or 4)
	only_round = str(input("Size only on round level? (def. True): ") or True)
	only_round = True if only_round == "True" else False
	display_on_tg = int(input("Telegram alert? (def. 1): ") or 1)
	time_log = int(input("Print time log? (def. 1): ") or 1)
	
	msg_parameters = (
		f"x_range_filter = {x_range_filter}\n"
		f"x_change_filter = {x_change_filter}\n"
		f"x_volume_filter = {x_volume_filter}\n"
		f"x_trades_filter = {x_trades_filter}\n"
		f"x_atr_per_filter = {x_atr_per_filter}\n"
		f"ts_percent_filter = {ts_percent_filter}\n\n"
		f"search_distance = {search_distance}\n"
		f"futures_size_filter = {futures_size_filter}\n"
		f"spot_size_filter = {spot_size_filter}\n"
		f"multiplier = {multiplier}\n"
		f"only_round = {only_round}"
	)
	bot1.send_message(662482931, msg_parameters)
	
	print("\nGetting pairs...")
	pairs = get_pairs(
		x_range_filter=x_range_filter,
		x_change_filter=x_change_filter,
		x_volume_filter=x_volume_filter,
		x_trades_filter=x_trades_filter,
		x_atr_per_filter=x_atr_per_filter,
		ts_percent_filter=ts_percent_filter
	)
	print(pairs)
	print("")
	
	reload = 60 / ((1100 / 12) / len(pairs)) - 3
	reload_time = reload if reload >= 1 else 1
	level_repeat = int(60 / (reload_time + 3))
	
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
			                  only_round,
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
		