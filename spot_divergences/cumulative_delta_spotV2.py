import time
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV2 import binance_pairs

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(filtered_symbols, binance_frame, request_limit_length, distance_to_low, gap_filter):
	
	for symbol in filtered_symbols:
		binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}'
		binance_klines = requests.get(binance_klines)
		
		if binance_klines.status_code == 200:
			response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
			if response_length == request_limit_length:
				binance_candle_data = binance_klines.json()
				timestamp = list(float(i[0]) for i in binance_candle_data)
				open = list(float(i[1]) for i in binance_candle_data)
				high = list(float(i[2]) for i in binance_candle_data)
				low = list(float(i[3]) for i in binance_candle_data)
				close = list(float(i[4]) for i in binance_candle_data)
				volume = list(float(i[5]) for i in binance_candle_data)
				buy_volume = list(float(i[9]) for i in binance_candle_data)
				
				max_gap = 0
				cumulative_delta = [int(buy_volume[0] - (volume[0] - buy_volume[0]))]
				
				for i in range(1, len(close)):
					gap = abs(open[i] - close[i - 1])
					gap_p = 0
					if open[i] != 0: gap_p = gap / (open[i] / 100)
					if gap_p > max_gap: max_gap = gap_p
					
					b_vol = buy_volume[i]
					s_vol = volume[i] - buy_volume[i]
					new_delta = b_vol - s_vol
					new_delta = cumulative_delta[-1] + new_delta
					cumulative_delta.append(int(new_delta))
				
				max_gap = float('{:.2f}'.format(max_gap))
				
				# last_cd_low_index = None
				# last_cd_low_value = None
				last_lowerlow_index = None
				last_lowerlow_value = None
				
				for i in range(5, len(low) - 7):
					
					# 	if cumulative_delta[i] == min(list(cumulative_delta[i-5 : i+6])):
					# 		last_cd_low_index = i
					# 		last_cd_low_value = cumulative_delta[i]
					
					if low[i] == min(list(low[i - 5: i + 6])):
						last_lowerlow_index = i
						last_lowerlow_value = low[i]
				
				if last_lowerlow_value:  # and last_cd_low_value:
					
					# clean_cd_vector = True
					clean_low_vector = True
					
					# for i in range(last_cd_low_index+1, len(cumulative_delta)-1):
					# 	if cumulative_delta[i] < cumulative_delta[last_cd_low_index]:
					# 		clean_cd_vector = False
					
					for i in range(last_lowerlow_index + 1, len(low) - 1):
						if low[i] < low[last_lowerlow_index]:
							clean_low_vector = False
					
					dist_to_low = (low[-1] - last_lowerlow_value) / (low[-1] / 100)
					dist_to_low = float('{:.2f}'.format(dist_to_low))
					
					price_range = abs(max(high) - min(low)) / (close[-1] / 100) if close[-1] != 0 else 0
					price_range = float('{:.2f}'.format(price_range))
					
					if max_gap <= gap_filter and \
						clean_low_vector and \
						dist_to_low > distance_to_low and \
						cumulative_delta[-1] == min(cumulative_delta):
						print(f"{symbol} ({binance_frame}), \n"
				        f"range: {price_range}%, \n"
				        f"dist to low: {dist_to_low}%, \n"
				        f"gap: {max_gap}%")
				
						bot1.send_message(662482931, f"{symbol} ({binance_frame}): range {price_range}%, gap {max_gap}%")


if __name__ == '__main__':
	print("PARAMETERS:")
	price_filter = float(input("Price filter (def. 0.0000001): ") or 0.0000001)
	binance_frame = str(input("Timeframe (def. 5m): ") or "5m")
	request_limit_length = int(input("Request length (def. 92): ") or 92)
	distance_to_low = float(input("Distance to low (def. 0.5): ") or 0.5)
	gap_filter = float(input("Gap filter (def. 0.1): ") or 0.1)
	sleep_time = int(input("Sleep time (def. 5): ") or 5) * 60
	proc = int(input("Processes (def. 8): ") or 8)
	
	bot1.send_message(662482931, f"STARTING WITH:\n"
	        f"price_filter = {price_filter}, \n"
			f"binance_frame = {binance_frame}, \n"
			f"request_limit_length = {request_limit_length} candles, \n"
			f"distance_to_low = {distance_to_low}%, \n"
			f"gap_filter = {gap_filter}%, \n"
			f"sleep_time = {sleep_time} seconds, \n"
			f"Processes = {proc}")
	
	print("")
	
	while True:
		time1 = time.perf_counter()
		pairs = binance_pairs(proc, price_filter)
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search, args=(pairs[proc_number], binance_frame, request_limit_length, distance_to_low, gap_filter,))
			the_processes.append(process)
		
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"Finished search in {int(time3)} seconds")
		print("")
		
		time.sleep(sleep_time)