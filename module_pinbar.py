import talipp.indicators.EMA
import pandas as pd
from requests import get
from multiprocessing import Process, Queue
import telebot
import time
import datetime




tick_size_filter = 0.02
analysis_length = 24

# PIN PARAMETERS
candle_part = 5
pin_br_ratio_value = 8

pin_range_percent_filter_min = 0.00
pin_range_percent_filter_max = 100 # off

room_to_the_left = 1

avg_br_ratio_value = 0
avg_atr_min = 0.00
avg_atr_max = 100 # off

risk_reward = 2
risk = 20

show_trades = True
revert = False

def pinbar_analysis(symbol, cOpen, cHigh, cLow, cClose, cTime):

	results = []

	for i in range(745, 24, -1):
		
		print(i)
		
		# TICK SIZE
		all_ticks = list(cOpen[-i:-i-200:-1]) + list(cHigh[-i:-i-200:-1]) + list(cLow[-i:-i-200:-1]) + list(cClose[-i:-i-200:-1])
		all_ticks = sorted(all_ticks)

		diffs = 10

		for u in range(0, len(all_ticks) - 1):
			if 0 < all_ticks[-u] - all_ticks[-u - 1] < diffs:
				diffs = all_ticks[-u] - all_ticks[-u - 1]

		tick_size = diffs / (cClose[-i] / 100)
		
		# AVERAGE ATR
		atr = (sum(sum([cHigh[-i:-i-analysis_length:-1] - cLow[-i:-i-analysis_length:-1]])) / len(cClose[-i:-i-analysis_length:-1]))
		atr_per = atr / (cClose[-1] / 100)
		atr_per = float('{:.2f}'.format(atr_per))
		
		# EMA
		ema33 = talipp.indicators.EMA(period=33, input_values=list(cClose[0: len(cClose) - i]))
		ema66= talipp.indicators.EMA(period=66, input_values=list(cClose[0: len(cClose) - i]))
		ema100 = talipp.indicators.EMA(period=100, input_values=list(cClose[0: len(cClose) - i]))
		ema133 = talipp.indicators.EMA(period=133, input_values=list(cClose[0: len(cClose) - i]))
		ema166 = talipp.indicators.EMA(period=166, input_values=list(cClose[0: len(cClose) - i]))
		ema200 = talipp.indicators.EMA(period=200, input_values=list(cClose[0: len(cClose) - i]))

		# print(f'{symbol} {cTime[-i].strftime("%Y-%m-%d %H:%M:%S")}, ema24: {ema24[-1]}, ema48: {ema48[-1]}, ema96: {ema96[-1]}')
		
		# DONCHIAN
		# d_min = min(cLow[-i:-indicator_length - i:-1])
		# d_max = max(cHigh[-i:-indicator_length - i:-1])
		# d_mid = (d_min + d_max) / 2
		
		# AVERAGE BODY/RANGE RATIO
		br_ranges = []
		
		for b in range(i+1, i+analysis_length):
			
			if (cHigh[-b] - cLow[-b]) != 0:
				br_ranges.append(abs(cOpen[-b] - cClose[-b]) / ((cHigh[-b] - cLow[-b]) / 100))
		
		if len(br_ranges) != 0:
			avg_br_ratio = sum(br_ranges) / len(br_ranges)
		else:
			avg_br_ratio = 0
		
		# PIN BODY/RANGE RATIO
		pin_range_percent: float
		br_ratio: float
		
		if (cHigh[-i] - cLow[-i]) != 0:
			pin_range_percent = (cHigh[-i] - cLow[-i]) / (cClose[-i] / 100)
			br_ratio = abs(cOpen[-i] - cClose[-i]) / ((cHigh[-i] - cLow[-i]) / 100)
		else:
			pin_range_percent = 0
			br_ratio = 0
			
		# PIN DEFINITION
		bear_pin = br_ratio <= pin_br_ratio_value and cClose[-i] <= cLow[-i] + (cHigh[-i] - cLow[-i]) / candle_part
		bull_pin = br_ratio <= pin_br_ratio_value and cClose[-i] >= cHigh[-i] - (cHigh[-i] - cLow[-i]) / candle_part
		
		# PIN VOLATILITY
		beautiful_pin = pin_range_percent_filter_max >= pin_range_percent >= pin_range_percent_filter_min
		beautiful_past = tick_size <= tick_size_filter and avg_br_ratio >= avg_br_ratio_value and avg_atr_max >= atr_per >= avg_atr_min
		
		# ROOM TO THE LEFT
		bullish_room = cLow[-i] <= min(cLow[-i:-i - room_to_the_left:-1])
		bearish_room = cHigh[-i] >= max(cHigh[-i:-i - room_to_the_left:-1])
		
		# INSIDE PINBAR
		bullish_pin_inside = cOpen[-i-3] <= cClose[-i-3] and cOpen[-i-2] <= cClose[-i-2] and cOpen[-i-1] <= cClose[-i-1] and cLow[-i] >= cLow[-i-1]
		bearish_room_inside = cOpen[-i-3] >= cClose[-i-3] and cOpen[-i-2] >= cClose[-i-2] and cOpen[-i-1] >= cClose[-i-1] and cHigh[-i] <= cHigh[-i-1]
		
		# BULLISH PATTERN
		if bull_pin and beautiful_pin and beautiful_past and bullish_room and ema33[-1] >= ema66[-1] >= ema100[-1] >= ema133[-1] >= ema166[-1] >= ema200[-1]:
			
			current_trade_index = i
			
			print("Found pin")
			
			if revert:
				entry = cHigh[-i] * 1.0003
				takeprofit = cLow[-i] * 0.9997
				stoploss = entry + abs(entry - takeprofit) * risk_reward
			else:
				entry = cHigh[-i] * 1.0003
				stoploss = cLow[-i] * 0.9997
				takeprofit = entry + abs(entry - stoploss) * risk_reward
				
			risk_perc = abs(entry-stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
			# p_size = 3000
		
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					
					if revert:
						loss = float(-(risk_perc / 100) * p_size * risk_reward - 0.0008 * p_size)
						take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
					else:
						loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
						take = float((risk_perc / 100) * p_size * risk_reward - 0.0006 * p_size)
						
					if cHigh[-s] >= stoploss >= cLow[-s]:
						results.append(loss)
						if show_trades:
							print(f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
								  f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))} '
							      f'enter_index: {current_trade_index}')
						
						current_trade_index = s - 1
						
						break
						
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						results.append(take)
						if show_trades:
							print(f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))} '
							      f'enter_index: {current_trade_index}')
							
						current_trade_index = s - 1
						
						break
					
					else:
						continue
						
			break
		
		# BEARISH PATTERN
		if bear_pin and beautiful_pin and beautiful_past and bearish_room and ema33[-1] <= ema66[-1] <= ema100[-1] <= ema133[-1] <= ema166[-1] <= ema200[-1]:
			
			current_trade_index = i
			
			print("Found pin")
			
			if revert:
				entry = cLow[-i] * 0.9997
				takeprofit = cHigh[-i] * 1.0003
				stoploss = entry - abs(entry - takeprofit) * risk_reward
			else:
				entry = cLow[-i] * 0.9997
				stoploss = cHigh[-i] * 1.0003
				takeprofit = entry - abs(entry - stoploss) * risk_reward
			
			risk_perc = abs(entry-stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
			# p_size = 3000
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					
					if revert:
						loss = float(-(risk_perc / 100) * p_size * risk_reward - 0.0008 * p_size)
						take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
					else:
						loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
						take = float((risk_perc / 100) * p_size * risk_reward - 0.0006 * p_size)
					
					if cHigh[-s] >= stoploss >= cLow[-s]:
						results.append(loss)
						if show_trades:
							print(f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))} '
							      f'enter_index: {current_trade_index}')
							
							current_trade_index = s - 1
							
						break
					
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						results.append(take)
						if show_trades:
							print(f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))} '
							      f'enter_index: {current_trade_index}')
							
							current_trade_index = s - 1
							
						break
					
					else:
						continue
			break
			
	if len(results) == 0:
		return [0]
	else:
		return results
#
#
url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + 'TOMOUSDT' + '&interval=' + '1h' + '&limit=999'
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
df1['close_time'] = pd.to_datetime(df1['close_time'], unit='ms')
cTime = df1['close_time'].iloc

cOpen = df1['cOpen'].to_numpy()
cHigh = df1['cHigh'].to_numpy()
cLow = df1['cLow'].to_numpy()
cClose = df1['cClose'].to_numpy()

pinbar_analysis("AAVEUSDT", cOpen, cHigh, cLow, cClose, cTime)
