import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV2 import binance_pairs


TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)


def search(filtered_symbols, request_limit_length, body_percent_filter, total_range_filter, pin_close_part, gap_filter, tick_size_filter, room_to_the_left):
	
	for symbol in filtered_symbols:
		for frame in ["30m", "1h", "2h"]:
			
			now = datetime.now()
			last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			
			if frame == "1h":
				if int(last_minute_digit) > 45:
					pass
				else:
					continue
				
			if frame == "2h":
				if int(last_minute_digit) > 45 and int(last_hour_digit) % 2 == 0:
					pass
				else:
					continue
				
			binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
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
					
					# ==== gap and sell volume ====
					for curr_index in range(1, len(close)):
						gap = abs(open[curr_index] - close[curr_index - 1])
						gap_p = 0
						if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
						if gap_p > max_gap: max_gap = gap_p
	
						s_v = volume[curr_index] - buy_volume[curr_index]
						sell_volume.append(s_v)
					max_gap = float('{:.3f}'.format(max_gap))
					
					# ==== binance ticksize ====
					bin_all_ticks = sorted(open + high + low + close)
					bin_diffs = 10
					for u in range(1, len(bin_all_ticks) - 1):
						if 0 < bin_all_ticks[-u] - bin_all_ticks[-u - 1] < bin_diffs:
							bin_diffs = bin_all_ticks[-u] - bin_all_ticks[-u - 1]
					binance_tick_size = float('{:.3f}'.format(bin_diffs / (close[-1] / 100)))
					
					# ==== pin definition ====
					if open[-1] != 0 and high[-1] != 0 and low[-1] != 0 and close[-1] != 0 and max_gap <= gap_filter and binance_tick_size <= tick_size_filter:
					
						body_range = abs(open[-1] - close[-1])
						total_range = abs(high[-1] - low[-1]) if high[-1] != low[-1] else 0.0000001
						part = total_range / pin_close_part
						body_percent = body_range / (total_range / 100)
						total_range = float('{:.2f}'.format(total_range / (close[-1] / 100)))
						
						volume_scheme: str
						
						if volume[-1] > volume[-2] > volume[-3]: volume_scheme = "Strong rising"
						elif volume[-1] > volume[-2]: volume_scheme = "Rising"
						else: volume_scheme = "Casual"
						
						delta_1 = buy_volume[-1] - sell_volume[-1]
	
						if body_percent < body_percent_filter and \
							high[-1] >= close[-1] >= (high[-1] - part) and \
							total_range >= total_range_filter and \
							low[-1] <= min(low[-1:-room_to_the_left-1:-1]):
							
							print(
								f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}, "
								f"{symbol} ({frame}), "
							    f"[{open[-1]}-{high[-1]}-{low[-1]}-{close[-1]}], "
							    f"max gap {max_gap}%, "
							    f"body_percent {int(body_percent)}%, "
							    f"close whithin 1/{pin_close_part} from high, "
							    f"pin total range {total_range}%, "
							    f"room to the left {room_to_the_left}, "
							    f"tick size {binance_tick_size}%"
							)
							
							bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S')}: #{symbol} ({frame}),\n"
							                             f"{volume_scheme} volume, {'negative' if delta_1 <= 0 else 'positive'} delta,\n"
							                             f"Gap: {max_gap}%, tick: {binance_tick_size}%")
					
if __name__ == '__main__':
	print("PARAMETERS:")
	price_filter = 0.0 # float(input("Price filter (def. 0.000000001): ") or 0.000000001)
	request_limit_length = 300 # int(input("Request length (def. 384): ") or 384)
	body_percent_filter = int(input("Body percent (def. 20): ") or 20)
	pin_close_part = int(input("Close at part (def. 4): ") or 4)
	total_range_filter = float(input("Pin range (def. 0.5): ") or 0.5)
	gap_filter = 0.3 # float(input("Max gap (def. 0.3): ") or 0.3)
	tick_size_filter = 0.3 # float(input("Max tick size (def. 0.3): ") or 0.3)
	room_to_the_left = int(input("Room to the left (def. 1): ") or 1)
	proc = int(input("Processes (def. 8): ") or 8)
	print("")
	
	bot1.send_message(662482931, f"STARTING WITH:\n\n"
	        f"price_filter = {price_filter}, \n"
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
			# last_second_digit = now.strftime('%S')
			time.sleep(30)
			if int(last_minute_digit) == 55 or int(last_minute_digit) == 25:
				break
				
	while True:
		
		time1 = time.perf_counter()
		pairs = binance_pairs(proc, price_filter)
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search, args=(pairs[proc_number], request_limit_length, body_percent_filter, total_range_filter, pin_close_part, gap_filter, tick_size_filter, room_to_the_left, ))
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
