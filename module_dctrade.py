import trade_operations as to
import talipp.indicators.EMA
# from talipp.ohlcv import OHLCV


def dc_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, room_filter, volume_room_filter, revert, risk, rr_ratio, pin_maxrange, pin_minrange, show_trades, cOpen, cHigh, cLow, cClose, cVolume, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# INDICATIORS
	# ema33 = ema(period=50, input_values=list(cClose[0: len(cClose) - i + 1]))
	# ema66 = ema(period=80, input_values=list(cClose[0: len(cClose) - i + 1]))
	# ema99 = ema(period=220, input_values=list(cClose[0: len(cClose) - i + 1]))
	ema250 = talipp.indicators.EMA(period=250, input_values=list(cClose[0: len(cClose) - i + 1]))
	
	l_l_30 = min(cLow[-i:-30 - i:-1])
	h_h_30 = max(cHigh[-i:-30 - i:-1])
	
	l_l_60 = min(cLow[-i:-120 - i:-1])
	h_h_60 = max(cHigh[-i:-120 - i:-1])
	
	mid_60 = (l_l_60 + h_h_60) / 2
	
	sell_profit_range = abs(l_l_30 - l_l_60) / (cClose[-i] / 100)
	sell_loss_range = abs(l_l_30 - h_h_60) / (cClose[-i] / 100)
	buy_profit_range = abs(h_h_30 - h_h_60) / (cClose[-i] / 100)
	buy_loss_range = abs(h_h_30 - l_l_60) / (cClose[-i] / 100)
	
	
	if tick_size <= ts_filter:
		sell_entry = 0
		buy_entry = 0

		min_range_filter = 0.6
		max_range_filter = 3.0

		if max_range_filter >= sell_profit_range >= min_range_filter and max_range_filter >= sell_loss_range >= min_range_filter:
			sell_entry = l_l_30

		if max_range_filter >= buy_profit_range >= min_range_filter and max_range_filter >= buy_loss_range >= min_range_filter:
			buy_entry = h_h_30
		
		# =================== SELL TRADE ===================
		if cHigh[-i + 1] >= sell_entry >= cLow[-i + 1] and \
			cLow[-i] >= sell_entry and \
			cHigh[-i] <= ema250[-1] and \
			cHigh[-i] <= mid_60:
			
			sell_stoploss = h_h_60
			sell_takeprofit = l_l_60
			
			sell_stop_perc = abs(sell_entry - sell_stoploss) / (cClose[-i] / 100)
			sell_take_perc = abs(sell_entry - sell_takeprofit) / (cClose[-i] / 100)

			sell_size = risk / sell_stop_perc * 100
			
			loss = float(-(sell_stop_perc / 100) * sell_size - 0.0008 * sell_size)
			take = float((sell_take_perc / 100) * sell_size - 0.0006 * sell_size)
			
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
		
		# =================== BUY TRADE ===================
		if cHigh[-i + 1] >= buy_entry >= cLow[-i + 1] and \
			cHigh[-i] <= buy_entry and \
			cLow[-i] >= ema250[-1] and \
			cLow[-i] >= mid_60:
			
			buy_stoploss = l_l_60
			buy_takeprofit = h_h_60
			
			buy_stop_perc = abs(buy_entry - buy_stoploss) / (cClose[-i] / 100)
			buy_take_perc = abs(buy_entry - buy_takeprofit) / (cClose[-i] / 100)
			
			buy_size = risk / buy_stop_perc * 100
			
			loss = float(-(buy_stop_perc / 100) * buy_size - 0.0008 * buy_size)
			take = float((buy_take_perc / 100) * buy_size - 0.0006 * buy_size)
			
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