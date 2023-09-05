import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime
from module_get_pairs import get_pairs
from module_pinbar import pinbar_analysis

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

timeinterval = '1h'


def calculation(instr, trades_count, trades_result,):
	
	# the_sum = 0
	
	for symbol in instr:

		# --- DATA ---
		url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + timeinterval + '&limit=995'
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
		
		if len(cClose) == 995:
			sum_of_all = pinbar_analysis(symbol, cOpen, cHigh, cLow, cClose)
			summ = sum(sum_of_all)
			summ = float('{:.2f}'.format(summ))
			
			if summ != 0:
				# print(f"{symbol}, {len(sum_of_all)} trades, with result of {summ}$")
				trades_count.put(len(sum_of_all))
				trades_result.put(sum(sum_of_all))
		
	# print(f'The sum is {the_sum}')
	
	
def search_activale(price_filter, ticksize_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=16)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins {timeinterval}: Price <= ${price_filter}, Tick <= {ticksize_filter}%")
	
	trades_count = Queue()
	trades_result = Queue()
	the_processes = []
	
	for i in range(16):
		process = Process(target=calculation, args=(instr[i], trades_count, trades_result,))
		the_processes.append(process)
	
	for pro in the_processes:
		pro.start()
	
	for pro in the_processes:
		pro.join()
	
	for pro in the_processes:
		pro.close()
		
	trades_count_list = []
	trades_result_list = []
	
	while not trades_count.empty():
		trades_count_list.append(trades_count.get())
	
	while not trades_result.empty():
		trades_result_list.append(trades_result.get())
	
	print("")
	print(f"TOTAL, {sum(trades_count_list)} trades, with result of {int(sum(trades_result_list))}$")
	print("")
	
	time2 = time.perf_counter()
	time3 = time2 - time1
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == '__main__':
	
	price_filter = 3000
	ticksize_filter = 0.05
	search_activale(price_filter=price_filter, ticksize_filter=ticksize_filter)
	