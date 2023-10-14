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
		gap_filter,
		density_filter,
		lengthdiver_filter,
		extremum_window_filter,
		room_filter,
		range_range_filter,
		pin_range_filter,
		pin_part_filter
):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		frame = "5m"
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
					max_gap <= gap_filter and density >= density_filter:
					
					# ==== PIN SEARCH ====
					range_perc_range = (max(high[-1: - lengthdiver_filter - 1: -1]) - min(low[-1: - lengthdiver_filter - 1: -1])) / (max(high[-1: - lengthdiver_filter - 1: -1]) / 100) >= range_range_filter
					pin_perc_range = (high[-1] - low[-1]) / (high[-1] / 100) >= pin_range_filter
					
					bull_pin = min(close[-1], open[-1]) >= (high[-1] - (high[-1] - low[-1]) / pin_part_filter)
					bear_pin = max(close[-1], open[-1]) <= (low[-1] + (high[-1] - low[-1]) / pin_part_filter)
					
					bull_room = low[-1] == min(low[-1: -room_filter - 1: -1])
					bear_room = high[-1] == max(high[-1: -room_filter - 1: -1])
					
					highest_high_room = max(high[-1: -extremum_window_filter - 1: -1]) == max(high[-1: - lengthdiver_filter - extremum_window_filter - 1: -1]) and \
					                    high[-1] != max(high[-1: -extremum_window_filter - 1: -1])
					
					lowest_low_room = min(low[-1: -extremum_window_filter - 1: -1]) == min(low[-1: - lengthdiver_filter - extremum_window_filter - 1: -1]) and \
					                  high[-1] != min(low[-1: -extremum_window_filter - 1: -1])
					
					volume_scheme: str

					if volume[-1] > volume[-2] > volume[-3]:
						volume_scheme = "✅✅"
					elif volume[-1] > volume[-2]:
						volume_scheme = "✅◻️️"
					else:
						volume_scheme = "◻️️◻️"

					if density > 200:
						density_scheme = "✅✅"
					elif 200 >= density > 100:
						density_scheme = "✅◻️️"
					else:
						density_scheme = "◻️️◻️"
					
					# ===== PIN DEFINITION =====
					if range_perc_range and pin_perc_range and (
							(bull_pin and bull_room and highest_high_room)
							or
							(bear_pin and bear_room and lowest_low_room)
					):
						
						message_ss = f"{symbol} 48-range: {range_perc_range}%. Pin: {pin_perc_range}%. Density: {int(density)}"
						
						bot1.send_message(662482931,
						                  f"#{symbol} 48-range: {range_perc_range}%\n"
						                  f"Pin: {pin_perc_range}% \n"
						                  f"{volume_scheme} volume \n"
						                  f"{density_scheme} density: {int(density)}"
						                  )
						
						screenshoter_send(symbol, open, high, low, close, message_ss)
						print(message_ss)
					

if __name__ == '__main__':
	print("PARAMETERS:")
	proc = 16
	gap_filter = 0.5
	density_filter = 20
	tick_size_filter = 0.1
	lengthdiver_filter = int(input("Donchian length (def. 48): ") or 48)
	extremum_window_filter = int(input("Extremum window search (def. 12): ") or 12)
	room_filter = int(input("Pin room t/t left (def. 6): ") or 6)
	range_range_filter = float(input("Range range (def. 1.0): ") or 1.0)
	pin_range_filter = float(input("Pin range (def. 0.1): ") or 0.1)
	pin_part_filter = int(input("Pin part (def. 2): ") or 2)
	print("")
	
	bot1.send_message(662482931,
	                  f"Processes = {proc} \n\n"
	                  f"Gap filter = {gap_filter}% \n"
	                  f"Density filter = {density_filter} \n\n"
	                  f"Tick size filter = {tick_size_filter}% \n"
	                  f"Donchian length = {lengthdiver_filter} \n"
	                  f"Extremum window search = {extremum_window_filter} \n"
	                  f"Pin room t/t left = {room_filter} \n"
	                  f"Donhian range = {range_range_filter}% \n\n"
	                  f"Pin range = {pin_range_filter}% \n"
	                  f"Pin part = {pin_part_filter} \n\n"
	                  f"💵💵💵💵💵"
					)
	
	def waiting():
		while True:
			now = datetime.now()
			# last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(0.1)
			
			if (int(last_minute_digit)+1) % 5 == 0:
				if int(last_second_digit) == 20:
					break
				
	while True:
		
		time1 = time.perf_counter()
		pairs = binance_pairs(chunks=proc, quote_assets=["USDT"], day_range_filter=range_range_filter, day_density_filter=density_filter, tick_size_filter=tick_size_filter)
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search, args=(pairs[proc_number], gap_filter, density_filter, lengthdiver_filter, extremum_window_filter, room_filter, range_range_filter, pin_range_filter, pin_part_filter,))
			the_processes.append(process)
			
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
			
		for pro in the_processes:
			pro.close()
			
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"Finished search in {int(time3)} seconds")
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print("")
		
		waiting()
