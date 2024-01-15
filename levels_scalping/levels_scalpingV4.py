import time
from datetime import datetime
from multiprocessing import Process, Manager
import telebot
from modules import klines, order_book
import sys
from get_pairsV4 import get_pairs
from screenshoterV2 import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

	
def search(
		symbol,
		reload_time,
		request_limit_length,
		search_distance,
		multiplier,
		level_repeat,
		time_log
):
	
	levels_check = []

	c_room = 30
	d_room = 10
	
	while True:
		
		time1 = time.perf_counter()

		for market_type in ["f", "s"]:

			depth = order_book(symbol, 100, market_type)
			the_klines = klines(symbol, "1m", 100, market_type)

			if depth != None and the_klines != None:

				c_open, c_high, c_low, c_close, avg_vol = the_klines[0], the_klines[1], the_klines[2], the_klines[3], the_klines[4]
				depth = depth[1]

				if len(c_high) == len(c_low):
					for i in range(2, len(c_low)):

						if c_high[-i] >= max(c_high[-1: -i - c_room: -1]):
							for item in depth:
								if d_room - 1 < depth.index(item) < len(depth) - d_room and c_high[-i] == item[0]:

									lower_sizes = [depth[k][1] for k in range(depth.index(item) - d_room, depth.index(item))]
									higher_sizes = [depth[k][1] for k in range(depth.index(item) + 1, depth.index(item) + d_room + 1)]
									distance_per = abs(c_high[i] - c_close[-1]) / (c_close[-1] / 100)
									distance_per = float('{:.2f}'.format(distance_per))

									if item[1] >= max(lower_sizes) and item[1] >= max(higher_sizes) and distance_per <= search_distance:

										if levels_check.count(c_high[-i]) >= level_repeat:
											print(f"Found size on high {symbol} ({market_type}) at {c_high[-i]} size {item[1]} (${int(item[0] * item[1])})")
											msg = f"{market_type.capitalize()} #{symbol}: {item[0]} * {item[1]} = ${int(item[0] * item[1])} ({distance_per}%)"
											screenshoter_send(symbol, market_type, item[0], msg)
											levels_check.clear()
										else:
											levels_check.append(c_high[-i])

						if c_low[-i] <= min(c_low[-1: -i - c_room: -1]):
							for item in depth:
								if d_room - 1 < depth.index(item) < len(depth) - d_room and c_low[-i] == item[0]:

									lower_sizes = [depth[k][1] for k in range(depth.index(item) - d_room, depth.index(item))]
									higher_sizes = [depth[k][1] for k in range(depth.index(item) + 1, depth.index(item) + d_room + 1)]
									distance_per = abs(c_low[i] - c_close[-1]) / (c_close[-1] / 100)
									distance_per = float('{:.2f}'.format(distance_per))

									if item[1] >= max(lower_sizes) and item[1] >= max(higher_sizes) and distance_per <= search_distance:

										if levels_check.count(c_low[-i]) >= level_repeat:
											print(f"Found size on low {symbol} ({market_type}) at {c_low[-i]} size {item[1]} (${int(item[0] * item[1])})")
											msg = f"{market_type.capitalize()} #{symbol}: {item[0]} * {item[1]} = ${int(item[0] * item[1])} ({distance_per}%)"
											screenshoter_send(symbol, market_type, item[0], msg)
											levels_check.clear()
										else:
											levels_check.append(c_low[-i])

			elif market_type == "f" and (depth == None or the_klines == None):
				msg = (f"-----------------> \n"
					   f"Main file. Error in {symbol} data. Futures is n/a! \n"
					   f"-----------------> \n")
				print(msg)
				bot1.send_message(662482931, msg)

		time2 = time.perf_counter()
		time3 = time2 - time1
		time3 = float('{:.2f}'.format(time3))
		
		if time_log > 0:
			print(f"{symbol}: {time3} + {float('{:.2f}'.format(reload_time))} s, levels: {len(levels_check)}")
			sys.stdout.flush()
		
		time.sleep(reload_time)
		
if __name__ == '__main__':
	
	request_limit_length = 100

	search_distance = 1 # float(input(Search distance (def. 1.0%): ") or 1.0)
	multiplier = 4 # int(input("Multiplier (def. x4): ") or 4)
	seconds_approve = 60 # int(input(Lifetime of size, seconds (def. 30): ") or 30)
	time_log = int(input("Print time log? (def. 0): ") or 0)

	print("\nGetting pairs...")
	pairs = get_pairs()
	print(pairs)
	print("")

	reload = 60 / (1100 / (14 * len(pairs))) - 2
	reload_time = reload if reload >= 1 else 1
	level_repeat = int(seconds_approve / (reload_time + 2))
			
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
		