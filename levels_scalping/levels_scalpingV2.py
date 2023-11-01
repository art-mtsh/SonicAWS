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
		atr_per_filter,
		trades_k_filter,
		s_queue
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
				density = (max(high[-60: -1]) - min(low[-60: -1])) / tick_size
				
				# ==== AVERAGE ATR % ====
				avg_atr_per = [(high[-c] - low[-c]) / (close[-c] / 100) for c in range(60)]
				avg_atr_per = float('{:.2f}'.format(sum(avg_atr_per) / len(avg_atr_per)))
				
				# ==== VOLUME DYNAMIC ====
				volume_dynamic = None
				if len(volume) == request_limit_length:
					first_period_volume = sum(volume[-60:-1])
					second_period_volume = sum(volume[-120:-60])
					
					if first_period_volume > 0 and second_period_volume > 0:
						volume_dynamic = int(first_period_volume / (second_period_volume / 100))
					else:
						volume_dynamic = "n/a"
				
				# ==== THOUSANDS TRADES ====
				trades_k = int(sum(trades) / 1000)
				
				# ==== TICKSIZE % ====
				ts_percent = tick_size / (close[-1] / 100)
				ts_percent = float('{:.3f}'.format(ts_percent))
				
				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and \
					density >= density_filter and \
					avg_atr_per >= atr_per_filter and \
					trades_k >= trades_k_filter and \
					len(high) == len(low) == request_limit_length:
					
					print(f"{symbol}, gap {max_gap}%, dens {int(density)}, atr {avg_atr_per}%, tick {ts_percent}%, trades {int(sum(trades) / 1000)}K, vol {volume_dynamic}%")
					
					to_res = 100
					higher_high = ""
					
					to_sup = 100
					lower_low = ""
					
					for a in range(3, 120):
						if high[-a] == max(high[-1: -a - 4: -1]):
							
							for b in range(a + 4, 120):
								
								distance = abs(close[-1] - max(high[-a], high[-b])) / (max(high[-a], high[-b]) / 100)
								distance = float('{:.2f}'.format(distance))
								
								if high[-a] + high[-a] * 0.0002 >= high[-b] >= high[-a] - high[-a] * 0.0002 and \
									max(high[-a], high[-b]) == max(high[-1: -b - 2: -1]) and \
									distance <= 0.6 and distance < to_res:
									
									to_res = distance
									higher_high = (
										f"{symbol} resistance, \n"
										f"{max(high[-a], high[-b])} level, \n"
										f"{int(density)} x {ts_percent}%, \n"
										f"{avg_atr_per}% hour ATR, \n"
										f"{trades_k}K trades"
									)
					
					for a in range(3, 120):
						if low[-a] == min(low[-1: -a - 4: -1]):
							
							for b in range(a + 4, 120):
								
								distance = abs(close[-1] - min(low[-a], low[-b])) / (close[-1] / 100)
								distance = float('{:.2f}'.format(distance))
							
								if low[-a] + low[-a] * 0.0002 >= low[-b] >= low[-a] - low[-a] * 0.0002 and \
									min(low[-a], low[-b]) == min(low[-1: -b - 2: -1]) and \
									distance <= 0.6 and distance < to_sup:
									
									to_sup = distance
									lower_low = (
										f"{symbol} resistance, \n"
										f"{min(low[-a], low[-b])} level, \n"
										f"{int(density)} x {ts_percent}%, \n"
										f"{avg_atr_per}% hour ATR, \n"
										f"{trades_k}K trades"
									)

					if higher_high:
						s_queue.put(higher_high)
					
					if lower_low:
						s_queue.put(lower_low)


def printer(s_queue):
	
	message = ""
	
	while not s_queue.empty():
		data = s_queue.get()
		message += str(data) + "\n\n"
	
	if message:
		print("")
		print(message)
		# bot1.send_message(662482931, message)

if __name__ == '__main__':
	
	proc = 13
	gap_filter = 0.5 # float(input("Max gap filter (def. 0.2%): ") or 0.2)
	density_filter = 50 # int(input("Density filter (def. 30): ") or 30)
	tick_size_filter = 0.05 # float(input("Ticksize filter (def. 0.03%): ") or 0.03)
	atr_per_filter = 0.20 # float(input("ATR% filter (def. 0.3%): ") or 0.3)
	trades_k_filter = 100 # int(input("Trades filter (def. 100): ") or 100)
	
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
			time.sleep(0.1)
			
			# Перевірка в 04:15 , 09:30 , 14:45 ....
			if int(last_second_digit) == 0:
				break

	while True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		frame = "1m"
		time1 = time.perf_counter()
		
		pairs = binance_pairs(proc - 1, ["USDT"], 1, density_filter, tick_size_filter)
		
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
			                      atr_per_filter,
				                  trades_k_filter,
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
		