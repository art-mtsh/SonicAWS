import threading
import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV2 import binance_pairs

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)


end_date_timestamp = datetime(2023, 10, 4).timestamp()
end_date = datetime.fromtimestamp(end_date_timestamp)
hours_to_add = 8  # +++++++++++++++++++++++++
minutes_to_add = 25  # +++++++++++++++++++++++++
time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
new_date = end_date + time_to_add
end_date = new_date.timestamp() * 1000

def search(filtered_symbols, binance_frame, request_limit_length, distance_to_low, gap_filter):
	
	for symbol in filtered_symbols:
		binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}'
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
				cumulative_delta = {}
				new_delta = 0
		
				for i in range(1, len(close)):
					gap = abs(open[i] - close[i-1])
					gap_p = 0
					if open[i] !=0: gap_p = gap / (open[i] / 100)
					if gap_p > max_gap: max_gap = gap_p
					
					b_vol = buy_volume[i]
					s_vol = volume[i] - buy_volume[i]
					new_delta += b_vol - s_vol
					cumulative_delta[i] = new_delta
				
				max_gap = float('{:.2f}'.format(max_gap))
				lowest_cd_index = min(cumulative_delta, key=cumulative_delta.get)
				lowest_low_index = lowest_cd_index
				
				for i in range(lowest_cd_index, len(low) - 1):
					if low[lowest_low_index] > low[i]:
						lowest_low_index = i
				
				dist_to_low = (low[-1] - low[lowest_low_index]) / (low[-1] / 100)
				dist_to_low = float('{:.2f}'.format(dist_to_low))
				
				price_range = abs(max(high) - min(low)) / (close[-1] / 100) if close[-1] != 0 else 0
				price_range = float('{:.2f}'.format(price_range))
				
				if dist_to_low >= distance_to_low and \
					cumulative_delta.get(request_limit_length - 1) <= cumulative_delta.get(lowest_cd_index) and \
					max_gap <= gap_filter:
					print(f"{symbol} ({binance_frame}): price range = {price_range}%, {low[-1]} > {low[lowest_low_index]} ({dist_to_low}%)")
					# bot1.send_message(662482931, f"{symbol} ({binance_frame}): price range = {price_range}%, {low[-1]} > {low[lowest_low_index]} ({dist_to_low}%)")

if __name__ == '__main__':
	print("PARAMETERS:")
	price_filter = 0.000001 # float(input("Price filter: "))
	binance_frame = "5m" # str(input("Timeframe (1h, 30m, 15m, 5m, 1m): "))
	request_limit_length = 72 # int(input("Request length, bars: "))
	distance_to_low = 0.05 # float(input("Distance to low, %: "))
	gap_filter = 0.1 # float(input("Gap filter, %: "))
	sleep_time = 10000 # int(input("Sleep time, minutes: ")) * 60
	threads = 8 # int(input("Threads: "))
	
	print(f"STARTING WITH:\n"
	        f"price_filter = {price_filter}, \n"
			f"binance_frame = {binance_frame}, \n"
			f"request_limit_length = {request_limit_length} candles, \n"
			f"distance_to_low = {distance_to_low}%, \n"
			f"gap_filter = {gap_filter}%, \n"
			f"sleep_time = {sleep_time} seconds")
	
	print("")
	
	while True:
		time1 = time.perf_counter()
		pairs = binance_pairs(threads, price_filter)
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(threads):
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