# import talipp.indicators.EMA
# import pandas as pd
# from requests import get

atr_length = 30


def levels_search(symbol, frame, cHigh, cLow, cClose, search_distance):
	
	# AVERAGE ATR

	atr = (sum(sum([cHigh[-1:-atr_length-1:-1] - cLow[-1:-atr_length-1:-1]])) / len(cClose[-1:-atr_length-1:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	if len(cClose) >= 901:
		highs = []
		lows = []
		for i in range(31, 900):
			
			if cHigh[-i] == max(cHigh[-1:-i-30:-1]) and abs(cHigh[-i] - cClose[-1]) / (cClose[-1] / 100) <= search_distance:
				for b in range(i+30, 900):
					if cHigh[-b] == max(cHigh[-1:-b-30:-1]) and cHigh[-b] == cHigh[-i]:
						highs.append(cHigh[-b])
						print(f"{symbol} ({frame}): point 1 {-i}, point 2 {-b}, {cHigh[-b]}")
						
			if cLow[-i] == min(cLow[-1:-i-30:-1]) and abs(cLow[-i] - cClose[-1]) / (cClose[-1] / 100) <= search_distance:
				for b in range(i+30, 900):
					if cLow[-b] == min(cLow[-1:-b-30:-1]) and cLow[-b] == cLow[-i]:
						lows.append(cLow[-b])
						print(f"{symbol} ({frame}): point 1 {-i}, point 2 {-b}, {cLow[-b]}")

		if len(lows) != 0:
			return [atr_per, lows[-1], abs(lows[-1] - cClose[-1]) / (cClose[-1] / 100)]
		if len(highs) != 0:
			return [atr_per, highs[-1], abs(highs[-1] - cClose[-1]) / (cClose[-1] / 100)]
		else:
			return [0, 0, 0]
	else:
		return [0, 0, 0]
	
# url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + 'TOMOUSDT' + '&interval=' + '5m' + '&limit=300'
# data1 = get(url_klines).json()
#
# d1 = pd.DataFrame(data1)
# d1.columns = [
# 'open_time',
# 'cOpen',
# 'cHigh',
# 'cLow',
# 'cClose',
# 'cVolume',
# 'close_time',
# 'qav',
# 'num_trades',
# 'taker_base_vol',
# 'taker_quote_vol',
# 'is_best_match'
# ]
# df1 = d1
#
# df1['cOpen'] = df1['cOpen'].astype(float)
# df1['cHigh'] = df1['cHigh'].astype(float)
# df1['cLow'] = df1['cLow'].astype(float)
# df1['cClose'] = df1['cClose'].astype(float)
#
# cOpen = df1['cOpen'].to_numpy()
# cHigh = df1['cHigh'].to_numpy()
# cLow = df1['cLow'].to_numpy()
# cClose = df1['cClose'].to_numpy()
#
# print(sonic_signal(cOpen, cHigh, cLow, cClose, 12, 3, 6))