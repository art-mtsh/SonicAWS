import trade_operations as to
import talipp.indicators.EMA
from talipp.ohlcv import OHLCV

def pinbar_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, room_filter, volume_room_filter, revert, risk, rr_ratio, pin_maxrange, pin_minrange, show_trades, cOpen, cHigh, cLow, cClose, cVolume, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# INDICATIORS
	ema50 = talipp.indicators.EMA(period=50, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema100 = talipp.indicators.EMA(period=100, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema150 = talipp.indicators.EMA(period=150, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema200 = talipp.indicators.EMA(period=200, input_values=list(cClose[0: len(cClose) - i + 1]))
	
	# ohlcv_list = []
	#
	# for h in range(-50 - i, 1 - i):
	# 	talipp_ohlcv = OHLCV(cOpen[h], cHigh[h], cLow[h], cClose[h], cVolume[h])
	# 	ohlcv_list.append(talipp_ohlcv)
	#
	# talipp_stoch = talipp.indicators.Stoch(period=5, smoothing_period=3, input_values=ohlcv_list)
	# stochastic1 = talipp_stoch[-1]
	# stochastic2 = talipp_stoch[-2]
	
	williams = to.williams_pr(i, 14, cHigh, cLow, cClose)
	
	# range1 = to.bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("range percent")
	# range2 = to.bar_ratio_range(i+1, cOpen, cHigh, cLow, cClose).get("range percent")
	# range3 = to.bar_ratio_range(i+2, cOpen, cHigh, cLow, cClose).get("range percent")
	#
	# brr1 = to.bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	# brr2 = to.bar_ratio_range(i+1, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	# brr3 = to.bar_ratio_range(i+2, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	#
	# range_min = 0.3
	# range_max = 0.7
	# brr_min = 33
	
	if tick_size <= ts_filter:
		
		high_under_ema = 0
		low_above_ema = 0
		
		for s in range(1, 50):
			if cHigh[-i-s+1] < ema200[-s]:
				high_under_ema += 1
			else:
				break
				
		for s in range(1, 50):
			if cLow[-i-s+1] > ema200[-s]:
				low_above_ema += 1
			else:
				break
		
		# ================== BULL ==================
		if williams <= -95 and \
			cLow[-i] > ema50[-1] >= ema100[-1] >= ema150[-1] >= ema200[-1] and \
			low_above_ema >= 30 and \
			0.8 >= abs(cHigh[-i] * 1.0002 - ema50[-1]) / (cClose[-i] / 100) >= 0.4:
			
			entry = cHigh[-i] * 1.0002
			stoploss = ema50[-1]
			takeprofit = entry + abs(entry - stoploss) * rr_ratio
			risk_perc = abs(entry - stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
			
			if revert:
				loss = float(-(risk_perc / 100) * p_size * rr_ratio - 0.0008 * p_size)
				take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
			else:
				loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
				take = float((risk_perc / 100) * p_size * rr_ratio - 0.0006 * p_size)

			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  f'EMA50: {float("{:.4f}".format(ema50[-1]))}, '
							      f'WILL: {float("{:.4f}".format(williams))}, '
							      f'size: ${int(p_size)}, '
								  f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$), '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						return [s, loss, float("{:.2f}".format(0.0008 * p_size))]
						
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  f'EMA50: {float("{:.4f}".format(ema50[-1]))}, '
							      f'WILL: {float("{:.4f}".format(williams))}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$), '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						return [s, take, float("{:.2f}".format(0.0006 * p_size))]
					else:
						continue
				return [i, 0, 0]
			else:
				return [i, 0, 0]
		
		# ================== BEAR ==================
		elif williams >= -5 and \
			cHigh[-i] < ema50[-1] <= ema100[-1] <= ema150[-1] <= ema200[-1] and \
			high_under_ema >= 30 and \
			0.8 >= abs(cLow[-i] * 0.9998 - ema50[-1]) / (cClose[-i] / 100) >= 0.4:
			
			entry = cLow[-i] * 0.9998
			stoploss = ema50[-1]
			takeprofit = entry - abs(entry - stoploss) * rr_ratio
			risk_perc = abs(entry - stoploss) / (cClose[-i] / 100)
			p_size = risk / risk_perc * 100
			
			if revert:
				loss = float(-(risk_perc / 100) * p_size * rr_ratio - 0.0008 * p_size)
				take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
			else:
				loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
				take = float((risk_perc / 100) * p_size * rr_ratio - 0.0006 * p_size)
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  f'EMA50: {float("{:.4f}".format(ema50[-1]))}, '
							      f'WILL: {float("{:.4f}".format(williams))}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$), '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						return [s, loss, float("{:.2f}".format(0.0008 * p_size))]
					
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  f'EMA50: {float("{:.4f}".format(ema50[-1]))}, '
							      f'WILL: {float("{:.4f}".format(williams))}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$), '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						return [s, take, float("{:.2f}".format(0.0006 * p_size))]
					else:
						continue
				return [i, 0, 0]
			else:
				return [i, 0, 0]
		else:
			return [i, 0, 0]
	else:
		return [i, 0, 0]
	