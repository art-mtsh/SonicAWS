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
		s_queue
		):
	
	for data in filtered_symbols:
		symbol = data[0]
		tick_size = data[1]
		request_limit_length = 96
		
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
				
				# ==== GAP AND SELL VOLUME ====
				for curr_index in range(1, len(close)):
					gap = abs(open[curr_index] - close[curr_index - 1])
					gap_p = 0
					if open[curr_index] !=0: gap_p = gap / (open[curr_index] / 100)
					if gap_p > max_gap: max_gap = gap_p

					s_v = volume[curr_index] - buy_volume[curr_index]
					sell_volume.append(s_v)
					
				max_gap = float('{:.3f}'.format(max_gap))
				density = (max(high[-13: -1]) - min(low[-13: -1])) / tick_size
				
				# ==== CHECK DATA ====
				if open[-1] != 0 and high[-1] != 0 and \
					low[-1] != 0 and close[-1] != 0 and \
					max_gap <= gap_filter and \
					density >= density_filter and \
					len(high) == len(low) == request_limit_length:
					
					if len(volume) == request_limit_length and len(trades) == request_limit_length and sum(volume) != 0:
						
						trades_sum = sum(trades) / 1000000
						trades_sum = float('{:.2f}'.format(trades_sum))
						
						net_change = int((max(high) - min(low)) / (max(high) / 100))
						
						volume_change = int(sum(volume[48:request_limit_length]) / (sum(volume[0:48]) / 100))
						
						s_queue.put([symbol, trades_sum, net_change, volume_change])

def printer(s_queue):
	
	screener = []
	
	while not s_queue.empty():
		data = s_queue.get()
		screener.append(data)
		time.sleep(0.1)

	screener = sorted(screener, key=lambda x: (x[2]), reverse=True)
	trades_filter = 0
	
	message = ""
	
	for i in screener:
		if i[0] == "BTCUSDT":
			trades_filter += i[1] / 5
			message = f"{i[0]}, trades: {i[1]}M, 4H: {i[2]}%, v.change: +{i[3]}%\n"
			break
	
	
	for i in screener:
		if i[0] != "BTCUSDT" and i[1] >= trades_filter:
			message += f"\n{i[0]}, trades: {i[1]}M, 4H: {i[2]}%, v.change: +{i[3]}%"
			
	print(message)
	if message:
		bot1.send_message(662482931, message)

if __name__ == '__main__':
	
	proc = 15
	gap_filter = 0.1 # float(input("Max gap filter (def. 0.1%): ") or 0.1)
	density_filter = 20 # int(input("Density filter (def. 20): ") or 20)
	tick_size_filter = 0.05 # float(input("Ticksize filter (def. 0.05%): ") or 0.05)
	
	def waiting():
		
		while True:
			now = datetime.now()
			last_hour_digit = int(now.strftime('%H'))
			last_minute_digit = now.strftime('%M')
			last_second_digit = now.strftime('%S')
			time.sleep(0.1)
			
			# Перевірка в 04:30 , 09:00...
			if (int(last_minute_digit) + 1) % 30 == 0:
				if int(last_second_digit) == 20:
					break

	while True:
		
		manager = Manager()
		shared_queue = manager.Queue()
		
		frame = "5m"
		time1 = time.perf_counter()
		
		pairs = binance_pairs(
			chunks=proc,
			quote_assets=["USDT"],
			day_range_filter=1,
			day_density_filter=20,
			tick_size_filter=0.1
		)
		
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
		