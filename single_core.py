import pandas as pd
from requests import get
import telebot
import time
import datetime
import requests
import talipp.indicators.EMA as ema

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

timeinterval = '5m'


def get_pairs(price_filter, ticksize_filter):
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
	
	return result_pairs


def search_activale(price_filter, ticksize_filter, volume_filter, atr_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	
	instr = get_pairs(price_filter, ticksize_filter)

	bot1.send_message(662482931, f'🔹 watchlist for {len(instr)} symbols ({timeinterval}) 🔹')
	bot1.send_message(662482931, f'🔹 price <= ${price_filter}, volume>=${volume_filter}.000/min 🔹')
	bot1.send_message(662482931, f'🔹 tick<={ticksize_filter}%, avg.ATR>={atr_filter}% 🔹')
	print(f"{len(instr)} symbols: Price <= ${price_filter}, Tick <= {ticksize_filter}%, Volume >= ${volume_filter}.000/min, avg.ATR >= {atr_filter}%")
	
	for symbol in instr:
		try:
			# --- DATA ---
			url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + timeinterval + '&limit=260'
			data1 = get(url_klines).json()
			
			d1 = pd.DataFrame(data1)
			d1.columns = [
				'open_time',
				'cOpen',
				'cHigh',
				'cLow',
				'cClose',
				'cVolume',
				'close_time',
				'qav',
				'num_trades',
				'taker_base_vol',
				'taker_quote_vol',
				'is_best_match'
			]
			df1 = d1
			df1['cOpen'] = df1['cOpen'].astype(float)
			df1['cHigh'] = df1['cHigh'].astype(float)
			df1['cLow'] = df1['cLow'].astype(float)
			df1['cClose'] = df1['cClose'].astype(float)
			df1['cVolume'] = df1['cVolume'].astype(float)
			
			cOpen = df1['cOpen'].to_numpy()
			cHigh = df1['cHigh'].to_numpy()
			cLow = df1['cLow'].to_numpy()
			cClose = df1['cClose'].to_numpy()
			cVolume = df1['cVolume'].to_numpy()
			
			avgvolume_60 = int(((sum(cVolume[-1:-61:-1]) / len(cVolume[-1:-61:-1])) * cClose[-1]) / 1000)
			atr_60m = (sum(sum([cHigh[-1:-61:-1] - cLow[-1:-61:-1]])) / len(cClose[-1:-61:-1]))
			atr_60per = atr_60m / (cClose[-1] / 100)
			atr_60per = float('{:.2f}'.format(atr_60per))
			
			sonic: str
			
			ema34_basis = ema(period=34, input_values=cClose)
			ema34_low = ema(period=34, input_values=cLow)
			ema34_high = ema(period=34, input_values=cHigh)
			ema89 = ema(period=89, input_values=cClose)
			ema233 = ema(period=233, input_values=cClose)
			
			rising_dragon = ema34_low[-1] > ema89[-1] > ema233[-1]
			falling_dragon = ema34_high[-1] < ema89[-1] < ema233[-1]
			
			dragon_distance_k: float
			if ema34_high[-1] != ema34_low[-1]:
				dragon_distance_k = abs(ema34_basis[-1] - ema89[-1]) / (ema34_high[-1] - ema34_low[-1])
			else:
				dragon_distance_k = 0
			
			cloud_above = 0
			cloud_below = 0
			
			for i in range(2, 12):
				if cLow[-i] < ema34_high[-i] or ema34_low[-i] < ema89[-i]:  # or ema89[-i] < ema233[-i]:
					cloud_above += 1
			
			for i in range(2, 12):
				if cHigh[-i] > ema34_low[-i] or ema34_high[-i] > ema89[-i]:  # or ema89[-i] > ema233[-1]:
					cloud_below += 1
			
			if dragon_distance_k > 1:
				if rising_dragon and cloud_above == 0:
					if ema34_high[-1] >= cLow[-1] >= ema89[-1]:
						sonic = 'Sonic RISE'
					sonic = 'Cloud above'
				elif falling_dragon and cloud_below == 0:
					if ema34_low[-1] <= cHigh[-1] <= ema89[-1]:
						sonic = 'Sonic FALL'
					sonic = 'Cloud below'
				else:
					sonic = 'Sleep'
			else:
				sonic = 'Sleep'
			
				
			if avgvolume_60 >= volume_filter and atr_60per >= atr_filter:
				if 'Cloud' in sonic:
					print(f"{symbol}. {sonic};")
					bot1.send_message(662482931, f'{symbol}. {sonic}! avg.ATR: {atr_60per}%')
				
				elif 'RISE' in sonic or 'FALL' in sonic:
					print(f"-------> {symbol}. {sonic};")
					bot3.send_message(662482931, f'{symbol}. {sonic}! avg.ATR: {atr_60per}%')
		
		except telebot.apihelper.ApiTelegramException as ex:
			print(f'Telegram error for {symbol}: {ex}')
			bot2.send_message(662482931, f'Telegram error for {symbol}: {ex}')
		
		except Exception as exy:
			print(f'Error main module for {symbol}: {exy}')
			bot2.send_message(662482931, f'Error main module for {symbol}: {exy}')

	bot1.send_message(662482931, f'|--------- thats all ---------|')
	time2 = time.perf_counter()
	time3 = time2 - time1
	print(f"Finished processes in {int(time3)} secs, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")


# PARAMETERS
price_filter = 10000
ticksize_filter = 0.02
volume_filter = 5
atr_filter = 0.25

def waiting():
	while True:
		now = datetime.datetime.now()
		last_minute_digit = int(now.strftime('%M')[-1])
		hours_now = int(now.strftime('%H'))
		if hours_now in list(range(9, 23)):
			if last_minute_digit == 3 or last_minute_digit == 8:
				break
		time.sleep(0.1)

if __name__ == '__main__':
	while True:
		search_activale(
			price_filter=price_filter,
			ticksize_filter=ticksize_filter,
			volume_filter=volume_filter,
			atr_filter=atr_filter
		)
		time.sleep(60)
		waiting()