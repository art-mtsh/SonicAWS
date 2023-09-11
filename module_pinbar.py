import trade_operations as to
import talipp.indicators.EMA
from talipp.ohlcv import OHLCV

def pinbar_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, room_filter, volume_room_filter, revert, risk, rr_ratio, pin_maxrange, pin_minrange, show_trades, cOpen, cHigh, cLow, cClose, cVolume, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# INDICATIORS
	ema20 = talipp.indicators.EMA(period=20, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema40 = talipp.indicators.EMA(period=40, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema60 = talipp.indicators.EMA(period=60, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema80 = talipp.indicators.EMA(period=80, input_values=list(cClose[0: len(cClose) - i + 1]))
	
	ohlcv_list = []
	
	for h in range(-50 - i, 1 - i):
		talipp_ohlcv = OHLCV(cOpen[h], cHigh[h], cLow[h], cClose[h], cVolume[h])
		ohlcv_list.append(talipp_ohlcv)
	
	talipp_stoch = talipp.indicators.Stoch(period=5, smoothing_period=5, input_values=ohlcv_list)
	stochastic1 = talipp_stoch[-1]
	stochastic2 = talipp_stoch[-2]
	
	range1 = to.bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("range percent")
	range2 = to.bar_ratio_range(i+1, cOpen, cHigh, cLow, cClose).get("range percent")
	range3 = to.bar_ratio_range(i+2, cOpen, cHigh, cLow, cClose).get("range percent")
	
	brr1 = to.bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	brr2 = to.bar_ratio_range(i+1, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	brr3 = to.bar_ratio_range(i+2, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	
	range_min = 0.3
	range_max = 0.7
	brr_min = 33
	
	if tick_size <= ts_filter:
		# BULLISH PATTERN
		
		high_under_ema = 0
		low_above_ema = 0
		
		for s in range(1, 50):
			if cHigh[-i-s+1] < ema80[-s]:
				high_under_ema += 1
			else:
				break
				
		for s in range(1, 50):
			if cLow[-i-s+1] > ema80[-s]:
				low_above_ema += 1
			else:
				break
		
		if stochastic2.d > stochastic1.d < 20 and \
			cClose[-i] < cOpen[-i] and \
			cLow[-i] > ema20[-1] >= ema40[-1] >= ema60[-1] >= ema80[-1] and \
			low_above_ema >= 30 and \
			0.5 >= abs(cLow[-i] - ema20[-1]) / (cClose[-i] / 100) >= 0.2:
			
			order_details = to.order(i, "bull", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = ema20[-1]
			takeprofit = entry + abs(entry - stoploss) * rr_ratio
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")

			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i+3}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  # f'EMA80: {ema80[-1]}, '
							      # f'STOCH: {stochastic1.d}, '
							      f'size: ${int(p_size)}, '
								  f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$), '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						return [s, loss, float("{:.2f}".format(0.0008 * p_size))]
						
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i+3}, '
							      f'{cTime[-i+3].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  # f'EMA80: {ema80[-1]}, '
							      # f'STOCH: {stochastic1.d}, '
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
		
		# BEARISH PATTERN
		elif stochastic2.d < stochastic1.d > 80 and \
			cClose[-i] > cOpen[-i] and \
			cHigh[-i] < ema20[-1] <= ema40[-1] <= ema60[-1] <= ema80[-1] and \
			high_under_ema >= 30 and \
			0.5 >= abs(cHigh[-i] - ema20[-1]) / (cClose[-i] / 100) >= 0.2:
			
			order_details = to.order(i, "bear", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = ema20[-1]
			takeprofit = entry - abs(entry - stoploss) * rr_ratio
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {-i+3}, '
							      f'{cTime[-i+3].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
                                  # f'EMA80: {ema80[-1]}, '
							      # f'STOCH: {stochastic1.d}, '
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
							      f'{cTime[-i+3].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
                                  # f'O: {cOpen[-i]}, '
							      # f'H: {cHigh[-i]}, '
							      # f'L: {cLow[-i]}, '
							      # f'C: {cClose[-i]}, '
							      # f'V: {cVolume[-i]}, '
							      # f'EMA80: {ema80[-1]}, '
							      # f'STOCH: {stochastic1.d}, '
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
	