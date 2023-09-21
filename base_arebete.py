import pandas as pd
from requests import get
from multiprocessing import Process
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

price_filter = 100000
ticksize_filter = 0.05

divergence_filter = 0.31


def calculation(instr, ticksize_filter):
	for frame in range(0, 1):
		for symbol in instr:
			# --- BINANCE DATA ---
			binance_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + binance_frame[frame] + '&limit=200'
			binance_data = get(binance_klines).json()
			binance_pd = pd.DataFrame(binance_data)
			if not binance_pd.empty:
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
			
				# --- BYBIT DATA ---
				bybit_klines = f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame[frame]}&limit=200'
				bybit_data = get(bybit_klines).json()
				bybit_pd = pd.DataFrame(bybit_data)
				
				if not bybit_pd.empty:
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
					
					# ==== bybit ticksize ====
					all_ticks = list(bybOpen[-1:-1 - 195:-1]) + \
				            list(bybHigh[-1:-1 - 195:-1]) + \
				            list(bybLow[-1:-1 - 195:-1]) + \
				            list(bybClose[-1:-1 - 195:-1])
					all_ticks = sorted(all_ticks)
					
					diffs = 10
					
					for u in range(0, len(all_ticks) - 1):
						if 0 < all_ticks[-u] - all_ticks[-u - 1] < diffs:
							diffs = all_ticks[-u] - all_ticks[-u - 1]
					
					bybit_tick_size = float('{:.4f}'.format(diffs / (bybClose[-1] / 100)))
					
					current_clean = float('{:.2f}'.format(abs(binClose[-1] - bybClose[-1]) / (binClose[-1] / 100)))
		
					# if len(binClose) > 725 and len(bybClose) > 725:
					# 	divers = []
					# 	for l in range(1, 721):
					# 		distance_per = abs(binClose[-l] - bybClose[-l]) / (binClose[-l] / 100)
					# 		distance_per = float('{:.2f}'.format(distance_per))
					# 		divers.append(distance_per)
					#
					# 	if len(divers) > 1:
					# 		if max(divers) - min(divers) >= 0.30:
					# 			print(f"{symbol}, {divers}")
					# 		results = []
					# 		# for d in range(0, len(divers)-1):
					# 		# 	if abs(divers[d] - divers[d+1]) >= 0.4:
					# 		# 		results.append(abs(divers[d] - divers[d+1]))
					#
					# 		if len(results) != 0:
					# 			print(f"{symbol} : {int(sum(results))}")
					
					if len(binClose) > 195 and \
						len(bybClose) > 195 and \
						current_clean >= divergence_filter and \
						bybit_tick_size <= ticksize_filter:

						divers = []
						for l in range(1, 181):
							distance_per = abs(binClose[-l] - bybClose[-l]) / (binClose[-l] / 100)
							distance_per = float('{:.2f}'.format(distance_per))
							divers.append(distance_per)

						'''
						Розраховувати "чисту" дивергенцію в моменті (за мінусом комісій, тіксайзу і т.д.) - не має сенсу, бо
						нам важлива результуюча різниця між поточною дивергенцією (входу) і майбутньою дивергенцією (виходу)
						від ЯКОЇ ВЖЕ ми і будемо віднімати комісії і т.д.

						Різниця між дивергенцією входу і дивергенцією виходу має бути 0.11% + 0.08% = 0.19% - аби вийти в нуль.
						Усе, що далі - наш прибуток.
						'''
						if current_clean - min(divers) >= divergence_filter:
							current_price_diff = float('{:.4f}'.format(abs(binClose[-1]-bybClose[-1])))
							print(f"#{symbol}:\n"
							      f"Current divergence: {current_clean}% > {divergence_filter}\n"
							      f"{binClose[-1]} - {bybClose[-1]} = {current_price_diff}\n"
							      f"Divs ranges is: {min(divers)} --> {max(divers)}\n")
	
							bot3.send_message(662482931, f"#{symbol}:\n"
							      f"Current divergence: {current_clean}% > {divergence_filter}\n"
							      f"{binClose[-1]} - {bybClose[-1]} = {current_price_diff}\n"
							      f"Divs ranges is: {min(divers)} --> {max(divers)}\n")
					

def search_activale(price_filter, ticksize_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	threads = 8
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins: Price <= ${price_filter}, Tick <= {ticksize_filter}%")

	the_processes = []
	
	for i in range(threads):
		process = Process(target=calculation, args=(instr[i], ticksize_filter))
		the_processes.append(process)
	
	for pro in the_processes:
		pro.start()
	
	for pro in the_processes:
		pro.join()

	time2 = time.perf_counter()
	time3 = time2 - time1
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


def waiting():
	while True:
		now = datetime.datetime.now()
		# last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M'))
		last_second_digit = int(now.strftime('%S'))
		time.sleep(0.1)
		if last_second_digit == 0:
			break
		# if last_hour_digit in list(range(8, 23)):


if __name__ == '__main__':
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
		)
		waiting()
