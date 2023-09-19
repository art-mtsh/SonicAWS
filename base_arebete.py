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

price_filter = 4000
ticksize_filter = 0.02

atr_filter = 0.0
atr_length = 30

divergence_filter = 0.2


def calculation(instr, atr_filter, ticksize_filter):
	for frame in range(0, 1):
		for symbol in instr:
			# --- BINANCE DATA ---
			binance_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + binance_frame[frame] + '&limit=365'
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
			
			# binOpen = binance_df['binOpen'].to_numpy()
			binHigh = binance_df['binHigh'].to_numpy()
			binLow = binance_df['binLow'].to_numpy()
			binClose = binance_df['binClose'].to_numpy()
			
			atr = (sum(sum([binHigh[-1:-atr_length - 1:-1] - binLow[-1:-atr_length - 1:-1]])) / len(binClose[-1:-atr_length - 1:-1]))
			atr_per_binance = atr / (binClose[-1] / 100)
			atr_per_binance = float('{:.2f}'.format(atr_per_binance))
		
			# --- BYBIT DATA ---
			bybit_klines = f'https://api.bybit.com/v5/market/kline?category=inverse&symbol={symbol}&interval={bybit_frame[frame]}&limit=365'
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
				
				# ==== bybit ticksize ====
				all_ticks = list(bybOpen[-1:-1 - 300:-1]) + \
			            list(bybHigh[-1:-1 - 300:-1]) + \
			            list(bybLow[-1:-1 - 300:-1]) + \
			            list(bybClose[-1:-1 - 300:-1])
				all_ticks = sorted(all_ticks)
				
				diffs = 10
				
				for u in range(0, len(all_ticks) - 1):
					if 0 < all_ticks[-u] - all_ticks[-u - 1] < diffs:
						diffs = all_ticks[-u] - all_ticks[-u - 1]
				
				bybit_tick_size = float('{:.4f}'.format(diffs / (bybClose[-1] / 100)))
				# ==== bybit ticksize ====
				
				divers = []
				
				for l in range(2, 365, 60):
					distance = abs(binClose[-l] - bybClose[-l])
					distance_per = distance / (max([binClose[-l], bybClose[-l]]) / 100)
					distance_per = float('{:.2f}'.format(distance_per))
					divers.append(distance_per)
				
				historical_divergence = divers[0] - min(divers)
				
				clean_profit = historical_divergence - bybit_tick_size * 2 - 0.04 * 2 - 0.055 * 2
				clean_profit = float('{:.4f}'.format(clean_profit))
				
				if bybit_tick_size <= ticksize_filter and clean_profit >= divergence_filter:
					print(f'{symbol}:\nPotential profit: {clean_profit}%\nHistorical max diver: {historical_divergence}%\nCurrent: {divers[0]}, last min: {min(divers)}\nDivers: {divers}\n')
					bot3.send_message(662482931, f'{symbol}:\nPotential profit: {clean_profit}%\nHistorical max diver: {historical_divergence}%\nCurrent: {divers[0]}, last min: {min(divers)}\nDivers: {divers}\n')
				

def search_activale(price_filter, ticksize_filter, atr_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	threads = 8
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins: Price <= ${price_filter}, Tick <= {ticksize_filter}%, avg.ATR >= {atr_filter}%")

	the_processes = []
	
	for i in range(threads):
		process = Process(target=calculation, args=(instr[i], atr_filter, ticksize_filter))
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
		# last_minute_digit = int(now.strftime('%M')[-1])
		last_second_digit = int(now.strftime('%S'))
		if last_second_digit == 0:
			break
		time.sleep(0.1)
		# if last_hour_digit in list(range(8, 23)):


if __name__ == '__main__':
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
			atr_filter=atr_filter,
		)
		waiting()
