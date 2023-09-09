import trade_operations as to

def pinbar_analysis(symbol, bar_index, ts_filter, atr_filter, avg_brr_filter, room_filter, revert, risk, rr_ratio, show_trades, cOpen, cHigh, cLow, cClose, cTime):

	i = bar_index

	# TICK SIZE
	tick_size = to.tick_size(i, cOpen, cHigh, cLow, cClose)
	
	# AVERAGE ATR
	atr_per = to.average_atr(i, cHigh, cLow, cClose)
	
	# AVERAGE BODY/RANGE RATIO
	avg_brratio = to.avg_brr(i, 24, cOpen, cHigh, cLow, cClose)
	
	# PIN DEFINITION
	pin_status = to.pin(i, 10, 5, 0.2, 3, cOpen, cHigh, cLow, cClose)
	
	# ROOM TO THE LEFT
	bullish_room = to.room_ttl(i, cHigh, cLow).get('low_room')
	bearish_room = to.room_ttl(i, cHigh, cLow).get('high_room')
	
	if tick_size <= ts_filter and atr_per >= atr_filter and avg_brratio >= avg_brr_filter:
		# BULLISH PATTERN
		if pin_status == "bull" and bullish_room >= room_filter:
			
			order_details = to.order(i, "bull", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = order_details.get("stoploss")
			takeprofit = order_details.get("takeprofit")
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")

			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
								  f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						return [s, loss]
						
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Pin at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						return [s, take]
					
					else:
						continue
			else:
				return [i, 0]
		else:
			return [i, 0]
		
		# BEARISH PATTERN
		if pin_status == "bear" and bearish_room >= room_filter:
			
			order_details = to.order(i, "bear", revert, risk, rr_ratio, cHigh, cLow, cClose)
			
			entry = order_details.get("entry")
			stoploss = order_details.get("stoploss")
			takeprofit = order_details.get("takeprofit")
			p_size = order_details.get("position size")
			loss = order_details.get("loss")
			take = order_details.get("take")
			
			# ВАРІАНТ ЗІ ВХОДОМ НА НАСТУПНОМУ Ж БАРІ
			if cHigh[-i+1] >= entry >= cLow[-i+1]:
				for s in range(i, 0, -1):
					if cHigh[-s] >= stoploss >= cLow[-s]:
						if show_trades:
							print(f'Pin at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(loss))}$ '
							      f'(fee: {float("{:.2f}".format(0.0008 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(stoploss))}, '
							      f'close at {s}')
						return [s, loss]
					
					elif cHigh[-s] >= takeprofit >= cLow[-s]:
						if show_trades:
							print(f'Pin at {i}, '
							      f'{cTime[-i].strftime("%Y-%m-%d %H:%M:%S")} {symbol}, '
							      f'size: ${int(p_size)}, '
							      f'pnl: {float("{:.2f}".format(take))}$ '
							      f'(fee: {float("{:.2f}".format(0.0006 * p_size))}$) '
							      f'entry: {float("{:.5f}".format(entry))}, '
							      f'exit: {float("{:.5f}".format(takeprofit))}, '
							      f'close at {s}')
						return [s, take]
					
					else:
						continue
			else:
				return [i, 0]
		else:
			return [i, 0]
	else:
		return [i, 0]