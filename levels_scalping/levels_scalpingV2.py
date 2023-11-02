import time
from datetime import datetime
from multiprocessing import Process, Manager
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
		tick_size_filter,
		atr_per_filter,
		trades_k_filter,
		s_queue,
		search_distance,
		levels_scatter
		):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		request_limit_length = 200
		
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
				trades = list(int(i[8]) for i in binance_candle_data)
				buy_volume = list(float(i[9]) for i in binance_candle_data)
				sell_volume = [volume[0] - buy_volume[0]]
				max_gap = 0
				
				# ==== GAP, SELL.V, 1H DENSITY ====
				for curr_index in range(1, len(close)):
					gap = abs(open[curr_index] - close[curr_index - 1])
					gap_p = 0
					if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
					if gap_p > max_gap: max_gap = gap_p

					s_v = volume[curr_index] - buy_volume[curr_index]
					sell_volume.append(s_v)
					
				max_gap = float('{:.3f}'.format(max_gap))
				density = [(x - y) / tick_size for x, y in zip(high, low)]
				density = sum(density) / len(density)
				
				# ==== AVERAGE ATR % ====
				avg_atr_per = [(high[-c] - low[-c]) / (close[-c] / 100) for c in range(60)]
				avg_atr_per = float('{:.2f}'.format(sum(avg_atr_per) / len(avg_atr_per)))
				
				# ==== VOLUME DYNAMIC ====
				volume_dynamic = None
				if len(volume) == request_limit_length:
					first_period_volume = sum(volume[-60:-1])
					second_period_volume = sum(volume[-120:-60])
					third_period_volume = sum(volume[-180:-120])
					
					if first_period_volume >= second_period_volume >= third_period_volume > 0:
						volume_dynamic = "Rising"
					elif 0 < first_period_volume <= second_period_volume <= third_period_volume:
						volume_dynamic = "Falling"
					else:
						volume_dynamic = "Neutral"
				
				# ==== THOUSANDS TRADES ====
				trades_k = int(sum(trades) / 1000)
				
				# ==== TICKSIZE % ====
				ts_percent = tick_size / (close[-1] / 100)
				ts_percent = float('{:.3f}'.format(ts_percent))
				
				if int(datetime.now().strftime('%M')) == 0 and symbol == "BTCUSDT":
					s_queue.put(f"{symbol}: {trades_k}K on {request_limit_length} candles")
					
				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and \
					density >= density_filter and \
					avg_atr_per >= atr_per_filter and \
					trades_k >= trades_k_filter and \
					len(high) == len(low) == request_limit_length:
					
					# print(f"{symbol}, gap {max_gap}%, dens {int(density)}, atr {avg_atr_per}%, tick {ts_percent}%, trades {trades_k}K, vol {volume_dynamic}%")
					# print(f"{symbol}, trades {trades_k}K")
					
					to_res = 100
					higher_high = ""
					
					to_sup = 100
					lower_low = ""
					
					information = (f"{ts_percent}% ticksize, \n"
					               f"{int(density)} density, \n"
					               f"{trades_k}K trades, \n"
					               f"{avg_atr_per}% hour ATR, \n"
					               f"{volume_dynamic} volume")
					
					# =============== RESISTANCE на ДВОХ точках
					for a in range(3, 120):
						if high[-a] == max(high[-1: -a - 4: -1]):
							
							for b in range(a + 4, 120):
								
								distance = abs(close[-1] - max(high[-a], high[-b])) / (max(high[-a], high[-b]) / 100)
								distance = float('{:.2f}'.format(distance))
								
								if abs(high[-a] - high[-b]) <= close[-1] * levels_scatter and \
									max(high[-a], high[-b]) == max(high[-1: -b - 11: -1]) and \
									distance <= search_distance and distance < to_res:
									
									to_res = distance
									higher_high = (
										f"{symbol}: ‼️ resistance in {distance}%, \n"
										f"{max(high[-a], high[-b])} level, \n" +
										information
									)
					
					# =============== SUPPORT на ДВОХ точках
					for a in range(3, 120):
						if low[-a] == min(low[-1: -a - 4: -1]):
							
							for b in range(a + 4, 120):
								
								distance = abs(close[-1] - min(low[-a], low[-b])) / (close[-1] / 100)
								distance = float('{:.2f}'.format(distance))
							
								if abs(low[-a] - low[-b]) <= close[-1] * levels_scatter and \
									min(low[-a], low[-b]) == min(low[-1: -b - 11: -1]) and \
									distance <= search_distance and distance < to_sup:
									
									to_sup = distance
									lower_low = (
										f"{symbol}: ‼️ support in {distance}%, \n"
										f"{min(low[-a], low[-b])} level, \n" +
										information
									)
					
					
					for h in range(10, 122, 10):
						
						# =============== RESISTANCE на КАНАЛІ
						highs = high[-1: -h: -1]
						highs = sorted(highs, reverse=True)
						
						if (max(highs[0: 5]) - min(highs[0:5])) <= close[-1] * levels_scatter and min(highs[0:5]) > high[-1]:
							distance = (min(highs[0:5]) - high[-1]) / (close[-1] / 100)
							distance = float('{:.2f}'.format(distance))
							
							if distance <= search_distance and distance < to_res:
								higher_high = (
									f"{symbol}: 〽️ resistance in {distance}%, \n"
									f"{max(highs[0: 5])} level, \n" +
									information
								)
						
						# =============== SUPPORT на КАНАЛІ
						lows = low[-1: -h: -1]
						lows = sorted(lows, reverse=False)
						
						if (max(lows[0: 5]) - min(lows[0:5])) <= close[-1] * levels_scatter and max(lows[0:5]) < low[-1]:
							distance = (low[-1] - max(lows[0:5])) / (close[-1] / 100)
							distance = float('{:.2f}'.format(distance))
							
							if distance <= search_distance and distance < to_res:
								lower_low = (
									f"{symbol}: 〽️ support in {distance}%, \n"
									f"{min(lows[0:5])} level, \n" +
									information
								)
					
					# =============== RESISTANCE від ЕКСТРЕМУМА
					if max(high[-1: -10: -1]) == max(high) and max(high[-1: -10: -1]) > high[-1]:
						distance = abs(max(high[-1: -10: -1]) - high[-1]) / (close[-1] / 100)
						distance = float('{:.2f}'.format(distance))
						
						if distance <= search_distance and distance < to_res:
							higher_high = (
								f"{symbol}: 🔥 resistance in {distance}%, \n"
								f"{max(high[-1: -10: -1])} level, \n" +
								information
							)
					
					# # =============== SUPPORT на ЕКСТРЕМУМІ
					# if min(low[-1: -10: -1]) == min(low) and min(low[-1: -10: -1]) < low[-1]:
					# 	distance = abs(min(low[-1: -10: -1]) - low[-1]) / (close[-1] / 100)
					# 	distance = float('{:.2f}'.format(distance))
					#
					# 	if distance <= search_distance and distance < to_res:
					# 		lower_low = (
					# 			f"{symbol}: 🔥 support in {distance}%, \n"
					# 			f"{min(low[-1: -10: -1])} level, \n" +
					#			information
					# 		)
							
					if higher_high:
						s_queue.put(higher_high)
					
					if lower_low:
						s_queue.put(lower_low)


def printer(s_queue):
	
	# message = ""
	
	while not s_queue.empty():
		data = s_queue.get()
		# message += "\n" + str(data) + "\n"
		bot1.send_message(662482931, str(data))
	
	# if message:
	# 	print(message)
		# bot1.send_message(662482931, message)

if __name__ == '__main__':
	
	
	proc = 14
	gap_filter = 0.5 # float(input("Max gap filter (def. 0.2%): ") or 0.2)
	density_filter = 20 # int(input("Density filter (def. 30): ") or 30)
	tick_size_filter = 0.1 # float(input("Ticksize filter (def. 0.03%): ") or 0.03)
	atr_per_filter = 0.30 # float(input("ATR% filter (def. 0.3%): ") or 0.3)
	trades_k_filter = 100 # int(input("Trades filter (def. 100): ") or 100)
	search_distance = 1
	levels_scatter = 0.03 / 100
	
	# print(f"\n"
	#       f"Processes = {proc} \n"
    #       f"Gap filter = {gap_filter}% \n"
    #       f"Density filter = {density_filter} \n"
    #       f"Tick size filter = {tick_size_filter}% \n"
    #       f"ATR% filter = {atr_per_filter}% \n"
    #       f"Trades = {trades_k_filter}K \n"
	# 	)
	
	# bot1.send_message(662482931,
	#                   f"Processes = {proc} \n\n"
	#                   f"Gap filter = {gap_filter}% \n"
	#                   f"Density filter = {density_filter} \n"
	#                   f"Tick size filter = {tick_size_filter}% \n"
	#                   f"ATR% filter = {atr_per_filter}% \n"
	#                   f"Trades = {trades_k_filter}K \n\n"
	#                   f"💵💵💵💵💵"
	# 				)
	
	def waiting():
		
		while True:
			now = datetime.now()
			last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(1)
			
			# Перевірка в 04:15 , 09:30 , 14:45 ....
			if int(last_second_digit) == 0:
				break

	while True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		frame = "1m"
		time1 = time.perf_counter()
		
		pairs = binance_pairs(proc - 1, ["USDT"], 2, density_filter, tick_size_filter)
		
		print(f">>> {datetime.now().strftime('%H:%M:%S')} / {sum(len(inner_list) for inner_list in pairs)} pairs")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search,
			                  args=(
				                  pairs[proc_number],
			                      frame,
			                      gap_filter,
			                      density_filter,
				                  tick_size_filter,
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
		
		printer(shared_queue)
			
		time2 = time.perf_counter()
		time3 = time2 - time1

		print(f"<<< {datetime.now().strftime('%H:%M:%S')} / {int(time3)} seconds")
		print("")
		
		waiting()
		