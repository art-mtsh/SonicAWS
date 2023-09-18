import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime
from module_get_pairs import get_pairs

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

binance_frame = ['1m', '5m', '15m', '30m', '1h']
bybit_frame = ['1', '5', '15', '30', '60']
atr_length = 30
divergence = 0.2

def calculation(instr, atr_filter, for_signal, for_status):
	for frame in range(0, 5):
		for symbol in instr:
			# --- BINANCE DATA ---
			binance_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + binance_frame[frame] + '&limit=240'
			binance_data = get(binance_klines).json()
			binance_pd = pd.DataFrame(binance_data)
			binance_pd.columns = [
				'open_time',
				'binOpen',
				'binHigh',
				'binLow',
				'binClose',
				'binVolume',
				'binClose_time',
				'qav',
				'num_trades',
				'taker_base_vol',
				'taker_quote_vol',
				'is_best_match'
			]
			binance_df = binance_pd
			
			binance_df['binOpen'] = binance_df['binOpen'].astype(float)
			binance_df['binHigh'] = binance_df['binHigh'].astype(float)
			binance_df['binLow'] = binance_df['binLow'].astype(float)
			binance_df['binClose'] = binance_df['binClose'].astype(float)
			
			binOpen = binance_df['binOpen'].to_numpy()
			binHigh = binance_df['binHigh'].to_numpy()
			binLow = binance_df['binLow'].to_numpy()
			binClose = binance_df['binClose'].to_numpy()
			
			atr = (sum(sum([binHigh[-1:-atr_length - 1:-1] - binLow[-1:-atr_length - 1:-1]])) / len(binClose[-1:-atr_length - 1:-1]))
			atr_per_binance = atr / (binClose[-1] / 100)
			atr_per_binance = float('{:.2f}'.format(atr_per_binance))
		
			# --- BYBIT DATA ---
			bybit_klines = f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame[frame]}&limit=20'
			bybit_data = get(bybit_klines).json()
			bybit_pd = pd.DataFrame(bybit_data)
			if not bybit_pd.empty and atr_per_binance >= atr_filter:
				data_list = bybit_pd["result"]["list"]
				column_names = ["time_start", "bybOpen", "bybHigh", "bybLow", "bybClose", "volume", "some_column"]
				bybit_df = pd.DataFrame(data_list, columns=column_names)
				
				bybit_df['bybOpen'] = bybit_df['bybOpen'].astype(float)
				bybit_df['bybHigh'] = bybit_df['bybHigh'].astype(float)
				bybit_df['bybLow'] = bybit_df['bybLow'].astype(float)
				bybit_df['bybClose'] = bybit_df['bybClose'].astype(float)
				
				bybOpen = bybit_df['bybOpen'].to_numpy()[::-1]
				bybHigh = bybit_df['bybHigh'].to_numpy()[::-1]
				bybLow = bybit_df['bybLow'].to_numpy()[::-1]
				bybClose = bybit_df['bybClose'].to_numpy()[::-1]
			
				prev_binance_max = max(binHigh[-2:-12:-1])
				prev_bybit_max = max(bybHigh[-2:-12:-1])
				
				third_binance_max = max(binHigh[-5:-15:-1])
				third_bybit_max = max(bybHigh[-5:-15:-1])
				
				prev_binance_min = min(binLow[-2:-12:-1])
				prev_bybit_min = min(bybLow[-2:-12:-1])
				
				third_binance_min = min(binLow[-5:-15:-1])
				third_bybit_min = min(bybLow[-5:-15:-1])
				
				binance_overhigh = prev_binance_max == third_binance_max and binHigh[-1] >= prev_binance_max
				bybit_overhigh = prev_bybit_max == third_bybit_max and bybHigh[-1] >= prev_bybit_max
				
				binance_underlow = prev_binance_min == third_binance_min and binLow[-1] <= prev_binance_min
				bybit_underlow = prev_bybit_min == third_bybit_min and bybLow[-1] <= prev_bybit_min
				
				if (binance_overhigh and not bybit_overhigh):
					one = float("{:.2f}".format((binHigh[-1] - prev_binance_max) / (binClose[-1] / 100)))
					two = float("{:.2f}".format((bybHigh[-1] - prev_bybit_max) / (bybClose[-1] / 100)))
					if abs(one) >= divergence or abs(two) >= divergence:
						print(f'{symbol}({binance_frame[frame]}), sell:\nBinance overhigh {one}%({prev_binance_max}), bybit {two}%({prev_bybit_max})')
						bot3.send_message(662482931, f'{symbol}({binance_frame[frame]}), sell.\nBinance overhigh {one}%({prev_binance_max}), bybit {two}%({prev_bybit_max})')
					
				if (bybit_overhigh and not binance_overhigh):
					one = float("{:.2f}".format((binHigh[-1] - prev_binance_max) / (binClose[-1] / 100)))
					two = float("{:.2f}".format((bybHigh[-1] - prev_bybit_max) / (bybClose[-1] / 100)))
					if abs(one) >= divergence or abs(two) >= divergence:
						print(f'{symbol}({binance_frame[frame]}), sell:\nBinance {one}%({prev_binance_max}), bybit overhigh {two}%({prev_bybit_max})')
						bot3.send_message(662482931, f'{symbol}({binance_frame[frame]}), sell.\nBinance {one}%({prev_binance_max}), bybit overhigh {two}%({prev_bybit_max})')
					
				if (binance_underlow and not bybit_underlow):
					one = float("{:.2f}".format((binLow[-1] - prev_binance_min) / (binClose[-1] / 100)))
					two = float("{:.2f}".format((bybLow[-1] - prev_bybit_min) / (bybClose[-1] / 100)))
					if abs(one) >= divergence or abs(two) >= divergence:
						print(f'{symbol}({binance_frame[frame]}), buy:\nBinance underlow {one}%({prev_binance_min}), bybit {two}%({prev_bybit_min})')
						bot3.send_message(662482931, f'{symbol}({binance_frame[frame]}), buy.\nBinance underlow {one}%({prev_binance_min}), bybit {two}%({prev_bybit_min})')
					
				if (bybit_underlow and not binance_underlow):
					one = float("{:.2f}".format((binLow[-1] - prev_binance_min) / (binClose[-1] / 100)))
					two = float("{:.2f}".format((bybLow[-1] - prev_bybit_min) / (bybClose[-1] / 100)))
					if abs(one) >= divergence or abs(two) >= divergence:
						print(f'{symbol}({binance_frame[frame]}), buy:\nBinance {one}%({prev_binance_min}), bybit underlow {two}%({prev_bybit_min})')
						bot3.send_message(662482931, f'{symbol}({binance_frame[frame]}), buy.\nBinance {one}%({prev_binance_min}), bybit underlow {two}%({prev_bybit_min})')

def search_activale(price_filter, ticksize_filter, atr_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	threads = 8
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins: Price <= ${price_filter}, Tick <= {ticksize_filter}%, avg.ATR >= {atr_filter}%")
	
	for_signal = Queue()
	for_status = Queue()
	the_processes = []
	
	for i in range(threads):
		process = Process(target=calculation, args=(instr[i], atr_filter, for_signal, for_status,))
		the_processes.append(process)
	
	for pro in the_processes:
		pro.start()
	
	for pro in the_processes:
		pro.join()
	#
	# # Collect results
	# to_signal = []
	# to_status = []
	#
	# while not for_signal.empty():
	# 	to_signal.append(for_signal.get())
	#
	# while not for_status.empty():
	# 	to_status.append(for_status.get())
	#
	# # Format results as a single message
	# signal_message = "\n".join(to_signal)
	# status_message = "\n".join(to_status)
	
	time2 = time.perf_counter()
	time3 = time2 - time1
	
	# if len(signal_message) != 0:
	# 	print(f'For signal:\n{signal_message}')
	# 	bot3.send_message(662482931, f'️{total_count}c({timeinterval}): <${price_filter}, <{ticksize_filter}%, >{atr_filter}%, >{cloud_filter}cds\n'
	# 							f'\n'
	# 							f'{signal_message}\n'
	# 							f'\n'
	# 							f'🍌 {int(time3)} seconds 🍌', timeout=30)
	
	# if len(status_message) != 0:
	# 	print(f'For status:\n{status_message}')
	# 	bot1.send_message(662482931, f'{status_message}\n', timeout=30)
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


def waiting():
	while True:
		now = datetime.datetime.now()
		last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M')[-1])
		last_second_digit = int(now.strftime('%S'))
		time.sleep(30)
		# if last_hour_digit in list(range(8, 23)):
		break


if __name__ == '__main__':
	
	price_filter = 4000
	ticksize_filter = 0.02
	atr_filter = 0.3
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
			atr_filter=atr_filter,
		)
		waiting()

