import requests


def ticksize_dictionary(ticksize_filter, price_filter):
	def bybit_tick_sizes():
		
		bybit_ticksize_url = "https://api.bybit.com/derivatives/v3/public/instruments-info"
		response = requests.get(bybit_ticksize_url)
		response_data = response.json()
		response_data = response_data.get("result").get("list")
		
		# Use a dictionary comprehension to create the bybit_tick_sizes dictionary
		bybit_tick_sizes = {
			s.get("symbol"): [
				float(s.get("priceFilter").get("tickSize")),
				s.get("lotSizeFilter").get("qtyStep")
				]
			for s in response_data
		}
		# print(bybit_tick_sizes)
		return bybit_tick_sizes # {"symbol": [tick_size, minQty]}
	
	def bybit_prices():
		
		bybit_ticker_url = "https://api.bybit.com/v5/market/tickers?category=linear"
		response = requests.get(bybit_ticker_url)
		response_data = response.json()
		response_data = response_data.get("result").get("list")
		
		# Use a dictionary comprehension to create the bybit_prices dictionary
		bybit_prices = {
			data.get("symbol"): [float(data.get("bid1Price")), float(data.get("ask1Price"))]
			for data in response_data
		}
		
		# print(bybit_prices)
		return bybit_prices
	
	
	def binance_tick_sizes():
		
		binance_ticksize_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
		response = requests.get(binance_ticksize_url)
		response_data = response.json()
		response_data = response_data.get("symbols")
		
		# Use a dictionary comprehension to create the binance_tick_sizes dictionary
		binance_tick_sizes = {
			s.get("symbol"): [
				float(s.get("filters")[0].get("tickSize")),
				(s.get("filters")[1]).get("minQty")
			]
			for s in response_data
		}
		# print(binance_tick_sizes)
		return binance_tick_sizes # {"symbol": [tick_size, minQty]}
	
	
	def binance_prices():
		
		binance_ticker_url = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
		response = requests.get(binance_ticker_url)
		response_data = response.json()
		
		# Use a dictionary comprehension to create the binance_prices dictionary
		binance_prices = {
			data["symbol"]: [float(data["bidPrice"]), float(data["askPrice"])]
			for data in response_data
		}
		# print(binance_prices)
		return binance_prices
	
	bybit_tick_sizes = bybit_tick_sizes()
	binance_tick_sizes = binance_tick_sizes()
	bybit_prices = bybit_prices()
	binance_prices = binance_prices()
	
	common_keys_in_ticksizes = set(bybit_tick_sizes.keys()) & set(binance_tick_sizes.keys())
	common_keys_in_prices = set(bybit_prices.keys()) & set(binance_prices.keys())
	
	max_tss = {key: max(bybit_tick_sizes[key][0], binance_tick_sizes[key][0]) for key in common_keys_in_ticksizes}
	max_pss = {key: max(max(bybit_prices[key]), max(binance_prices[key])) for key in common_keys_in_prices}
	
	result = {}
	
	for key, value in max_tss.items():
		if key in max_pss.keys():
			ts = max_tss[key] / (max_pss[key] / 100)
			ts = float('{:.3f}'.format(ts))
			
			if ts <= ticksize_filter and max_pss[key] <= price_filter:
				# result[key] = ts
				binance_qty_step = int(float(binance_tick_sizes[key][1])) \
					if int(float(binance_tick_sizes[key][1])) == float(binance_tick_sizes[key][1]) \
					else float(binance_tick_sizes[key][1])
				
				bybit_qty_step = int(float(bybit_tick_sizes[key][1])) \
					if int(float(bybit_tick_sizes[key][1])) == float(bybit_tick_sizes[key][1]) \
					else float(bybit_tick_sizes[key][1])
				
				result[key] = [binance_qty_step, bybit_qty_step]
				
	return result

for key, value in ticksize_dictionary(0.05, 100).items():
	print(f"{key}: Binace step {value[0]}, bybit step {value[1]}")