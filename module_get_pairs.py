import requests


def get_pairs(price_filter, ticksize_filter, num_chunks):
	base_url = "https://fapi.binance.com/fapi/v1/"
	
	# Get list of perpetual futures trading pairs
	futures_pairs_response = requests.get(base_url + "exchangeInfo")
	futures_pairs_data = futures_pairs_response.json()
	
	perpetual_pairs = [
		pair_info["symbol"]
		for pair_info in futures_pairs_data["symbols"]
		if pair_info["contractType"] == "PERPETUAL"
	]
	
	# Get ticker prices for all pairs
	ticker_prices_response = requests.get(base_url + "ticker/price")
	ticker_prices_data = ticker_prices_response.json()
	ticker_prices_dict = {ticker_data["symbol"]: float(ticker_data["price"]) for ticker_data in ticker_prices_data}
	
	# Get symbol information for all pairs
	symbols_info_response = requests.get(base_url + "exchangeInfo")
	symbols_info_data = symbols_info_response.json()
	symbol_info_dict = {symbol_info["symbol"]: symbol_info for symbol_info in symbols_info_data["symbols"]}
	
	result_pairs = []
	
	for symbol in perpetual_pairs:
		symbol_info = symbol_info_dict.get(symbol)
		if not symbol_info:
			continue
		
		tick_size = None
		for f in symbol_info["filters"]:
			if f["filterType"] == "PRICE_FILTER":
				tick_size = float(f["tickSize"])
				break
		
		if tick_size is None:
			continue
		
		current_price = ticker_prices_dict.get(symbol, 0)
		
		# Calculate tick size in percent of current price
		if current_price != 0 and tick_size != 0:
			tick_size_percent = (tick_size / current_price) * 100
		else:
			tick_size_percent = 100
		
		if tick_size_percent <= ticksize_filter and current_price <= price_filter:
			result_pairs.append(symbol)
	
	avg_chunk_size = len(result_pairs) // num_chunks
	remainder = len(result_pairs) % num_chunks

	chunks = []
	i = 0
	for _ in range(num_chunks):
		chunk_size = avg_chunk_size + 1 if remainder > 0 else avg_chunk_size
		chunks.append(result_pairs[i:i + chunk_size])
		i += chunk_size
		remainder -= 1

	return chunks

# res = get_pairs(10000, 0.02, 1)
# print(res)
# for i in res:
# 	print(i)
#
# print(len(res))