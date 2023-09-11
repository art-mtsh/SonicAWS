import trade_operations as to


def ib_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, revert, risk, rr_ratio, show_trades, cOpen, cHigh, cLow, cClose, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# AVERAGE ATR
	atr_per = to.average_atr(i, cHigh, cLow, cClose)
	
	# AVERAGE BODY/RANGE RATIO
	avg_brratio = to.avg_brr(i, 24, cOpen, cHigh, cLow, cClose)
	
	# PIN DEFINITION
	ib_status = to.inbar(i, brr_filter=50, mb_size=3, min_bar_range=0.2, max_bar_range=3, cOpen=cOpen, cHigh=cHigh, cLow=cLow, cClose=cClose)
	
	if tick_size <= ts_filter and atr_per >= atr_filter and avg_brratio >= avg_brr_filter:
		# BULLISH PATTERN
		if ib_status == "bull": # and to.ema_directed(i, cClose) == "bull":
			
			order_details = to.order(i, "bull", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = order_details.get("stoploss")
			takeprofit = order_details.get("takeprofit")
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")

			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Inbar at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
								  f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						# print(f"sl ib on {symbol}")
						return [s, loss, float("{:.2f}".format(0.0008 * p_size))]
						
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Inbar at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						# print(f"tp ib on {symbol}")
						return [s, take, float("{:.2f}".format(0.0006 * p_size))]
				return [i, 0, 0]
			else:
				# print(f"no entry on bull ib {symbol}")
				return [i, 0, 0]
		
		# BEARISH PATTERN
		elif ib_status == "bear": # and to.ema_directed(i, cClose) == "bear":
			
			order_details = to.order(i, "bear", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = order_details.get("stoploss")
			takeprofit = order_details.get("takeprofit")
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 1, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Inbar at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						# print(f"sl ib on {symbol}")
						return [s, loss, float("{:.2f}".format(0.0008 * p_size))]
					
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Inbar at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						# print(f"tp ib on {symbol}")
						return [s, take, float("{:.2f}".format(0.0006 * p_size))]
				return [i, 0, 0]
			else:
				# print(f"no entry on bear ib {symbol}")
				return [i, 0, 0]
		else:
			# print(f"bull/bear ib pattern {symbol}")
			return [i, 0, 0]
	else:
		# print(f"no ib filter on {symbol}")
		return [i, 0, 0]
	