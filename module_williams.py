import trade_operations as to
import talipp.indicators.EMA
# from talipp.ohlcv import OHLCV


def w_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, room_filter, volume_room_filter, revert, risk, rr_ratio, pin_maxrange, pin_minrange, show_trades, cOpen, cHigh, cLow, cClose, cVolume, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# INDICATIORS
	ema50 = talipp.indicators.EMA(period=50, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema100 = talipp.indicators.EMA(period=100, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema150 = talipp.indicators.EMA(period=150, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema200 = talipp.indicators.EMA(period=200, input_values=list(cClose[0: len(cClose) - i + 1]))
	
	l_l_30 = min(cLow[-i:-30 - i:-1])
	h_h_30 = max(cHigh[-i:-30 - i:-1])
	
	l_l_60 = min(cLow[-i:-60 - i:-1])
	h_h_60 = max(cHigh[-i:-60 - i:-1])
	
	mid_60 = (l_l_60 + h_h_60) / 2

	williams = to.williams_pr(i, 14, cHigh, cLow, cClose)
	
	if tick_size <= ts_filter:
		
		high_under_ema = 0
		low_above_ema = 0
		
		for s in range(1, 50):
			if cHigh[-i - s + 1] < ema200[-s]:
				high_under_ema += 1
			else:
				break
		
		for s in range(1, 50):
			if cLow[-i - s + 1] > ema200[-s]:
				low_above_ema += 1
			else:
				break
				
		# =================== SELL УМОВИ ===================
		if williams >= -5 and \
			cHigh[-i] < ema50[-1] <= ema100[-1] <= ema150[-1] <= ema200[-1] and \
			high_under_ema >= 30 and \
			0.8 >= abs(cLow[-i] * 0.9998 - ema50[-1]) / (cClose[-i] / 100) >= 0.4:
			
			sell_entry = cLow[-i] * 0.9998
			sell_stoploss = ema50[-1]
			sell_takeprofit = sell_entry - abs(sell_entry - sell_stoploss) * rr_ratio
			risk_perc = abs(sell_entry - sell_stoploss) / (cClose[-i] / 100)
			sell_size = risk / risk_perc * 100
			
			if revert:
				loss = float(-(risk_perc / 100) * sell_size * rr_ratio - 0.0008 * sell_size)
				take = float((risk_perc / 100) * sell_size - 0.0006 * sell_size)
			else:
				loss = float(-(risk_perc / 100) * sell_size - 0.0008 * sell_size)
				take = float((risk_perc / 100) * sell_size * rr_ratio - 0.0006 * sell_size)
			
			# =================== ВХІД ===================
			if cHigh[-i+1] >= sell_entry >= cLow[-i+1]:
			# =================== ЦИКЛ ВИХОДУ ===================
				for s in range(i, 1, -1):
					if cHigh[-s] >= sell_stoploss >= cLow[-s]:
						return [
							i,
							cTime[-i],
							cTime[-s],
							symbol,
							cOpen[-i],
							cHigh[-i],
							cLow[-i],
							cClose[-i],
							cVolume[-i],
							mid_60,
							int(sell_size),
							float("{:.2f}".format(loss)),
							float("{:.2f}".format(0.0008 * sell_size)), # fee
							float("{:.5f}".format(sell_entry)),
							float("{:.5f}".format(sell_stoploss)),
							float("{:.5f}".format(sell_takeprofit)),
							"SELL",
							s
						]
					
					elif cHigh[-s] >= sell_takeprofit >= cLow[-s]:
						return [
							i,
							cTime[-i],
							cTime[-s],
							symbol,
							cOpen[-i],
							cHigh[-i],
							cLow[-i],
							cClose[-i],
							cVolume[-i],
							mid_60,
							int(sell_size),
							float("{:.2f}".format(take)),
							float("{:.2f}".format(0.0006 * sell_size)), # fee
							float("{:.5f}".format(sell_entry)),
							float("{:.5f}".format(sell_stoploss)),
							float("{:.5f}".format(sell_takeprofit)),
							"SELL",
							s
						]
					else:
						continue
				return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]
			return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]
		
		# =================== BUY УМОВИ ===================
		if williams <= -95 and \
			cLow[-i] > ema50[-1] >= ema100[-1] >= ema150[-1] >= ema200[-1] and \
			low_above_ema >= 30 and \
			0.8 >= abs(cHigh[-i] * 1.0002 - ema50[-1]) / (cClose[-i] / 100) >= 0.4:
			
			buy_entry = cHigh[-i] * 1.0002
			buy_stoploss = ema50[-1]
			buy_takeprofit = buy_entry + abs(buy_entry - buy_stoploss) * rr_ratio
			risk_perc = abs(buy_entry - buy_stoploss) / (cClose[-i] / 100)
			buy_size = risk / risk_perc * 100
			
			if revert:
				loss = float(-(risk_perc / 100) * buy_size * rr_ratio - 0.0008 * buy_size)
				take = float((risk_perc / 100) * buy_size - 0.0006 * buy_size)
			else:
				loss = float(-(risk_perc / 100) * buy_size - 0.0008 * buy_size)
				take = float((risk_perc / 100) * buy_size * rr_ratio - 0.0006 * buy_size)
			
			if cHigh[-i + 1] >= buy_entry >= cLow[-i + 1]:
			# =================== ЦИКЛ ВИХОДУ ===================
				for s in range(i, 1, -1):
					if cHigh[-s] >= buy_stoploss >= cLow[-s]:
						return [
							i,
							cTime[-i],
							cTime[-s],
							symbol,
							cOpen[-i],
							cHigh[-i],
							cLow[-i],
							cClose[-i],
							cVolume[-i],
							mid_60,
							int(buy_size),
							float("{:.2f}".format(loss)),
							float("{:.2f}".format(0.0008 * buy_size)),  # fee
							float("{:.5f}".format(buy_entry)),
							float("{:.5f}".format(buy_stoploss)),
							float("{:.5f}".format(buy_takeprofit)),
							"BUY",
							s
						]
						
					elif cHigh[-s] >= buy_takeprofit >= cLow[-s]:
						return [
							i,
							cTime[-i],
							cTime[-s],
							symbol,
							cOpen[-i],
							cHigh[-i],
							cLow[-i],
							cClose[-i],
							cVolume[-i],
							mid_60,
							int(buy_size),
							float("{:.2f}".format(take)),
							float("{:.2f}".format(0.0006 * buy_size)),  # fee
							float("{:.5f}".format(buy_entry)),
							float("{:.5f}".format(buy_stoploss)),
							float("{:.5f}".format(buy_takeprofit)),
							"BUY",
							s
						]
					
					else:
						continue
				return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]
			return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]
		return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]
	return [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0", 0]