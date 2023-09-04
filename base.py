import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime
from module_sonic import sonic_signal
from module_get_pairs import get_pairs

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

timeinterval = '5m'


def calculation(instr, atr_filter, cloud_filter, first_point, second_point, for_signal, for_status):
	for symbol in instr:
		# try:
		# --- DATA ---
		url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + timeinterval + '&limit=990'
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
		
		sonic = sonic_signal(cOpen=cOpen, cHigh=cHigh, cLow=cLow, cClose=cClose, cloud_filter=cloud_filter, first_point=first_point, second_point=second_point)
		
		if sonic[1] >= atr_filter:  # and avgvolume_60 >= volume_filter
			if 'Sleep' not in sonic[0] and '🟢' not in sonic[0] and '🔴' not in sonic[0]:
				for_status.put(f'{sonic[0]} {symbol.removesuffix("USDT")}, ATR: {sonic[1]}%, {sonic[2]}')
			
			elif '🟢' in sonic[0] or '🔴' in sonic[0]:
				for_signal.put(f'{sonic[0]} {symbol.removesuffix("USDT")}, ATR: {sonic[1]}%, {sonic[2]}')
		
		# except telebot.apihelper.ApiTelegramException as ex:
		# 	print(f'Telegram error for {symbol}: {ex}')
		# 	bot2.send_message(662482931, f'Telegram error for {symbol}: {ex}')
		#
		# except Exception as exy:
		# 	print(f'Error main module for {symbol}: {exy}')
		# 	bot2.send_message(662482931, f'Error main module for {symbol}: {exy}')


def search_activale(price_filter, ticksize_filter, atr_filter, cloud_filter, first_point, second_point):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=8)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins {timeinterval}: Price <= ${price_filter}, Tick <= {ticksize_filter}%, avg.ATR >= {atr_filter}%, Cloud >= {cloud_filter} candles")
	
	for_signal = Queue()
	for_status = Queue()
	the_processes = []
	
	for i in range(8):
		process = Process(target=calculation, args=(instr[i], atr_filter, cloud_filter, first_point, second_point, for_signal, for_status,))
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
		# to_signal.append('\n')
	
	while not for_status.empty():
		to_status.append(for_status.get())
		# to_status.append('\n')
	
	# Format results as a single message
	signal_message = "\n".join(to_signal)
	status_message = "\n".join(to_status)
	
	time2 = time.perf_counter()
	time3 = time2 - time1
	
	if len(signal_message) != 0:
		print(f'For signal:\n{signal_message}')
		bot3.send_message(662482931, f'️{total_count}c({timeinterval}): <${price_filter}, <{ticksize_filter}%, >{atr_filter}%, >{cloud_filter}cds\n'
								f'\n'
								f'{signal_message}\n'
								f'\n'
								f'🍌 {int(time3)} seconds 🍌')
	
	if len(status_message) != 0:
		print(f'For status:\n{status_message}')
		bot1.send_message(662482931, f'️{total_count}c({timeinterval}): <${price_filter}, <{ticksize_filter}%, >{atr_filter}%, >{cloud_filter}cds\n'
								f'\n'
								f'{status_message}\n'
								f'\n'
								f'🍌 {int(time3)} seconds 🍌')
	else:
		bot1.send_message(662482931, f'️😪')
	
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


def waiting():
	while True:
		now = datetime.datetime.now()
		last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M')[-1])
		last_second_digit = int(now.strftime('%S'))
		if last_hour_digit in list(range(8, 23)):
			if last_minute_digit == 4 or last_minute_digit == 9:
				if last_second_digit == 25:
					break
		time.sleep(0.1)


if __name__ == '__main__':
	
	price_filter = 3000  # int(input('Pice less than: '))
	ticksize_filter = 0.025  # float(input('Ticksize less than: '))
	volume_filter = 1  # int(input('Volume more than: '))
	atr_filter = 0.2  # float(input('ATR more than: '))
	cloud_filter = 60 # int(input('Cloud length: '))
	first_point = int(input('First point: '))
	second_point = int(input('Second point: '))
	
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
			atr_filter=atr_filter,
			cloud_filter=cloud_filter,
			first_point=first_point,
			second_point=second_point,
		)
		time.sleep(60)
		waiting()
