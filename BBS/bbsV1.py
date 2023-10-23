import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV3 import binance_pairs
from screenshoter import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(
		filtered_symbols,
		frame,
		gap_filter,
		density_filter,
		calculate_length,
		range_mp,
		curr_brr_filter
		
):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		# frame = "5m"
		request_limit_length = 100

		
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
				density = (high[-1] - low[-1]) / tick_size
			
				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and density >= density_filter and len(high) == len(low) == request_limit_length:
					
					# ==== BBS SEARCH ====
					current_brr = abs(open[-1] - close[-1]) / ((high[-1] - low[-1]) / 100)
					current_range = high[-1] - low[-1]
					ranges_list = []
					for ra in range(2, calculate_length):
						ranges_list.append((high[-ra] - low[-ra]) * range_mp)
					
					if current_range >= max(ranges_list) and current_brr >= curr_brr_filter:
						
						bot1.send_message(662482931, f"#{symbol} ({frame}), density: {int(density)}")
						screenshoter_send(symbol, open, high, low, close, f"{symbol} ({frame}), density: {int(density)}")
						print(f"{symbol} ({frame}), density: {int(density)}")
				
					# ==== PIN SEARCH ====
					bull_pin = min(close[-1], open[-1]) >= (high[-1] - (high[-1] - low[-1]) / 4)
					bear_pin = max(close[-1], open[-1]) <= (low[-1] + (high[-1] - low[-1]) / 4)
					
					brr1 = abs(open[-2] - close[-2]) / ((high[-2] - low[-2]) / 100) >= curr_brr_filter
					brr2 = abs(open[-3] - close[-3]) / ((high[-3] - low[-3]) / 100) >= curr_brr_filter
					brr3 = abs(open[-4] - close[-4]) / ((high[-4] - low[-4]) / 100) >= curr_brr_filter
					
					if brr1 and brr2 and brr3 and (bull_pin or bear_pin):
						
						bot1.send_message(662482931, f"#{symbol} ({frame}), density: {int(density)}")
						screenshoter_send(symbol, open, high, low, close, f"{symbol} ({frame}), density: {int(density)}")
						print(f"{symbol} ({frame}), density: {int(density)}")

if __name__ == '__main__':
	print("PARAMETERS:")
	proc = 16
	gap_filter = 0.8
	density_filter = 20
	tick_size_filter = 0.1
	
	timeframes = []

	while True:
		value = input("Frames: ")
		if value.lower() == 's':
			break
		timeframes.append(value)
	
	range_range_filter = float(input("Range range (def. 1.0): ") or 1.0)
	calculate_length = int(input("Calculate lenght (def. 24): ") or 24)
	range_mp = float(input("Range multiplier (def. 1.2): ") or 1.2)
	curr_brr_filter = int(input("Current BR-ratio (def. 66): ") or 66)
	print("")
	
	bot1.send_message(662482931,
	                  f"Processes = {proc} \n\n"
	                  f"Gap filter = {gap_filter}% \n"
	                  f"Density filter = {density_filter} \n"
	                  f"Tick size filter = {tick_size_filter}% \n"
	                  f"Frames = {timeframes}\n\n"
	                  f"Daily range filter = {range_range_filter} \n"
	                  f"Calculate lenght = {calculate_length} \n"
	                  f"Range multiplier = {range_mp} \n"
	                  f"Current BR-ratio = {curr_brr_filter} \n\n"
	                  f"💵💵💵💵💵"
					)
	
	def waiting(timeframes):
		
		while True:
			now = datetime.now()
			last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(0.1)
			
			# Перевірка в 04:20 , 09:20 , 14:20 ....
			if "5m" in timeframes and (int(last_minute_digit) + 1) % 5 == 0:
				if int(last_second_digit) == 20:
					return "5m"
			
			# Перевірка в 13:40 , 28:40 , 43:40 , 58:40
			if "15m" in timeframes and (int(last_minute_digit) + 2) % 15 == 0:
				if int(last_second_digit) == 40:
					return "15m"
			
			# Перевірка в 28:00 , 58:00
			if "30m" in timeframes and (int(last_minute_digit) + 2) % 30 == 0:
				if int(last_second_digit) == 0:
					return "30m"

			# Перевірка в 57:20
			if "1h" in timeframes and (int(last_minute_digit) + 3) == 60:
				if int(last_second_digit) == 20:
					return "1h"

			# Перевірка в 16:56:40
			if "2h" in timeframes and int(last_hour_digit) % 2 == 0:
				if (int(last_minute_digit) + 4) == 60:
					if int(last_second_digit) == 40:
						return "2h"
				
	while True:
		
		frame = waiting(timeframes)
		time1 = time.perf_counter()
		
		pairs = binance_pairs(
			chunks=proc,
			quote_assets=["USDT"],
			day_range_filter=range_range_filter,
			day_density_filter=density_filter,
			tick_size_filter=tick_size_filter
		)
		
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs on {frame}")
		print(f">>>")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search,
			                  args=(pairs[proc_number],
			                        frame,
			                        gap_filter,
			                        density_filter,
			                        calculate_length,
			                        range_mp,
			                        curr_brr_filter
			                        )
			                  )
			the_processes.append(process)
			
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()
			
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"<<<")
		print(f"Finished search in {int(time3)} seconds")
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print("")
		