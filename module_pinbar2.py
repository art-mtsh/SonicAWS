import trade_operations as to


def pinbar_analysis(symbol, candle_index, risk, tick_size_filter, show_trades_val, avg_atr_filter, avg_brr_filter, room_filter, revert, rr_ratio, indicator_lenght, cOpen, cHigh, cLow, cClose, cTime):
	
	tick_size = to.tick_size(candle_index, cOpen, cHigh, cLow, cClose)
	average_atr = to.average_atr(candle_index, cHigh, cLow, cClose)
	ema_directed = to.ema_directed(candle_index, cClose)
	donchian_middle = to.donchian_middle(candle_index, indicator_lenght, cHigh, cLow)
	average_br_ratio = to.avg_brr(candle_index, indicator_lenght, cOpen, cHigh, cLow, cClose)
	room = to.room_ttl(candle_index, cHigh, cLow)
	ib = to.inside_bar(candle_index, cOpen, cHigh, cLow, cClose)
	
	pin = to.pin(candle_index, 10, 5, 0.2, 2, cOpen, cHigh, cLow, cClose)
	
	if tick_size <= tick_size_filter and average_atr >= avg_atr_filter and average_br_ratio >= avg_brr_filter:
		if	ema_directed == "bull" and room.get("low_room") >= room_filter and pin == "bull":
			
			order_details = to.order(candle_index, revert=revert, risk=risk, rr_ratio=rr_ratio, cHigh=cHigh, cLow=cLow, cClose=cClose)
			
			return to.position(candle_index,
			                   symbol,
			                   show_trades=show_trades_val,
			                   entry=order_details.get("entry"),
			                   stoploss=order_details.get("stoploss"),
			                   takeprofit=order_details.get("takeprofit"),
			                   rr_ratio=rr_ratio,
			                   risk_perc=order_details.get("risc percent"),
			                   p_size=order_details.get("position size"),
			                   revert=revert,
			                   cOpen=cOpen,
			                   cHigh=cHigh,
			                   cLow=cLow,
			                   cClose=cClose)
		
		elif ema_directed == "bear" and room.get("high_room") >= room_filter and pin == "bear":
			
			order_details = to.order(candle_index, revert=revert, risk=risk, rr_ratio=rr_ratio, cHigh=cHigh, cLow=cLow, cClose=cClose)
			
			return to.position(candle_index,
			                   symbol,
			                   show_trades=False,
			                   entry=order_details.get("entry"),
			                   stoploss=order_details.get("stoploss"),
			                   takeprofit=order_details.get("takeprofit"),
			                   rr_ratio=rr_ratio,
			                   risk_perc=order_details.get("risc percent"),
			                   p_size=order_details.get("position size"),
			                   revert=revert,
			                   cOpen=cOpen,
			                   cHigh=cHigh,
			                   cLow=cLow,
			                   cClose=cClose)
		
	else:
		return {"result": 0, "close bar coordinate": candle_index - 1}