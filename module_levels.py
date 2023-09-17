# import talipp.indicators.EMA
# import pandas as pd
# from requests import get

atr_length = 60


def levels_search(cHigh, cLow, cClose):
	
	# AVERAGE ATR

	atr = (sum(sum([cHigh[-1:-atr_length-1:-1] - cLow[-1:-atr_length-1:-1]])) / len(cClose[-1:-atr_length-1:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	searh_distance = 0.5
	
	if len(cClose) >= 901:
		highs = []
		lows = []
		for i in range(61, 900):
			if cHigh[-i] == max(cHigh[-i+60:-i-61:-1]) and \
				cHigh[-i] >= cClose[-1] and \
				abs(cHigh[-i] - cClose[-1]) / (cClose[-1] / 100) <= searh_distance:
				clear_high = True
				for b in range(1, i):
					if cHigh[-b] > cHigh[-i]:
						clear_high = False
						break
				if clear_high:
					highs.append(cHigh[-i])
				
			if cLow[-i] == min(cLow[-i+60:-i-61:-1]) and \
				cLow[-i] <= cClose[-1] and \
				abs(cLow[-i] - cClose[-1]) / (cClose[-1] / 100) <= searh_distance:
				clear_low = True
				for b in range(1, i):
					if cLow[-b] < cLow[-i]:
						clear_low = False
						break
				if clear_low:
					lows.append(cLow[-i])

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