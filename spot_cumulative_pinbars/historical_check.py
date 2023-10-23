import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
import telebot
from spot_divergences.module_get_pairs_binanceV2 import binance_pairs

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

# end_date_timestamp = datetime(2023, 10, 5).timestamp()
# end_date = datetime.fromtimestamp(end_date_timestamp)
# hours_to_add = 9  # +++++++++++++++++++++++++
# minutes_to_add = 0  # +++++++++++++++++++++++++
# time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
# new_date = end_date + time_to_add
# end_date = new_date.timestamp() * 1000

def search(filtered_symbols, binance_frame, request_limit_length, body_percent_filter, total_range_filter, pin_close_part, gap_filter, tick_size_filter, room_to_the_left):
	
	for symbol in filtered_symbols:
		# binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_length}&endTime={int(end_date)}'
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
				sell_volume = [volume[0] - buy_volume[0]]
				cumulative_delta = [int(buy_volume[0] - (volume[0] - buy_volume[0]))]
				max_gap = 0
				for i in range(1, len(close)):
					gap = abs(open[i] - close[i-1])
					gap_p = 0
					if open[i] !=0: gap_p = gap / (open[i] / 100)
					if gap_p > max_gap: max_gap = gap_p
					
					b_vol = buy_volume[i]
					s_vol = volume[i] - buy_volume[i]
					sell_volume.append(s_vol)
					
					new_delta = b_vol - s_vol
					new_delta = cumulative_delta[-1] + new_delta
					cumulative_delta.append(int(new_delta))
				max_gap = float('{:.2f}'.format(max_gap))


				for i in range(room_to_the_left+1, len(close)-room_to_the_left-1):
					for b in range(2, 24):
						pin_open = open[i-b]
						pin_high = max(high[i:i-b-1:-1])
						pin_low = min(low[i:i-b-1:-1])
						pin_close = close[i]
						# ==== binance ticksize ====
						bin_all_ticks = list(open[i:i-room_to_the_left:-1]) + \
						                list(high[i:i-room_to_the_left:-1]) + \
						                list(low[i:i-room_to_the_left:-1]) + \
						                list(close[i:i-room_to_the_left:-1])
						bin_all_ticks = sorted(bin_all_ticks)
						bin_diffs = 10
						
						for u in range(1, len(bin_all_ticks) - 1):
							if 0 < bin_all_ticks[-u] - bin_all_ticks[-u - 1] < bin_diffs:
								bin_diffs = bin_all_ticks[-u] - bin_all_ticks[-u - 1]
						binance_tick_size = float('{:.4f}'.format(bin_diffs / (close[i] / 100)))
						
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
								pin_low <= min(low[i:i-room_to_the_left:-1]) and \
								binance_tick_size <= tick_size_filter:
								
								# print(
								# 	f"{symbol}, "
								#     f"coordinate {request_length - i} candles back, "
								#     f"[{pin_open}-{pin_high}-{pin_low}-{pin_close}], "
								#     f"max gap {max_gap}%, "
								#     f"body_percent {int(body_percent)}%, "
								#     f"close whithin 1/{pin_close_part} from high, "
								#     f"pin total range {total_range}%, "
								#     f"room to the left {room_to_the_left}, "
								#     f"tick size {binance_tick_size}%"
								# )
								
								closed = False
								for fin in range(i+1, len(close)):
									tp = pin_close + abs(pin_close - pin_low)
									sl = pin_low
									if high[fin] >= tp >= low[fin]:
										print(
											f"{symbol}, "
											f"{request_limit_length - i}, "
											f"{b}, "
											f"[{pin_open}-{pin_high}-{pin_low}-{pin_close}], "
											f"{total_range}, "
											f"PROFIT")
										closed = True
										break
									elif high[fin] >= sl >= low[fin]:
										print(
											f"{symbol}, "
											f"{request_limit_length - i}, "
											f"{b}, "
											f"[{pin_open}-{pin_high}-{pin_low}-{pin_close}], "
											f"{total_range}, "
											f"LOSS")
										closed = True
										break
										
								if not closed: print(
									f"{symbol}, "
									f"{request_limit_length - i}, "
									f"{b}, "
									f"[{pin_open}-{pin_high}-{pin_low}-{pin_close}], "
									f"{total_range}, "
									f"never closed...")



if __name__ == '__main__':
	print("PARAMETERS:")
	price_filter = float(input("Price filter (def. 0.000000001): ") or 0.000000001)
	
	binance_frame = str(input("Timeframe (def. 5m): ") or "5m")
	request_limit_length = int(input("Request length (def. 384): ") or 384)
	body_percent_filter = int(input("Body percent (def. 20): ") or 20)
	pin_close_part = int(input("Close at part (def. 5): ") or 5)
	total_range_filter = float(input("Pin range (def. 1.0): ") or 1.0)
	gap_filter = float(input("Max gap (def. 0.05): ") or 0.1)
	tick_size_filter = float(input("Max tick size (def. 0.1): ") or 0.1)
	room_to_the_left = int(input("Room to the left (def. 48): ") or 48)
	proc = int(input("Processes (def. 16): ") or 16)
	sleep_time = int(input("Sleep minutes (def. 5): ") or 5) * 60

	print("")
	
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
		
		time.sleep(sleep_time)