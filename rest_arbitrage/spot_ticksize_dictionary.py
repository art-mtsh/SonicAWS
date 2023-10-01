import requests


def ticksize_dictionary(ticksize_filter, price_filter):
	def bybit_tick_sizes():
		
		bybit_ticksize_url = "https://api.bybit.com/spot/v3/public/symbols"
		response = requests.get(bybit_ticksize_url)
		response_data = response.json()
		response_data = response_data.get("result").get("list")
		
		# Use a dictionary comprehension to create the bybit_tick_sizes dictionary
		bybit_tick_sizes = {
			s.get("name"): [
				float(s.get("minTradeQty")),
				s.get("minPricePrecision")
				]
			for s in response_data
		}
		return bybit_tick_sizes
	
	def bybit_prices():
		
		bybit_ticker_url = "https://api.bybit.com/spot/v3/public/quote/ticker/24hr"
		response = requests.get(bybit_ticker_url)
		response_data = response.json()
		response_data = response_data.get("result").get("list")
		
		# Use a dictionary comprehension to create the bybit_prices dictionary
		bybit_prices = {
			data.get("s"): [float(data.get("bp")), float(data.get("ap"))]
			for data in response_data
		}

		return bybit_prices
	
	def binance_tick_sizes():
		
		binance_ticksize_url = "https://api.binance.com/api/v3/exchangeInfo"
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

		return binance_tick_sizes
	
	def binance_prices():
		
		binance_ticker_url = "https://api.binance.com/api/v3/ticker/bookTicker"
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
			
			binance_qty_step = int(float(binance_tick_sizes[key][1])) \
				if int(float(binance_tick_sizes[key][1])) == float(binance_tick_sizes[key][1]) \
				else float(binance_tick_sizes[key][1])
			
			bybit_qty_step = int(float(bybit_tick_sizes[key][1])) \
				if int(float(bybit_tick_sizes[key][1])) == float(bybit_tick_sizes[key][1]) \
				else float(bybit_tick_sizes[key][1])
			
			if ts <= ticksize_filter and max_pss[key] < price_filter:
			
				result[key] = [binance_qty_step, bybit_qty_step]
				
	return result

res = ticksize_dictionary(0.2, 1000)
for key, value in res.items():
	print(f"{key}: Binance step {value[0]}, bybit step {value[1]}")

print("")
print(len(res))
