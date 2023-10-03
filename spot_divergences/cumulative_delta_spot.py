import threading
import time
import requests
import telebot
from module_get_pairs_binance import binance_pairs

TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)

def search(filtered_dictionary):
	
	binance_frame = "1h"
	request_limit_length = 96
	
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
		buy_volume = []
		cumulative_delta = []

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
				buy_volume = list(float(i[9]) for i in binance_candle_data)

				
				cumulative_delta = {}
				new_delta = 0
				
				for i in range(1, len(volume)):
					b_vol = buy_volume[i]
					s_vol = volume[i] - buy_volume[i]
					new_delta += b_vol - s_vol
					cumulative_delta[i] = new_delta
			
				lowest_cd_index = min(cumulative_delta, key=cumulative_delta.get)
				lowest_low_index = lowest_cd_index
				
				for i in range(lowest_cd_index, len(low) - 1):
					if low[lowest_low_index] > low[i]:
						lowest_low_index = i
				
				if low[-1] > low[lowest_low_index] and cumulative_delta.get(95) <= cumulative_delta.get(lowest_cd_index):
					dist_to_low = (low[-1] - low[lowest_low_index]) / (low[-1] / 100)
					dist_to_low = '{:.2f}'.format(dist_to_low)
					print(f"{symbol}: {dist_to_low}%")
					bot1.send_message(662482931, f"{symbol}: {dist_to_low}%")

		else:
			print(f"Received status code: {binance_klines.status_code}")

if __name__ == '__main__':
	
	while True:
		time1 = time.perf_counter()
		
		pairs = binance_pairs(4)
		
		print(f"pairs: {sum(len(inner_list) for inner_list in pairs)}")
		
		t1 = threading.Thread(target=search(pairs[0]))
		t2 = threading.Thread(target=search(pairs[1]))
		t3 = threading.Thread(target=search(pairs[2]))
		t4 = threading.Thread(target=search(pairs[3]))
		
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
		
		print(f"Finished processes in {int(time3)} seconds")
		
		time.sleep(1800)