import talipp.indicators.EMA

indicator_length = 34

candle_part = 4
br_ratio_value = 10

range_percent_filter = 0.4
atr_min = 0.4
atr_max = 1.2

tp_multiplier = 2
risk = 15

show_trades = False

def pinbar_analysis(symbol, cOpen, cHigh, cLow, cClose):
	
	results = []

	for i in range(24, 745):
		
		# AVERAGE ATR
		atr = (sum(sum([cHigh[-i:-i-48:-1] - cLow[-i:-i-48:-1]])) / len(cClose[-i:-i-48:-1]))
		atr_per = atr / (cClose[-1] / 100)
		atr_per = float('{:.2f}'.format(atr_per))
		
		# EMA
		ema34 = talipp.indicators.EMA(period=34, input_values=cClose[-i:-len(cClose):-1])
		ema89 = talipp.indicators.EMA(period=89, input_values=cClose[-i:-len(cClose):-1])
		
		# DONCHIAN
		# d_min = min(cLow[-i:-indicator_length - i:-1])
		# d_max = max(cHigh[-i:-indicator_length - i:-1])
		# d_mid = (d_min + d_max) / 2
		
		# BODY/RANGE RATIO
		range_percent: float
		br_ratio: float
		
		if (cHigh[-i] - cLow[-i]) != 0:
			range_percent = (cHigh[-i] - cLow[-i]) / (cClose[-i] / 100)
			br_ratio = abs(cOpen[-i] - cClose[-i]) / ((cHigh[-i] - cLow[-i]) / 100)
		else:
			range_percent = 0
			br_ratio = 0
			
		# PIN DEFINITION
		bear_pin = br_ratio <= br_ratio_value and cClose[-i] <= cLow[-i] + (cHigh[-i] - cLow[-i]) / candle_part
		bull_pin = br_ratio <= br_ratio_value and cClose[-i] >= cHigh[-i] - (cHigh[-i] - cLow[-i]) / candle_part
		
		# BULLISH PATTERN
		if bull_pin and cLow[-i] >= ema34[-1] >= ema89[-1] and range_percent >= range_percent_filter and atr_max >= atr_per >= atr_min:
			entry = cHigh[-i] * 1.0001
			stoploss = cLow[-i] * 0.9999
			takeprofit = entry + abs(entry - stoploss) * tp_multiplier
			risk_perc = abs(entry-stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
		
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						results.append(float(-(risk_perc / 100) * p_size - 0.0008 * p_size))
						if show_trades:
							print(f'{symbol} '
							      f'position size: {p_size}, '
							      f'result: {float(-(risk_perc / 100) * p_size - 0.0008 * p_size)}, '
							      f'entry: {-i} bars ago, '
							      f'price: {entry}, '
							      f'exit: {stoploss} '
							      f'(bull trade)')
						break
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						results.append(float((risk_perc / 100) * p_size * tp_multiplier - 0.0006 * p_size))
						if show_trades:
							print(f'{symbol} '
							      f'position size: {p_size}, '
							      f'result: {float((risk_perc / 100) * p_size * tp_multiplier - 0.0006 * p_size)}, '
							      f'entry: {-i} bars ago, '
							      f'price: {entry}, '
							      f'exit: {takeprofit} '
							      f'(bull trade)')
						break
					
					else:
						continue
		
		# BEARISH PATTERN
		if bear_pin and cHigh[-i] <= ema34[-1] <= ema89[-1] and range_percent >= range_percent_filter and atr_max >= atr_per >= atr_min:
			entry = cLow[-i] * 0.9999
			stoploss = cHigh[-i] * 1.0001
			takeprofit = entry - abs(entry - stoploss) * tp_multiplier
			risk_perc = abs(entry-stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						results.append(float(-(risk_perc / 100) * p_size - 0.0008 * p_size))
						if show_trades:
							print(f'{symbol} '
							      f'position size: {p_size}, '
							      f'result: {float(-(risk_perc / 100) * p_size - 0.0008 * p_size)}, '
							      f'entry: {-i} bars ago, '
							      f'price: {entry}, '
							      f'exit: {stoploss} '
							      f'(bear trade)')
						break
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						results.append(float((risk_perc / 100) * p_size * tp_multiplier - 0.0006 * p_size))
						if show_trades:
							print(f'{symbol} '
							      f'position size: {p_size}, '
							      f'result: {float((risk_perc / 100) * p_size * tp_multiplier - 0.0006 * p_size)}, '
							      f'entry: {-i} bars ago, '
							      f'price: {entry}, '
							      f'exit: {takeprofit} '
							      f'(bear trade)')
						break
					else:
						continue
			
	if len(results) == 0:
		return [0]
	else:
		return results

# url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + 'TOMOUSDT' + '&interval=' + '1h' + '&limit=999'
# data1 = get(url_klines).json()
#
# d1 = pd.DataFrame(data1)
# d1.columns = [
# 	'open_time',
# 	'cOpen',
# 	'cHigh',
# 	'cLow',
# 	'cClose',
# 	'cVolume',
# 	'close_time',
# 	'qav',
# 	'num_trades',
# 	'taker_base_vol',
# 	'taker_quote_vol',
# 	'is_best_match'
# 	]
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
# summ = 0
#
# for i in pinbar_analysis(cOpen, cHigh, cLow, cClose):
# 	summ += i[0]
# 	print(f'With result of {i[0]}, entry was {i[1]} bars ago, on price {i[2]} and closed on {i[3]} ({i[4]} trade)')
#
# print(summ)
