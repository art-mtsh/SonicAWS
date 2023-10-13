import time
from datetime import datetime
from multiprocessing import Process
import requests
import telebot
from module_get_pairs_binanceV3 import binance_pairs
from screenshoter import screenshoter_send

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)


def search(filtered_symbols, request_limit_length, gap_filter, density_filter, body_percent_filter, pin_range_filter, pin_close_part):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]

		# for frame in ["30m", "1h", "2h"]:
		for frame in ["5m"]:
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
					
					# ==== gap and sell volume ====
					for curr_index in range(1, len(close)):
						gap = abs(open[curr_index] - close[curr_index - 1])
						gap_p = 0
						if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
						if gap_p > max_gap: max_gap = gap_p
	
						s_v = volume[curr_index] - buy_volume[curr_index]
						sell_volume.append(s_v)
					max_gap = float('{:.3f}'.format(max_gap))
					density = (high[-1] - low[-1]) / tick_size
				
					# ==== CURRENT CANDLE CHARACTERISTICS ====
					if open[-1] != 0 and high[-1] != 0 and \
						low[-1] != 0 and close[-1] != 0 and \
						max_gap <= gap_filter and density >= density_filter:
						
						body_range = abs(open[-1] - close[-1])
						total_range = abs(high[-1] - low[-1]) if high[-1] != low[-1] else 0.0000001
						part = total_range / pin_close_part
						body_percent = body_range / (total_range / 100)
						total_range = float('{:.2f}'.format(total_range / (close[-1] / 100)))
						
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
						
						buy_volume_power = int(buy_volume[-1] / (volume[-1] / 100)) if volume[-1] != 0 else 0
						sell_volume_power = int(sell_volume[-1] / (volume[-1] / 100)) if volume[-1] != 0 else 0

						day_range = (max(high) - min(low)) / (max(high) / 100)
						day_range = float('{:.1f}'.format(day_range))
						
						# ===== PIN DEFINITION =====
						if body_percent <= body_percent_filter and day_range / 3 >= total_range >= pin_range_filter:
							if high[-1] >= close[-1] >= (high[-1] - part) and \
								max(high[-2:-6:-1]) == max(high[-1:-25:-1]) and \
								low[-1] <= low[-2]:
								
								message_ss = f"{symbol} 48-range: {day_range}%. Pin: {total_range}% ({int(body_percent)}/100). Density: {int(density)}"
								
								bot1.send_message(662482931,
								                  f"🔴 #{symbol} 48-range: {day_range}%\n"
								                  f"🔴 pin: {total_range}% ({int(body_percent)}/100)\n"
								                  f"{volume_scheme} volume, b_{buy_volume_power}/{sell_volume_power}_s\n"
								                  f"{density_scheme} density: {int(density)}"
								                  )
								
								screenshoter_send(symbol, open, high, low, close, message_ss)
								print(message_ss)
							
							if low[-1] <= close[-1] <= (low[-1] + part) and \
								min(low[-2:-6:-1]) == min(low[-1:-25:-1]) and \
								high[-1] >= high[-2]:
								
								message_ss = f"{symbol} 48-range: {day_range}%. Pin: {total_range}% ({int(body_percent)}/100). Density: {int(density)}"
								
								bot1.send_message(662482931,
								                  f"🟢 #{symbol} 48-range: {day_range}%\n"
								                  f"🟢 pin: {total_range}% ({int(body_percent)}/100)\n"
								                  f"{volume_scheme} volume, b_{buy_volume_power}/{sell_volume_power}_s\n"
								                  f"{density_scheme} density: {int(density)}"
								                  )
								
								screenshoter_send(symbol, open, high, low, close, message_ss)
								print(message_ss)
					
if __name__ == '__main__':
	print("PARAMETERS:")
	request_limit_length = 48
	body_percent_filter = int(input("Body percent (def. 33): ") or 33)
	pin_close_part = int(input("Close at part (def. 3): ") or 3)
	pin_range_filter = float(input("Pin range (def. 0.1): ") or 0.1)
	gap_filter = 0.4
	tick_size_filter = 0.1
	density_filter = 20
	proc = int(input("Processes (def. 16): ") or 16)
	print("")
	
	bot1.send_message(662482931, f"STARTING WITH:\n\n"
			f"request_limit_length = {request_limit_length} candles, \n"
			f"body_percent_filter = {body_percent_filter}%, \n"
			f"pin_close_part = 1/{pin_close_part}, \n"
			f"total_range_filter = {pin_range_filter}%, \n"
			f"gap_filter = {gap_filter}%, \n"
            f"tick_size_filter = {tick_size_filter}%, \n"
            f"day_density_filter = {density_filter}, \n"
            f"proc = {proc} cores\n\n"
            f"💵💵💵💵💵")
	
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
		pairs = binance_pairs(chunks=proc, quote_assets=["USDT"], day_range_filter=pin_range_filter, day_density_filter=density_filter, tick_size_filter=tick_size_filter)
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs:")
		
		the_processes = []
		for proc_number in range(proc):
			process = Process(target=search, args=(pairs[proc_number], request_limit_length, gap_filter, density_filter, body_percent_filter, pin_range_filter, pin_close_part,))
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
