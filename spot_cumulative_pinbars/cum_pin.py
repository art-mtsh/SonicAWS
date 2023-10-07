import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV2 import binance_pairs
from queue import Queue

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(filtered_symbols, binance_frame, request_limit_length, body_percent_filter, total_range_filter, pin_close_part, gap_filter, tick_size_filter, room_to_the_left):
	
	for symbol in filtered_symbols:
		
		not_sent = True
		
		binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}'
		binance_klines = requests.get(binance_klines)
		
		if binance_klines.status_code == 200:
			response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
			if response_length == request_limit_length:
				binance_candle_data = binance_klines.json()
				open = list(float(i[1]) for i in binance_candle_data)
				high = list(float(i[2]) for i in binance_candle_data)
				low = list(float(i[3]) for i in binance_candle_data)
				close = list(float(i[4]) for i in binance_candle_data)
				volume = list(float(i[5]) for i in binance_candle_data)
				buy_volume = list(float(i[9]) for i in binance_candle_data)
				sell_volume = [volume[0] - buy_volume[0]]
				max_gap = 0
				for curr_index in range(1, len(close)):
					gap = abs(open[curr_index] - close[curr_index - 1])
					gap_p = 0
					if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
					if gap_p > max_gap: max_gap = gap_p

					s_v = volume[curr_index] - buy_volume[curr_index]
					sell_volume.append(s_v)
				max_gap = float('{:.2f}'.format(max_gap))
				
				curr_index = -1
				
				for b in range(24, 1, -1):
					pin_open = open[curr_index - b]
					pin_high = max(high[curr_index:curr_index - b:-1])
					pin_low = min(low[curr_index:curr_index - b:-1])
					pin_close = close[curr_index]
					pin_volume = sum(volume[curr_index:curr_index - b:-1])
					prev_pin_volume = sum(volume[curr_index - b:curr_index - b - b:-1])
					# ==== binance ticksize ====
					bin_all_ticks = sorted(open + high + low + close)
					bin_diffs = 10
					for u in range(1, len(bin_all_ticks) - 1):
						if 0 < bin_all_ticks[-u] - bin_all_ticks[-u - 1] < bin_diffs:
							bin_diffs = bin_all_ticks[-u] - bin_all_ticks[-u - 1]
					binance_tick_size = float('{:.4f}'.format(bin_diffs / (close[curr_index] / 100)))
					
					if pin_open != 0 and pin_high != 0 and pin_low != 0 and pin_close != 0:
					
						body_range = abs(pin_open - pin_close)
						total_range = abs(pin_high - pin_low) if pin_high != pin_low else 0.0000001
						part = total_range / pin_close_part
						body_percent = body_range / (total_range / 100)
						total_range = float('{:.2f}'.format(total_range / (pin_close / 100)))

						if max_gap <= gap_filter and \
							body_percent < body_percent_filter and \
							pin_high >= pin_close >= (pin_high - part) and \
							total_range >= total_range_filter and \
							pin_low <= min(low[curr_index:curr_index - b * room_to_the_left-1:-1]) and \
							binance_tick_size <= tick_size_filter and \
							not_sent:
							
							print(
								f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}, "
								f"{symbol}, "
							    f"[{pin_open}-{pin_high}-{pin_low}-{pin_close}], "
								f"cum pin of {b} candles, "
							    f"max gap {max_gap}%, "
							    f"body_percent {int(body_percent)}%, "
							    f"close whithin 1/{pin_close_part} from high, "
							    f"pin total range {total_range}%, "
							    f"room to the left {room_to_the_left}, "
							    f"tick size {binance_tick_size}%"
							)
							
							bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}\n"
							                             f"#{symbol}, "
							                             f"cum pin of {b} candles, "
							                             f"cv: {int(pin_volume/10000)}, pv {int(prev_pin_volume/10000)}")
							
							not_sent = False




if __name__ == '__main__':
	print("PARAMETERS:")
	price_filter = 0.000000001 # float(input("Price filter (def. 0.000000001): ") or 0.000000001)
	binance_frame = "5m" # str(input("Timeframe (def. 5m): ") or "5m")
	request_limit_length = 250 # int(input("Request length (def. 384): ") or 384)
	body_percent_filter = int(input("Body percent (def. 20): ") or 20)
	pin_close_part = int(input("Close at part (def. 4): ") or 4)
	total_range_filter = float(input("Pin range (def. 1): ") or 1)
	gap_filter = float(input("Max gap (def. 0.1): ") or 0.1)
	tick_size_filter = float(input("Max tick size (def. 0.1): ") or 0.1)
	room_to_the_left = int(input("Room to the left (def. 2): ") or 2)
	proc = int(input("Processes (def. 8): ") or 8)
	print("")
	
	bot1.send_message(662482931, f"STARTING WITH:\n\n"
	        f"price_filter = {price_filter}, \n"
			f"binance_frame = {binance_frame}, \n"
			f"request_limit_length = {request_limit_length} candles, \n"
			f"body_percent_filter = {body_percent_filter}%, \n"
			f"pin_close_part = 1/{pin_close_part}, \n"
			f"total_range_filter = {total_range_filter}%, \n"
			f"gap_filter = {gap_filter}%, \n"
            f"tick_size_filter = {tick_size_filter}%, \n"
            f"room_to_the_left = {room_to_the_left} pins, \n"
            f"proc = {proc} cores\n\n"
            f"💵💵💵💵💵"
	        )
	
	def waiting():
		while True:
			now = datetime.now()
			# last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(0.1)
			if int(last_second_digit) == 0:
				if int(last_minute_digit[-1]) == 4 or int(last_minute_digit[-1]) == 9:
					break
				
	while True:
		
		time1 = time.perf_counter()
		pairs = binance_pairs(proc, price_filter)
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search, args=(pairs[proc_number], binance_frame, request_limit_length, body_percent_filter, total_range_filter, pin_close_part, gap_filter, tick_size_filter, room_to_the_left, ))
			the_processes.append(process)
			
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()

		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"Finished search in {int(time3)} seconds")
		print("")
		
		waiting()
