import requests

def search():
	binance_ticker_url = "https://api.binance.com/api/v3/ticker/bookTicker"
	response = requests.get(binance_ticker_url)
	response_data = response.json()
	filtered_symbols = []
	for data in response_data:
		if float(data["bidPrice"]) >= price_filter and "RUB" not in data["symbol"]:
			filtered_symbols.append(data["symbol"])
	
	for symbol in filtered_symbols:
		binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}'
		binance_klines = requests.get(binance_klines)
		
		if binance_klines.status_code == 200:
			response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
			if response_length == request_limit_length:
				binance_candle_data = binance_klines.json()
				timestamp = list(float(i[0]) for i in binance_candle_data)
				open = list(float(i[1]) for i in binance_candle_data)
				high = list(float(i[2]) for i in binance_candle_data)
				low = list(float(i[3]) for i in binance_candle_data)
				close = list(float(i[4]) for i in binance_candle_data)
				volume = list(float(i[5]) for i in binance_candle_data)
				buy_volume = list(float(i[9]) for i in binance_candle_data)
		
				max_gap = 0
				cumulative_delta = {}
				new_delta = 0
		
				for i in range(1, len(close)):
					gap = abs(open[i] - close[i-1])
					if open[i] !=0: gap_p = gap / (open[i] / 100)
					if gap_p > max_gap: max_gap = gap_p
					
					b_vol = buy_volume[i]
					s_vol = volume[i] - buy_volume[i]
					new_delta += b_vol - s_vol
					cumulative_delta[i] = new_delta
				
				max_gap = float('{:.2f}'.format(max_gap))
				lowest_cd_index = min(cumulative_delta, key=cumulative_delta.get)
				lowest_low_index = lowest_cd_index
				
				for i in range(lowest_cd_index, len(low) - 1):
					if low[lowest_low_index] > low[i]:
						lowest_low_index = i
				
				dist_to_low = (low[-1] - low[lowest_low_index]) / (low[-1] / 100)
				dist_to_low = float('{:.2f}'.format(dist_to_low))
				
				if dist_to_low >= distance_to_low and \
					cumulative_delta.get(request_limit_length - 1) <= cumulative_delta.get(lowest_cd_index) and \
					max_gap <= gap_filter:
					print(f"=========================================>>>>> {symbol}: DIVERGENCE max gap: {max_gap}%")
					
				elif max_gap <= gap_filter:
					print(f"{symbol}, "
					      f"max gap: {max_gap}%, "
					      f"lowest low index: {lowest_low_index}, "
					      f"lowest cd index: {lowest_cd_index}")

if __name__ == '__main__':
	
	price_filter = 0.0001
	binance_frame = "5m"
	request_limit_length = 24
	distance_to_low = 0.1
	gap_filter = 0.5
	
	while True:
		binance_frame = str(input("Timeframe (1h, 30m, 15m, 5m, 1m): "))
		request_limit_length = int(input("Request length, bars: "))
		sleep_time = int(input("Sleep time, minutes: ")) * 60
		distance_to_low = float(input("Distance to low, %: "))
		
		time1 = time.perf_counter()
		
		pairs = binance_pairs(4)
		
		print(f"pairs: {sum(len(inner_list) for inner_list in pairs)}")
		
		t1 = threading.Thread(target=search(pairs[0], binance_frame, request_limit_length, distance_to_low))
		t2 = threading.Thread(target=search(pairs[1], binance_frame, request_limit_length, distance_to_low))
		t3 = threading.Thread(target=search(pairs[2], binance_frame, request_limit_length, distance_to_low))
		t4 = threading.Thread(target=search(pairs[3], binance_frame, request_limit_length, distance_to_low))
		
		t1.start()
		t2.start()
		t3.start()
		t4.start()
		
		t1.join()
		t2.join()
		t3.join()
		t4.join()
		
		time2 = time.perf_counter()
		time3 = time2 - time1
		
		print(f"finished processes in {int(time3)} seconds")
		print("")
		
		time.sleep(sleep_time)