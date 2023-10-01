from datetime import datetime, timedelta
import time
import requests
import telebot
from rest_arbitrage import keys

bot1 = telebot.TeleBot(keys.TELEGRAM_TOKEN)

def search():

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
	
	ticksize_dictionary = binance_tick_sizes()
	prices_dictionary = binance_prices()
	filtered_dictionary = []
	
	for s, vals in ticksize_dictionary.items():
		if s in prices_dictionary.keys():
			bid = prices_dictionary.get(s)[0]
			ask = prices_dictionary.get(s)[1]
			if bid != 0 and ask != 0:
				
				symbol = s
				tick_size = ticksize_dictionary.get(s)[0]
				minimum_size = ticksize_dictionary.get(s)[1]
		
				tick_size_percent = tick_size / (bid / 100) if bid != 0 else 100
				spread = abs(bid - ask)
				spread_percent = spread / (bid / 100) if bid != 0 else 100
				
				if bid >= 0.0001 and tick_size_percent <= 0.2:
					# print(f"{symbol}, tick: {tick_size_percent}%, spread: {spread_percent}%")
					filtered_dictionary.append(s)
	
	binance_frame = "15m"
	request_limit_length = 50
	
	# end_date_timestamp = datetime(2023, 9, 30).timestamp()
	# end_date = datetime.fromtimestamp(end_date_timestamp)
	# hours_to_add = 13  # +++++++++++++++++++++++++
	# minutes_to_add = 0  # +++++++++++++++++++++++++
	# time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
	# new_date = end_date + time_to_add
	# end_date = new_date.timestamp() * 1000
	
	
	for symbol in filtered_dictionary:
		timestamp = []
		open = []
		high = []
		low = []
		close = []
		volume = []
		cumulative_volume = []
		
		# binance_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_frame}&limit={request_limit_length}&endTime={int(end_date)}'
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
				
		cumulative_volume = [volume[0]]
		
		for i in range(1, len(close)):
			previous_value = cumulative_volume[-1]
			
			if close[i] > close[i-1]:
				cumulative_volume.append(previous_value + volume[i])
			elif close[i] == close[i-1]:
				cumulative_volume.append(previous_value)
			else:
				cumulative_volume.append(previous_value - volume[i])
				
		cum_min = min(cumulative_volume[-1:-49:-1])
		
		range_max = max(high[-1:-49:-1])
		range_min = min(low[-1:-49:-1])
		
		cumdelta_lowest = cumulative_volume[-1] == cum_min
		rising = range_max >= close[-1] >= (range_max - range_min) / 3
		range_min_max = (range_max - range_min) / (range_max / 100)
		
		
		if cumdelta_lowest and rising and 2 >= range_min_max >= 0.5:
			
			print(f"{symbol}, max {range_max}, low {low[-1]} min {range_min}, close {close[-1]}")
			bot1.send_message(662482931, f'️{symbol} divers...')

if __name__ == '__main__':
	
	while True:
		search()
		time.sleep(3600)