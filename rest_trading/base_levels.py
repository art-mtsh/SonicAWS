import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime
from module_levels import levels_search
from module_get_pairs import get_pairs

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)


def calculation(instr, atr_filter, search_distance, for_signal, for_status):
	for frame in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
		for symbol in instr:
			# --- DATA ---
			url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + frame + '&limit=999'
			data1 = get(url_klines).json()
			
			d1 = pd.DataFrame(data1)
			d1.columns = [
				'open_time',
				'cOpen',
				'cHigh',
				'cLow',
				'cClose',
				'cVolume',
				'close_time',
				'qav',
				'num_trades',
				'taker_base_vol',
				'taker_quote_vol',
				'is_best_match'
			]
			df1 = d1
			
			df1['cOpen'] = df1['cOpen'].astype(float)
			df1['cHigh'] = df1['cHigh'].astype(float)
			df1['cLow'] = df1['cLow'].astype(float)
			df1['cClose'] = df1['cClose'].astype(float)
			
			cOpen = df1['cOpen'].to_numpy()
			cHigh = df1['cHigh'].to_numpy()
			cLow = df1['cLow'].to_numpy()
			cClose = df1['cClose'].to_numpy()
			
			lev_s = levels_search(symbol=symbol, frame=frame, cHigh=cHigh, cLow=cLow, cClose=cClose, search_distance=search_distance)
			
			if lev_s[0] >= atr_filter and lev_s[1] != 0:
				for_status.put(f'{symbol}({frame}), atr: {lev_s[0]}%, {lev_s[1]} in {float("{:.1f}".format(lev_s[2]))}%')


def search_activale(price_filter, ticksize_filter, atr_filter, search_distance):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	threads = 16
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=threads)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins: Price <= ${price_filter}, Tick <= {ticksize_filter}%, avg.ATR >= {atr_filter}%")
	
	for_signal = Queue()
	for_status = Queue()
	the_processes = []
	
	for i in range(threads):
		process = Process(target=calculation, args=(instr[i], atr_filter, search_distance, for_signal, for_status,))
		the_processes.append(process)
	
	for pro in the_processes:
		pro.start()
	
	for pro in the_processes:
		pro.join()
	
	# Collect results
	to_signal = []
	to_status = []
	
	while not for_signal.empty():
		to_signal.append(for_signal.get())
	
	while not for_status.empty():
		to_status.append(for_status.get())
	
	# Format results as a single message
	signal_message = "\n".join(to_signal)
	status_message = "\n".join(to_status)
	
	time2 = time.perf_counter()
	time3 = time2 - time1
	
	# if len(signal_message) != 0:
	# 	print(f'For signal:\n{signal_message}')
	# 	bot1.send_message(662482931, f'️{total_count}c({timeinterval}): <${price_filter}, <{ticksize_filter}%, >{atr_filter}%, >{cloud_filter}cds\n'
	# 							f'\n'
	# 							f'{signal_message}\n'
	# 							f'\n'
	# 							f'🍌 {int(time3)} seconds 🍌', timeout=30)
	
	if len(status_message) != 0:
		print(f'For status:\n{status_message}')
		bot1.send_message(662482931, f'{status_message}\n', timeout=30)
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


def waiting():
	while True:
		now = datetime.datetime.now()
		last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M')[-1])
		last_second_digit = int(now.strftime('%S'))
		time.sleep(90)
		if last_hour_digit in list(range(8, 23)):
			break


if __name__ == '__main__':
	
	price_filter = 3000  # int(input('Pice less than: '))
	ticksize_filter = 0.03  # float(input('Ticksize less than: '))
	atr_filter = 0.2  # float(input('ATR more than: '))
	search_distance = float(input("Search distance: "))
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
			atr_filter=atr_filter,
			search_distance=search_distance
		)
		waiting()

