import requests
import telebot

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def extremum(symbol, frame, request_limit_length):

	response = requests.get(f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}')
	
	if response.status_code == 200:
		
		response_length = len(response.json()) if response.json() != None else 0
		
		if response_length == request_limit_length:
			binance_candle_data = response.json()
			open = list(float(i[1]) for i in binance_candle_data)
			high = list(float(i[2]) for i in binance_candle_data)
			low = list(float(i[3]) for i in binance_candle_data)
			close = list(float(i[4]) for i in binance_candle_data)
			volume = list(float(i[5]) for i in binance_candle_data)
			trades = list(int(i[8]) for i in binance_candle_data)
			buy_volume = list(float(i[9]) for i in binance_candle_data)
			sell_volume = [volume[0] - buy_volume[0]]
			
			return [max(high), min(low), close[-1]]
		
		else:
			msg = f"Not enough data for {symbol} on 1m"
			bot1.send_message(662482931, msg)
			print(msg)
	
	
	elif response.status_code == 429:
		msg = f"{symbol} LIMITS REACHED !!!! 429 CODE !!!!"
		bot1.send_message(662482931, msg)
		bot1.send_message(662482931, msg)
		bot1.send_message(662482931, msg)
		print(msg)
	
	else:
		msg = f"Troubles with {symbol} data request on 1m, status code {response.status_code}"
		bot1.send_message(662482931, msg)
		print(msg)


def order_book(url):

	response = requests.get(url)
	
	if response.status_code == 200:

		response_data = response.json()
		
		bids = response_data.get('bids')
		asks = response_data.get('asks')
		close = float(asks[0][0])
		
		combined_list = bids + asks
		combined_list = list(combined_list)
		combined_list = [[float(item[0]), float(item[1])] for item in combined_list]
		combined_list = sorted(combined_list, key=lambda x: x[1])
		
		decimal_1 = len(str(combined_list[12][0]).split('.')[-1].rstrip('0'))
		decimal_2 = len(str(combined_list[34][0]).split('.')[-1].rstrip('0'))
		decimal_3 = len(str(combined_list[23][0]).split('.')[-1].rstrip('0'))
		max_decimal = max([decimal_1, decimal_2, decimal_3])

		return [close, combined_list, max_decimal]
	
	elif response.status_code == 429:
		bot1.send_message(662482931, "LIMITS REACHED !!!! 429 CODE !!!!")
		bot1.send_message(662482931, "LIMITS REACHED !!!! 429 CODE !!!!")
		bot1.send_message(662482931, "LIMITS REACHED !!!! 429 CODE !!!!")
		print(f"LIMITS REACHED !!!! 429 CODE !!!!")
	
	# else:
	# 	print(url)
	# 	print(response.status_code)

	
def three_distances(symbol, close, combined_list, max_avg_size, search_distance, size_filter):
	
	max_min = extremum(symbol, '1m', 30)
	max_of_range = max_min[0]
	min_of_range = max_min[1]
	
	price_1 = combined_list[-1][0]
	size_1 = combined_list[-1][1]
	size_1_dollars = (price_1 * size_1) / 1000
	distance_1 = abs(close - price_1) / (close / 100)
	distance_1 = float('{:.2f}'.format(distance_1))
	
	price_2 = combined_list[-2][0]
	size_2 = combined_list[-2][1]
	size_2_dollars = (price_2 * size_2) / 1000
	distance_2 = abs(close - price_2) / (close / 100)
	distance_2 = float('{:.2f}'.format(distance_2))
	
	price_3 = combined_list[-3][0]
	size_3 = combined_list[-3][1]
	size_3_dollars = (price_3 * size_3) / 1000
	distance_3 = abs(close - price_3) / (close / 100)
	distance_3 = float('{:.2f}'.format(distance_3))
	
	res = []
	
	if size_1 >= max_avg_size and size_1_dollars >= size_filter and distance_1 <= search_distance and max_of_range >= price_1 >= min_of_range:
		# and (price_1 >= max_of_range or min_of_range >= price_1):
		
		res.append([distance_1, price_1, size_1])
	
	if size_2 >= max_avg_size and size_2_dollars >= size_filter and distance_2 <= search_distance and max_of_range >= price_2 >= min_of_range:
		# and (price_2 >= max_of_range or min_of_range >= price_2):

		res.append([distance_2, price_2, size_2])
	
	if size_3 >= max_avg_size and size_3_dollars >= size_filter and distance_3 <= search_distance and max_of_range >= price_3 >= min_of_range:
		# and (price_3 >= max_of_range or min_of_range >= price_3):
		
		res.append([distance_3, price_3, size_3])
		
	return res
