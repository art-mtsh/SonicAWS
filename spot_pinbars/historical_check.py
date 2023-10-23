import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
from module_get_pairs_binanceV3 import binance_pairs

ver = []

def search(
		filtered_symbols,
		frame,
		request_length,
		gap_filter,
		ticksize_filter,
		density_filter,
		donchian_length,
		extremum_window,
		room_filter,
		range_range_filter,
		min_pin_range_absolute,
		max_pin_range_mp,
		pin_part_filter,
		end_date
		):
	
	for data in filtered_symbols:
		
		symbol = data[0]
		tick_size = data[1]
		
		futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_length}&endTime={int(end_date)}'
		klines = requests.get(futures_klines)
		
		if klines.status_code == 200:
			response_length = len(klines.json()) if klines.json() != None else 0
			if response_length == request_length:
				binance_candle_data = klines.json()
				open = list(float(i[1]) for i in binance_candle_data)
				high = list(float(i[2]) for i in binance_candle_data)
				low = list(float(i[3]) for i in binance_candle_data)
				close = list(float(i[4]) for i in binance_candle_data)
			
				if len(open) == len(high) == len(low) == len(close) == request_length:
					
					for candle in range(request_length - donchian_length, donchian_length, -1):
						
						# ==== price gap ====
						max_gap = 0
						for i in range(candle, candle-donchian_length, -1):
							gap = abs(open[i] - close[i - 1])
							gap_p = 0
							if open[i] != 0: gap_p = gap / (open[i] / 100)
							if gap_p > max_gap: max_gap = gap_p
						max_gap = float('{:.2f}'.format(max_gap))
						
						# ==== binance ticksize ====
						bin_all_ticks = open + high + low + close
						bin_all_ticks = sorted(bin_all_ticks)
						bin_diffs = 10
						for u in range(1, len(bin_all_ticks) - 1):
							if 0 < bin_all_ticks[-u] - bin_all_ticks[-u - 1] < bin_diffs:
								bin_diffs = bin_all_ticks[-u] - bin_all_ticks[-u - 1]
						binance_tick_size = float('{:.4f}'.format(bin_diffs / (close[-candle] / 100)))
						
						density = (high[-candle] - low[-candle]) / bin_diffs

						# if symbol not in ver and candle == 100 and symbol == "LDOUSDT":
						# 	ver.append(symbol)
						# 	print(f"Verified {symbol}, index {-candle}, o {open[-candle]} h { high[-candle]} l {low[-candle]} c {close[-candle]}, gap {max_gap}, ticksize {binance_tick_size}, density: {density}")

						# ==== PIN SEARCH ====
						range_perc_range = (max(high[-candle: - donchian_length - candle: -1]) - min(low[-candle: - donchian_length - candle: -1])) / \
						                   (max(high[-candle: - donchian_length - candle: -1]) / 100) >= range_range_filter
						
						range_range = max(high[-candle: - donchian_length - candle: -1]) - min(low[-candle: - donchian_length - candle: -1])
						donchian_basis = (max(high[-candle: - donchian_length - candle: -1]) + min(low[-candle: - donchian_length - candle: -1])) / 2
						
						pin_perc_range_abs = (high[-candle] - low[-candle]) / (high[-candle] / 100) >= min_pin_range_absolute
						pin_perc_range_rel = range_range / max_pin_range_mp >= (high[-candle] - low[-candle])
						
						less_than_third = (high[-candle] - low[-candle]) <= \
						                  (max(high[-candle: - donchian_length - extremum_window - candle: -1]) -
						                   min(low[-candle: - donchian_length - extremum_window - candle: -1])) / 3
						
						bull_pin = min(close[-candle], open[-candle]) >= (high[-candle] - (high[-candle] - low[-candle]) / pin_part_filter)
						bear_pin = max(close[-candle], open[-candle]) <= (low[-candle] + (high[-candle] - low[-candle]) / pin_part_filter)
						
						bull_room = low[-candle] == min(low[-candle: -room_filter - candle: -1])
						bear_room = high[-candle] == max(high[-candle: -room_filter - candle: -1])
						
						highest_high_room = max(high[-candle: -extremum_window - candle: -1]) == \
						                    max(high[-candle: - donchian_length - extremum_window - candle: -1]) and \
						                    high[-candle] != max(high[-candle: -extremum_window - candle: -1]) and \
						                    low[-candle] != min(low[-candle: - donchian_length - extremum_window - candle: -1])
						
						lowest_low_room = min(low[-candle: -extremum_window - candle: -1]) == \
						                  min(low[-candle: - donchian_length - extremum_window - candle: -1]) and \
						                  low[-candle] != min(low[-candle: -extremum_window - candle: -1]) and \
						                  high[-candle] != max(high[-candle: - donchian_length - extremum_window - candle: -1])
						
						# ===== PIN DEFINITION =====
						if range_perc_range and \
							pin_perc_range_abs and \
							pin_perc_range_rel and \
							less_than_third and \
							max_gap <= gap_filter and \
							binance_tick_size <= ticksize_filter and \
							density >= density_filter:
							
								ed_timestamp = end_date / 1000
								ed_timestamp = datetime.fromtimestamp(ed_timestamp)
								enddate = ed_timestamp.strftime("%d.%m.%Y %H:%M:%S")
								
								if bull_pin and highest_high_room and bull_room and low[-candle] >= donchian_basis:
									
									if high[-candle] < high[-candle + 1]:
										stoploss = low[-candle]
										takeprofit = high[-candle] + (high[-candle] - low[-candle])
										
										# print("")
										# print(f"{symbol}, BULL TRADE on {-candle + 1} o {open[-candle]} h {high[-candle]} l {low[-candle]} c {close[-candle]}")
										
										for res in range(-candle + 1, 0):
											if low[res] < stoploss:
												print(f"{enddate}, "
												      f"{symbol}, "
												      f"{-candle}, "
												      f"BULL, "
												      f"-1, "
												      f"{high[-candle]}, "
												      f"{stoploss}, "
												      f"{takeprofit}, "
												      f"{int(density)}, "
												      f"{max(high[-candle: - donchian_length - candle: -1])}, "
												      f"{min(low[-candle: - donchian_length - candle: -1])}")
												break

											if high[res] >= takeprofit:
												print(f"{enddate}, "
												      f"{symbol}, "
												      f"{-candle}, "
												      f"BULL, "
												      f"1, "
												      f"{high[-candle]}, "
												      f"{stoploss}, "
												      f"{takeprofit}, "
												      f"{int(density)}, "
												      f"{max(high[-candle: - donchian_length - candle: -1])}, "
												      f"{min(low[-candle: - donchian_length - candle: -1])}")
												break
								
								if bear_pin and lowest_low_room and bear_room and high[-candle] <= donchian_basis:

									if low[-candle] > low[-candle + 1]:
										stoploss = high[-candle]
										takeprofit = low[-candle] - (high[-candle] - low[-candle])
										
										# print("")
										# print(f"{symbol}, BEAR TRADE on {-candle + 1} o {open[-candle]} h {high[-candle]} l {low[-candle]} c {close[-candle]}")
										
										for res in range(-candle + 1, 0):
											if high[res] > stoploss:
												print(f"{enddate}, "
												      f"{symbol}, "
												      f"{-candle}, "
												      f"BEAR, "
												      f"-1, "
												      f"{low[-candle]}, "
												      f"{stoploss}, "
												      f"{takeprofit}, "
												      f"{int(density)}, "
												      f"{max(high[-candle: - donchian_length - candle: -1])}, "
												      f"{min(low[-candle: - donchian_length - candle: -1])}")
												break

											if low[res] <= takeprofit:
												print(f"{enddate}, "
												      f"{symbol}, "
												      f"{-candle}, "
												      f"BEAR, "
												      f"1, "
												      f"{low[-candle]}, "
												      f"{stoploss}, "
												      f"{takeprofit}, "
												      f"{int(density)}, "
												      f"{max(high[-candle: - donchian_length - candle: -1])}, "
												      f"{min(low[-candle: - donchian_length - candle: -1])}")
												break
												
if __name__ == '__main__':
	
	proc = 16
	frame = "1h"
	gap_filter = 0.05
	tick_size_filter = 0.05
	density_filter = 20
	
	lengthdiver_filter = 48
	extremum_window_filter = 12
	room_filter = 12
	range_range_filter = 0.0
	min_pin_range_absolute = 0.8
	max_pin_range_mp = 5
	pin_part_filter = 2
	
	request_length = 24 + lengthdiver_filter * 2
	
	if True:
		
		time1 = time.perf_counter()
		pairs = binance_pairs(chunks=proc, quote_assets=["USDT"], day_range_filter=0, day_density_filter=0, tick_size_filter=100)
		print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
		print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs")
		print(f">>>")
		
		year = 2023
		
		for month in range(1, 10):
		
			for day in range(1, 31):
				
				if month == 2 and day > 27: continue
				
				the_processes = []
				
				for proc_number in range(proc):
					
					end_date_timestamp = datetime(year, month, day).timestamp()
					end_date = datetime.fromtimestamp(end_date_timestamp)
					hours_to_add = 3  # +++++++++++++++++++++++++
					minutes_to_add = 0  # +++++++++++++++++++++++
					time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
					new_date = end_date + time_to_add
					end_date = new_date.timestamp() * 1000
					
					process = Process(target=search, args=(
						pairs[proc_number],
						frame,
						request_length,
						gap_filter,
						tick_size_filter,
						density_filter,
						lengthdiver_filter,
						extremum_window_filter,
						room_filter,
						range_range_filter,
						min_pin_range_absolute,
						max_pin_range_mp,
						pin_part_filter,
						end_date,
					)
					                  )
					the_processes.append(process)
				
				for pro in the_processes:
					pro.start()
				
				for pro in the_processes:
					pro.join()
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"Finished search in {int(time3)} seconds")
		print("")
