import time
from datetime import datetime
from multiprocessing import Process, Queue, Manager
import requests
import telebot
from module_get_pairs_binanceV3 import binance_pairs
# from screenshoter import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(
		filtered_symbols,
		frame,
		gap_filter,
		density_filter,
		level_window,
		distance_filter,
		atr_per_filter,
		s_queue
		):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		request_limit_length = 576
		
		# ==== DATA REQUEST ====
		futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
		spot_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
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
				buy_volume = list(float(i[9]) for i in binance_candle_data)
				sell_volume = [volume[0] - buy_volume[0]]
				max_gap = 0
				
				# ==== GAP AND SELL VOLUME ====
				for curr_index in range(1, len(close)):
					gap = abs(open[curr_index] - close[curr_index - 1])
					gap_p = 0
					if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
					if gap_p > max_gap: max_gap = gap_p

					s_v = volume[curr_index] - buy_volume[curr_index]
					sell_volume.append(s_v)
				max_gap = float('{:.3f}'.format(max_gap))
				density = (max(high[-13: -1]) - min(low[-13: -1])) / tick_size
				
				avg_atr = [high[-c] - low[-c] for c in range(48)]
				avg_atr = float('{:.4f}'.format(sum(avg_atr) / len(avg_atr)))
				
				avg_atr_per = [(high[-c] - low[-c]) / (high[-c] / 100) for c in range(48)]
				avg_atr_per = float('{:.4f}'.format(sum(avg_atr_per) / len(avg_atr_per)))
				
				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and \
					density >= density_filter and \
					avg_atr_per >= atr_per_filter and \
					len(high) == len(low) == request_limit_length:
					
					dist_to_high = 100
					dist_to_low = 100
					
					higher_high = ""
					lower_low = ""
					
					for a in range(5, request_limit_length - 7):
						
						if high[a] == max(high[a - 5: a + 1]) and \
							high[a] == max(high[a: a + 6]):
							
							for b in range(a + level_window, request_limit_length - 7):
								
								if high[b] == max(high[b - 5: b + 1]) and \
									high[b] == max(high[b: b + 6]) and \
									high[a] + avg_atr >= high[b] >= high[a] - avg_atr and \
									max([high[a], high[b]]) == max(high[a: b+1]):
									
									for c in range(b + level_window, request_limit_length - 7):
										
										if high[c] == max(high[c - 5: c + 1]) and \
											high[c] == max(high[c: c + 6]) and \
											high[b] + avg_atr >= high[c] >= high[b] - avg_atr and \
											max([high[b], high[c]]) == max(high[b: request_limit_length]):
											
											lowest_resistance = min([high[a], high[b], high[c]])
											distance = abs(high[-1] - lowest_resistance) / (lowest_resistance / 100)
											distance = float('{:.2f}'.format(distance))
											
											if high[-1] <= lowest_resistance and \
												distance <= distance_filter and \
												distance < dist_to_high and \
												high[a] >= high[b] >= high[c]:

												higher_high = f"{symbol}, res: {high[a]}❕{high[b]}❕{high[c]}, dist: {distance}%"
												dist_to_high = distance
											
						if low[a] == min(low[a - 5: a + 1]) and \
							low[a] == min(low[a: a + 6]):
							
							for b in range(a + level_window, request_limit_length - 7):
								
								if low[b] == min(low[b - 5: b + 1]) and \
									low[b] == min(low[b: b + 6]) and \
									low[a] + avg_atr >= low[b] >= low[a] - avg_atr and \
									min([low[a], low[b]]) == min(low[a: b + 1]):
									
									for c in range(b + level_window, request_limit_length - 7):
										
										if low[c] == min(low[c - 5: c + 1]) and \
											low[c] == min(low[c: c + 6]) and \
											low[b] + avg_atr >= low[c] >= low[b] - avg_atr and \
											min([low[b], low[c]]) == min(low[b: request_limit_length]):
											
											highest_support = max([low[a], low[b], low[c]])
											distance = abs(low[-1] - highest_support) / (highest_support / 100)
											distance = float('{:.2f}'.format(distance))
											
											if low[-1] >= highest_support and \
												distance <= distance_filter and \
												distance < dist_to_low and \
												low[a] <= low[b] <= low[c]:
												
												lower_low = f"{symbol}, sup: {low[a]}❕{low[b]}❕{low[c]}, dist: {distance}%"
												dist_to_low = distance
												
					if higher_high:

						print(higher_high)
						s_queue.put(higher_high)
					
					if lower_low:

						print(lower_low)
						s_queue.put(lower_low)

					# 	screenshoter_send(symbol, open, high, low, close, f"{symbol} ({frame}), BBSh, density: {int(density)}")

def printer(s_queue):
	
	message = ""
	
	while not s_queue.empty():
		data = s_queue.get()
		message += str(data) + "\n"
	
	if message:
		bot1.send_message(662482931, message)

if __name__ == '__main__':
	
	proc = 15
	gap_filter = float(input("Max gap filter (def. 0.2%): ") or 0.2)
	density_filter = int(input("Density filter (def. 30): ") or 30)
	tick_size_filter = float(input("Ticksize filter (def. 0.05%): ") or 0.05)
	atr_per_filter = float(input("ATR% filter (def. 0.3%): ") or 0.3)
	level_window = int(input("Window between lvls (def. 24): ") or 24)
	distance_filter = float(input("Distance filter (def. 1%): ") or 1)

	
	bot1.send_message(662482931,
	                  f"Processes = {proc} \n\n"
	                  f"Gap filter = {gap_filter}% \n"
	                  f"Density filter = {density_filter} \n"
	                  f"Tick size filter = {tick_size_filter}% \n"
	                  f"ATR% filter = {atr_per_filter}\n\n"

	                  f"Window between lvls = {level_window} candles \n"
	                  f"Distance filter = {distance_filter}%\n\n"
	                  f"💵💵💵💵💵"
					)
	
	def waiting():
		
		while True:
			now = datetime.now()
			last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(0.1)
			
			# Перевірка в 04:15 , 09:30 , 14:45 ....
			if (int(last_minute_digit) + 1) % 15 == 0:
				if int(last_second_digit) == 20:
					break

	while True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		frame = "5m"
		time1 = time.perf_counter()
		
		pairs = binance_pairs(
			chunks=proc,
			quote_assets=["USDT"],
			day_range_filter=2,
			day_density_filter=density_filter,
			tick_size_filter=tick_size_filter
		)
		
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs on {frame}")
		print(f">>>")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search,
			                  args=(
				                  pairs[proc_number],
			                      frame,
			                      gap_filter,
			                      density_filter,
			                      level_window,
			                      distance_filter,
			                      atr_per_filter,
			                      shared_queue,
			                      ))
			the_processes.append(process)
		
		print_process = Process(target=printer, args=(shared_queue, ))
		the_processes.append(print_process)
			
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()
			
		printer(shared_queue)
			
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"<<<")
		print(f"Finished search in {int(time3)} seconds")
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print("")
		
		waiting()
		