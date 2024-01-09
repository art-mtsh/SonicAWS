import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
from module_get_pairs_binanceV3 import binance_pairs

'''
Стратегія пробою перехаю.

Є лой (фрактал), є хай (друга точка), найбільший за останні 120 хвилин, і є третя точка - відкат.
Після визначення трьох точок (лой, перехай, відкат), виставляється бай на другій точці, стоп на третій і тейк 1 до 1 RR.

Тести без комісії показали, що в трендові дні це працює з WR~58%, в нетрендові дні (яких набагато більше, бо бувають цілі нетрендові ПЕРІОДИ) - WR~30%

Стратегія скоріше ескізна (чогось невистачає), аніж робоча.

'''


def search(
		filtered_symbols,
		frame,
		request_length,
		gap_filter,
		ticksize_filter,
		density_filter,
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

				ed_timestamp = end_date / 1000
				ed_timestamp = datetime.fromtimestamp(ed_timestamp)
				enddate = ed_timestamp.strftime("%d.%m.%Y %H:%M:%S")

				if len(open) == len(high) == len(low) == len(close) == request_length:

					dist_a = 3
					dist_b = 120
					dist_c = 3
					w = 3
					range_filter = 0.4

					request_length = request_length - 60

					# ================================= BUY TRADE =================================
					next_buy_index = 0

					for a in range(dist_b+2, request_length):

						if a < next_buy_index:
							continue
						else:
							if low[a] == min(low[a-dist_a: a+dist_a]):

								first_low = low[a]
								first_low_index = a

								for b in range(a+w, request_length):

									if high[b] == max(high[a-dist_b: b+dist_a]):

										second_high = high[b]
										second_high_index = b

										a_b_range = abs(high[b] - low[a])
										a_b_range_percent = abs(high[b] - low[a]) / (high[b] / 100)

										if a_b_range_percent >= range_filter:

											third_low = 100000
											third_low_index = 100000

											for c in range(b+w, request_length):

												if low[c] == min(low[b: c+dist_c]) and \
														low[a] == min(low[a-dist_a: c+dist_c]) and \
														high[b] == max(high[a-dist_a: c+dist_c]) and \
														low[c] >= high[b] - (a_b_range / 3) and \
														low[c] < third_low:

													third_low = low[c]
													third_low_index = c

											if third_low != 100000:

												for d in range(third_low_index, request_length):
													# print(f"{symbol} {d}")

													if high[d] >= high[second_high_index] and low[third_low_index] == min(low[second_high_index: d]):

														entry = high[second_high_index]
														stoploss = low[third_low_index]
														takeprofit = entry + abs(entry - stoploss)

														for e in range(d, request_length):

															if stoploss >= low[e]:
																# print(f"{enddate} {symbol}: "
																# 	  f"first_low: {first_low} - {first_low_index}, "
																# 	  f"second_high: {second_high} - {second_high_index}, "
																# 	  f"third_low: {third_low} - {third_low_index}")
																# print(f"--- Stopped (buy {symbol} {first_low_index} -> {e})")
																print(-1, end=", ")
																next_buy_index = e
																break

															elif high[e] >= takeprofit:
																# print(f"{enddate} {symbol}: "
																# 	  f"first_low: {first_low} - {first_low_index}, "
																# 	  f"second_high: {second_high} - {second_high_index}, "
																# 	  f"third_low: {third_low} - {third_low_index}")
																# print(f"--- Profit (buy {symbol} {first_low_index} -> {e})")
																print(1, end=", ")
																next_buy_index = e
																break

														break
												break
											break
										break
								# break

					# ================================= SELL TRADE ================================
					next_sell_index = 0

					for a in range(dist_b + 2, request_length):

						if a < next_sell_index:
							continue
						else:
							if high[a] == max(high[a-dist_a: a+dist_a]):

								first_high = high[a]
								first_high_index = a

								for b in range(a+w, request_length):

									if low[b] == min(low[a-dist_b: b+dist_a]):

										second_low = low[b]
										second_low_index = b

										a_b_range = abs(high[a] - low[b])
										a_b_range_percent = abs(high[a] - low[b]) / (high[a] / 100)

										if a_b_range_percent >= range_filter:

											third_high = 0
											third_high_index = 0

											for c in range(b+w, request_length):

												if high[c] == max(high[b: c+dist_c]) and \
													high[a] == max(high[a-dist_a: c+dist_c]) and \
													low[b] == min(low[a-dist_a: c+dist_c]) and \
													high[c] <= low[b] + (a_b_range / 3) and \
													high[c] > third_high:

													third_high = high[c]
													third_high_index = c

											if third_high != 0:

												for d in range(third_high_index, request_length):
													# print(f"{symbol} {d}")

													if low[d] <= low[second_low_index] and high[third_high_index] == max(high[second_low_index: d]):

														entry = low[second_low_index]
														stoploss = high[third_high_index]
														takeprofit = entry - abs(entry - stoploss)

														for e in range(d, request_length):

															if stoploss <= high[e]:
																# print(f"{enddate} {symbol}: "
																# 	  f"first_high: {first_high} - {first_high_index}, "
																# 	  f"second_low: {second_low} - {second_low_index}, "
																# 	  f"third_high: {third_high} - {third_high_index}")
																# print(f"--- Stopped (sell {symbol} {first_high_index} -> {e})")
																print(-1, end=", ")
																next_sell_index = e
																break

															elif low[e] <= takeprofit:
																# print(f"{enddate} {symbol}: "
																# 	f"first_high: {first_high} - {first_high_index}, "
																# 	f"second_low: {second_low} - {second_low_index}, "
																# 	f"third_high: {third_high} - {third_high_index}")
																# print(f"--- Profit (sell {symbol} {first_high_index} -> {e})")
																print(1, end=", ")
																next_sell_index = e
																break

														break
												break
											break
										break
								# break

		elif klines.status_code == 418 or klines.status_code == 429:
			print(f"ERROR. Returned code: {klines.status_code}")
			print(futures_klines)


if __name__ == '__main__':

	time1 = time.perf_counter()

	proc = 2
	frame = "1m"
	gap_filter = 0.05
	tick_size_filter = 0.05
	density_filter = 20
	request_length = 720

	time1 = time.perf_counter()
	pairs = binance_pairs(chunks=proc, quote_assets=["USDT"], day_range_filter=5, day_density_filter=100, tick_size_filter=0.03)
	print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
	print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs\n")

	year = 2023
	# month = 12
	# day = 27

	for month in range(9, 13):
		print(f'\nMonth {month}')
		for day in range(1, 31):

			for hour in [0, 12]:

				time1 = time.perf_counter()
				# print(f"Starting 2023, {month} month, {day} day. {hour} hour")
				# print(">>>")
				the_processes = []

				for proc_number in range(proc):

					end_date_timestamp = datetime(year, month, day).timestamp()
					end_date = datetime.fromtimestamp(end_date_timestamp)
					hours_to_add = hour  # +++++++++++++++++++++++++
					minutes_to_add = 0  # +++++++++++++++++++++++
					time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
					new_date = end_date + time_to_add
					end_date = new_date.timestamp() * 1000

					process = Process(target=search, args=(pairs[proc_number], frame, request_length, gap_filter, tick_size_filter, density_filter, end_date, ))
					the_processes.append(process)

				for pro in the_processes:
					pro.start()

				for pro in the_processes:
					pro.join()

				time2 = time.perf_counter()
				time3 = time2 - time1

				# print(f"<<<")
				# print(f"Finished search in {int(time3)} seconds")
				# print("")
