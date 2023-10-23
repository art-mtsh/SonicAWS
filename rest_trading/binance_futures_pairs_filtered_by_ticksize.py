from requests import get
from module_get_pairs_binance import binance_pairs
from datetime import datetime, timedelta


binance_ticksize_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
response = get(binance_ticksize_url)
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


binance_frame = '1m'

end_date_timestamp = datetime(2023, 9, 30).timestamp()
end_date = datetime.fromtimestamp(end_date_timestamp)
hours_to_add = 13  # +++++++++++++++++++++++++
minutes_to_add = 0  # +++++++++++++++++++++++++
time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
new_date = end_date + time_to_add
end_date = new_date.timestamp() * 1000

request_limit_length = 120

symbols = binance_pairs(1)
symbols = symbols[0]

ranges = {}

print(f"{len(symbols)} symbols")


for symbol in symbols:
	
	bin_timestamp = []
	bin_open = []
	bin_high = []
	bin_low = []
	bin_close = []
	
	binance_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}'
	# binance_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={binance_frame}&limit={request_length}'
	binance_klines = get(binance_klines)
	
	if binance_klines.status_code == 200:
		response_length = len(binance_klines.json()) if binance_klines.json() != None else 0
		if response_length == request_limit_length:
			binance_candle_data = binance_klines.json()
			bin_timestamp = list(float(i[0]) for i in binance_candle_data)
			bin_open = list(float(i[1]) for i in binance_candle_data)
			bin_high = list(float(i[2]) for i in binance_candle_data)
			bin_low = list(float(i[3]) for i in binance_candle_data)
			bin_close = list(float(i[4]) for i in binance_candle_data)
		
	if len(bin_timestamp) == request_limit_length:
		max_price = max(bin_high)
		min_price = min(bin_low)
		middle = (max_price + min_price) / 2
		
		range = max_price - min_price
		range_p = range / (middle / 100)
		
		if symbol in binance_tick_sizes.keys():
			
			tick_size = binance_tick_sizes.get(symbol)
			tick_size = tick_size[0]
			tick_size = tick_size / (bin_close[-1] / 100)
		
			if max_price == bin_high[-1] and tick_size <= 0.1 and range_p >= 1:
				# ranges.update({symbol: ["max", tick_size]})
				print(f"{symbol}: max, {tick_size}%")
				
			if min_price == bin_low[-1] and tick_size <= 0.1 and range_p >= 1:
				# ranges.update({symbol: ["min", tick_size]})
				print(f"{symbol}: min, {tick_size}%")
		
# sorted_ranges = dict(sorted(ranges.items(), key=lambda item: item[1]))


# for key, value in ranges.items():
# 	print(f"{key}: {value}%")