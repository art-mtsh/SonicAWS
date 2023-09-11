import pandas as pd
from requests import get
from multiprocessing import Process, Manager
import time
import datetime
from module_get_pairs import get_pairs
from module_pinbar import pinbar_analysis
# from module_insidebar import ib_analysis

timeinterval = '15m'


def calculation(instr, year, month, day, pin_result_list, pin_fee_list, ib_result_list, ib_fee_list):
	
	for symbol in instr:
		
		values_to_get = 995
		
		end_time = datetime.datetime(year=year, month=month, day=day, hour=0, minute=0, second=0)
		end_time_ms = int(end_time.timestamp()) * 1000
		start_time_ms = end_time_ms - (values_to_get * 60 * 60 * 1000)
		
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
				
				pin_results_calc = []
				pin_fee_calc = []
				pin_start_point = 672 # For H1 - 745
				

				while pin_start_point > 24:
					for g in range(pin_start_point, 23, -1):
						sum_of_pin = pinbar_analysis(symbol=symbol,        # symbol
						                             bar_index=g,          # current bar coordinate
						                             # ======= GENERAL PARAMETERS =======
						                             ts_filter=0.02,       # tick size filter
						                             atr_filter=0.00,      # ATR filter
						                             avg_brr_filter=0,     # Body/Range ratio filter
						                             # ========= PIN PARAMETERS =========
						                             room_filter=1,        # Room to the left
						                             volume_room_filter=1, # Bigges volume for last ...
						                             pin_minrange=0.00,    # Pin minimum % range
						                             pin_maxrange=10.0,    # Pin minimum % range
						                             # ======== ORDER PARAMETERS ========
						                             revert=False,         # REVERT entries ?
						                             risk=30,              # Risk per trade
						                             rr_ratio=1,           # Risk/Reward ratio
						                             show_trades=True,     # Show trade?
						                             # ============== DATA ==============
						                             cOpen=cOpen,
						                             cHigh=cHigh,
						                             cLow=cLow,
						                             cClose=cClose,
						                             cVolume=cVolume,
						                             cTime=cTime)
						if sum_of_pin[1] != 0:
							pin_results_calc.append(int(sum_of_pin[1]))
							pin_fee_calc.append(int(sum_of_pin[2]))
							pin_start_point = sum_of_pin[0]
							break
						else:
							pin_start_point = g
				
				if len(pin_results_calc) != 0:
					
					for result in pin_results_calc:
						pin_result_list.append(int(result))
						
					for fee in pin_fee_calc:
						pin_fee_list.append(int(fee))
				else:
					pass

				# ib_results_calc = []
				# ib_fee_calc = []
				# ib_start_point = 745
				#
				# while ib_start_point > 24:
				# 	for g in range(ib_start_point, 23, -1):
				# 		sum_of_ib = ib_analysis(symbol=symbol,         # symbol
				# 		                             bar_index=g,       # current bar coordinate
				# 		                             ts_filter=0.02,    # tick size filter
				# 		                             atr_filter=0.2,    # ATR filter
				# 		                             avg_brr_filter=1,  # Body/Range ratio filter
				# 		                             revert=True,      # REVERT entries ?
				# 		                             risk=30,           # Risk per trade
				# 		                             rr_ratio=2,        # Risk/Reward ratio
				# 		                             show_trades=False, # Show trade?
				# 		                             cOpen=cOpen,
				# 		                             cHigh=cHigh,
				# 		                             cLow=cLow,
				# 		                             cClose=cClose,
				# 		                             cTime=cTime)
				#
				# 		if sum_of_ib[1] != 0:
				# 			ib_results_calc.append(int(sum_of_ib[1]))
				# 			ib_fee_calc.append(int(sum_of_ib[2]))
				# 			ib_start_point = sum_of_ib[0]
				# 			break
				# 		else:
				# 			ib_start_point = g
				#
				# if len(ib_results_calc) != 0:
				# 	for result in ib_results_calc:
				# 		ib_result_list.append(int(result))
				# 	for fee in ib_fee_calc:
				# 		ib_fee_list.append(int(fee))
				# else:
				# 	pass

			else:
				# print(f"{symbol} not enough DATA")
				continue
		else:
			# print(f"{symbol} no DATA")
			continue
				
			
				
def search_activale():
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	instr = get_pairs(price_filter=3000, ticksize_filter=100, num_chunks=16)
	total_count = sum(len(sublist) for sublist in instr)
	
	print(f"{total_count} coins. Timeframe: {timeinterval}")
	print("")
	
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
		[2023, 9, 7],
		[2023, 8, 28],
		[2023, 8, 21],
		[2023, 8, 14],
		[2023, 8, 7],
		[2023, 7, 28],
		[2023, 7, 21],
		[2023, 7, 14],
		[2023, 7, 7],
		[2023, 6, 28],
		[2023, 6, 21],
		[2023, 6, 14],
		[2023, 6, 7]
	]
	
	for date in dates_m15:
		
		time5 = time.perf_counter()
		
		the_processes = []
		
		pin_result_list = Manager().list()
		pin_fee_list = Manager().list()
		ib_result_list = Manager().list()
		ib_fee_list = Manager().list()
		
		for i in range(16):
			
			process = Process(target=calculation, args=(instr[i], date[0], date[1], date[2], pin_result_list, pin_fee_list, ib_result_list, ib_fee_list,))
			the_processes.append(process)
		
		for pro in the_processes:
			pro.start()
		
		for pro in the_processes:
			pro.join()
		
		for pro in the_processes:
			pro.close()
			
		# print(pin_result_list)
		# print(ib_result_list)
		# print("Processes are done")
		
		# ==== PINs RESULT ====
		pin_wintrades = 0

		if len(pin_result_list) != 0:

			for trades in pin_result_list:
				if trades > 0:
					pin_wintrades += 1

			pin_winrate = pin_wintrades / len(pin_result_list) * 100

		else:
			pin_winrate = 0

		pin_rough_pnl = sum(pin_result_list) + sum(pin_fee_list)
		pin_reverted_pnl = -pin_rough_pnl - sum(pin_fee_list) - abs(pin_rough_pnl)*0.035

		if sum(pin_result_list) != 0:
			print(f"{date[2] - 7}-{date[2]} week PIN TOTAL: {len(pin_result_list)} trades, winrate {int(pin_winrate)}%, PNL: {int(sum(pin_result_list))}$/{int(pin_reverted_pnl)}$ ({sum(pin_fee_list)}$ fee). Average PNL: {float('{:.5f}'.format(int(sum(pin_result_list)) / len(pin_result_list)))}")
		else:
			print(f"{date[2] - 7}-{date[2]} week has no PIN entries")

		# ==== IBs RESULT ====
		# ib_wintrades = 0
		#
		# if len(ib_result_list) != 0:
		#
		# 	for trades in ib_result_list:
		# 		if trades > 0:
		# 			ib_wintrades += 1
		#
		# 	ib_winrate = ib_wintrades / len(ib_result_list) * 100
		#
		# else:
		# 	ib_winrate = 0
		#
		# if sum(ib_result_list) != 0:
		# 	print(f"{date[1]} month IB TOTAL: {len(ib_result_list)} trades, winrate {int(ib_winrate)}%, with result of {int(sum(ib_result_list))}$ ({sum(ib_fee_list)}$ fee). Average PNL: {int(sum(ib_result_list)) / len(ib_result_list)}")
		# else:
		# 	print(f"{date[1]} month has no IB entries")

		# ====================
		
		time6 = time.perf_counter()
		time7 = time6 - time5
		
		# print(f"Month result: {sum(pin_result_list) + sum(ib_result_list)}$")
		print(f"Period cycle done in {int(time7)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")
		print("")
		
	time2 = time.perf_counter()
	time3 = time2 - time1
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == '__main__':
	search_activale()
	
