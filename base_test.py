import pandas as pd
from requests import get
from multiprocessing import Process, Manager
import time
import datetime
from module_get_pairs import get_pairs
from module_williams import w_analysis
# from module_insidebar import ib_analysis
from module_dctrade import dc_analysis

timeinterval = '1m'


def calculation(instr, year, month, day, hour, pin_result_list, pin_fee_list, dc_result_list, dc_fee_list):
	
	for symbol in instr:
		
		values_to_get = 995
		
		end_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=0, second=0)
		end_time_ms = int(end_time.timestamp()) * 1000
		start_time_ms = end_time_ms - (values_to_get * 60 * 1000)
		# print(start_time_ms.strftime("%Y-%m-%d %H:%M:%S"))
		# print(end_time.strftime("%Y-%m-%d %H:%M:%S"))
		
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
			df1['cVolume'] = df1['cVolume'].astype(float)
			df1['close_time'] = pd.to_datetime(df1['close_time'], unit='ms')
			cTime = df1['close_time'].iloc
			
			cOpen = df1['cOpen'].to_numpy()
			cHigh = df1['cHigh'].to_numpy()
			cLow = df1['cLow'].to_numpy()
			cClose = df1['cClose'].to_numpy()
			cVolume = df1['cVolume'].to_numpy()
			
			if len(cClose) == 995:
				
				# ===================== 4 ema + WILLIAMS(14) =====================

				# ===================== 2 DONCHIANS =====================

				dc_results_calc = []
				dc_fee_calc = []
				dc_start_point = 720  # For H1 - 745

				while dc_start_point > 1:
					for g in range(dc_start_point, 0, -1):
						sum_of_dc = dc_analysis(symbol=symbol,  # symbol
						                             bar_index=g,  # current bar coordinate
						                             # ======= GENERAL PARAMETERS =======
						                             ts_filter=0.02,  # tick size filter
						                             atr_filter=0.00,  # ATR filter
						                             avg_brr_filter=0,  # Body/Range ratio filter
						                             # ========= PIN PARAMETERS =========
						                             room_filter=1,  # Room to the left
						                             volume_room_filter=1,  # Bigges volume for last ...
						                             pin_minrange=0.00,  # Pin minimum % range
						                             pin_maxrange=10.0,  # Pin minimum % range
						                             # ======== ORDER PARAMETERS ========
						                             revert=False,  # REVERT entries ?
						                             risk=30,  # Risk per trade
						                             rr_ratio=1,  # Risk/Reward ratio
						                             show_trades=True,  # Show trade?
						                             # ============== DATA ==============
						                             cOpen=cOpen,
						                             cHigh=cHigh,
						                             cLow=cLow,
						                             cClose=cClose,
						                             cVolume=cVolume,
						                             cTime=cTime)
						if sum_of_dc[11] != 0:
							dc_results_calc.append(sum_of_dc)
							dc_start_point = sum_of_dc[-1] - 1
							break
						else:
							dc_start_point = g
				if len(dc_results_calc) != 0:
					# print(f"Found shit for {symbol}")
					for result in dc_results_calc:
						dc_result_list.append(result)
				else:
					# print(f"Nothing found for {symbol}")
					pass
			else:
				continue
		else:
			continue
			
				
def search_activale():
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	number_of_processes = 4
	instr = get_pairs(price_filter=3000, ticksize_filter=100, num_chunks=number_of_processes)
	# total_count = sum(len(sublist) for sublist in instr)
	#
	# print(f"{total_count} coins. Timeframe: {timeinterval}")
	# print("")
	
	general_total = 0
	
	dates_h1 = [
		[2023, 9, 8],
		[2023, 8, 8],
		[2023, 7, 8],
		[2023, 6, 8],
		[2023, 5, 8],
		[2023, 4, 8],
		[2023, 3, 8],
		[2023, 2, 8],
		[2023, 1, 8],
		[2022, 12, 8],
		[2022, 11, 8],
		[2022, 10, 8],
		[2022, 9, 8],
		[2022, 8, 8],
	]
	
	dates_m15 = [
		[2023, 10, 7],
		[2023, 9, 28],
		[2023, 9, 21],
		[2023, 9, 14],
		[2023, 9, 7],
		[2023, 8, 28],
		[2023, 8, 21],
		[2023, 8, 14],
		[2023, 8, 7],
		[2023, 7, 28],
		[2023, 7, 21],
		[2023, 7, 14],
		[2023, 7, 7]
	]
	
	year = 2023
	
	month = 9
	
	for day in range(13, 31):
		
		for day_part in range(9, 22, 12):
		
			time5 = time.perf_counter()
			
			the_processes = []
			
			pin_result_list = Manager().list()
			pin_fee_list = Manager().list()
			dc_result_list = Manager().list()
			dc_fee_list = Manager().list()
			
			for i in range(number_of_processes):
				
				process = Process(target=calculation, args=(instr[i], year, month, day, day_part, pin_result_list, pin_fee_list, dc_result_list, dc_fee_list,))
				the_processes.append(process)
			
			for pro in the_processes:
				pro.start()
			
			for pro in the_processes:
				pro.join()
			
			for pro in the_processes:
				pro.close()
			
			dc_sorted_result = sorted(dc_result_list, key=lambda x: x[1])
			
			dc_no_duplicate = []
			
			for non_unique in dc_sorted_result:
				if len(dc_no_duplicate) == 0:
					dc_no_duplicate.append(non_unique)
				else:
					if non_unique[1] != dc_no_duplicate[-1][1]:
						dc_no_duplicate.append(non_unique)
			
			unique_result = 0
			
			for unique in dc_no_duplicate:
				if -75 <= unique_result <= 200:
					unique_result += unique[11]
				else:
					break
			
			for day_result in dc_no_duplicate:
				print(f'{day_result[1].strftime("%Y-%m-%d")}, '
				      f'{day_result[1].strftime("%H:%M:%S")}, '
				      f'{day_result[2].strftime("%H:%M:%S")}, '
				      f'{day_result[3]}, '
				      f'{day_result[10]}, '
				      f'{day_result[11]}, '
				      f'{day_result[12]}, '
				      f'{day_result[13]}, '
				      f'{day_result[14]}, '
				      f'{day_result[15]}, '
				      f'{day_result[16]}')
			
			print(f"{year}-{month}-{day} (<{day_part}:00). Unique cumulative result: {int(unique_result)}$")
		
			general_total += float("{:.2f}".format(unique_result))
		
	time2 = time.perf_counter()
	time3 = time2 - time1
	print(f"Finished processes in {int(time3)} seconds with month result: {general_total}$, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == '__main__':
	search_activale()
	
