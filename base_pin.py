import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime
from module_get_pairs import get_pairs
from module_pinbar3 import pinbar_analysis

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

timeinterval = '1h'


def calculation(instr, year, month, trades_count, trades_result):
	
	for symbol in instr:
		
		values_to_get = 995
		
		# Set the desired end time (year, month, day, hour, minute, second)
		end_time = datetime.datetime(year=year, month=month, day=4, hour=0, minute=0, second=0)
		
		# Calculate the corresponding timestamp in milliseconds
		end_time_ms = int(end_time.timestamp()) * 1000
		
		# Calculate the start time (999 hours before the end_time)
		start_time_ms = end_time_ms - (values_to_get * 60 * 60 * 1000)
		
		# Create the URL with the specified timestamp range
		url_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeinterval}&startTime={start_time_ms}&endTime={end_time_ms}&limit={values_to_get}'
		
		data1 = get(url_klines).json()
		
		if len(data1) != 0:
			
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
			df1['close_time'] = pd.to_datetime(df1['close_time'], unit='ms')
			cTime = df1['close_time'].iloc
			
			cOpen = df1['cOpen'].to_numpy()
			cHigh = df1['cHigh'].to_numpy()
			cLow = df1['cLow'].to_numpy()
			cClose = df1['cClose'].to_numpy()
			
			ts_filter = 0.02
			atr_filter = 0.2
			
			avg_brr_filter = 20
			room_filter = 6
			revert = False
			
			risk = 20
			rr_ratio = 2
			show_trades = True
			
			results = []
			
			if len(cClose) == 995:
				start_point = 745
				
				while start_point != 24:
					for g in range(start_point, 23, -1):
						sum_of_all = pinbar_analysis(symbol, g, ts_filter, atr_filter, avg_brr_filter, room_filter, revert, risk, rr_ratio, show_trades, cOpen, cHigh, cLow, cClose, cTime)
						if sum_of_all[1] != 0:
							results.append(sum_of_all[1])
							start_point = sum_of_all[0]
							break
						else:
							start_point = g
							
			trades_result.put(sum(results))
			trades_count.put(len(results))

def search_activale(price_filter, ticksize_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=16)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins {timeinterval}: Price <= ${price_filter}, Tick <= {ticksize_filter}%")
	print("")
	
	dates = [
		[2023, 9],
		[2023, 8],
		[2023, 7],
		[2023, 6],
		[2023, 5],
		[2023, 4],
		[2023, 3],
		[2023, 2],
		[2023, 1],
		[2022, 12],
		[2022, 11],
		[2022, 10],
		[2022, 9],
		[2022, 8],
	]
	
	for date in dates:
		
		time5 = time.perf_counter()
		
		trades_count = Queue()
		trades_result = Queue()
		
		the_processes = []
		
		for i in range(1):
			process = Process(target=calculation, args=(instr[i], date[0], date[1], trades_count, trades_result, ))
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
		
		win_trades = 0
		
		for s in trades_count_list:
			if s > 0:
				win_trades += 1
		
		if sum(trades_count_list) != 0:
			print(f"{date[1]} month TOTAL: {len(trades_count_list)} trades, winrate {int(win_trades / (len(trades_count_list) / 100))}%, with result of {int(sum(trades_result_list))}$. Average PNL: {int(sum(trades_result_list)) / sum(trades_count_list)}")
		else:
			print(f"{date[1]} month has no entries")
		
		time6 = time.perf_counter()
		time7 = time6 - time5
		
		print(f"Month cycle done in {int(time7)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")
		print("")
		
	time2 = time.perf_counter()
	time3 = time2 - time1
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")

if __name__ == '__main__':
	
	price_filter = 3000
	ticksize_filter = 10.00
	search_activale(price_filter=price_filter, ticksize_filter=ticksize_filter)
