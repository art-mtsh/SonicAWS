import talipp.indicators.EMA

def tick_size(candle_index, cOpen, cHigh, cLow, cClose):
	all_ticks = list(cOpen[-candle_index:-candle_index - 200:-1]) + list(cHigh[-candle_index:-candle_index - 200:-1]) + list(cLow[-candle_index:-candle_index - 200:-1]) + list(cClose[-candle_index:-candle_index - 200:-1])
	all_ticks = sorted(all_ticks)
	
	diffs = 10
	
	for u in range(0, len(all_ticks) - 1):
		if 0 < all_ticks[-u] - all_ticks[-u - 1] < diffs:
			diffs = all_ticks[-u] - all_ticks[-u - 1]
	
	tick_size = diffs / (cClose[-candle_index] / 100)
	
	return tick_size

def williams_pr(i, length, cHigh, cLow, cClose):
	l_l = min(cLow[-i:-length - i:-1])
	h_h = max(cHigh[-i:-length - i:-1])
	if (h_h - l_l) != 0:
		return (h_h - cClose[-i]) / (h_h - l_l) * -100
	else:
		return 1
	
def average_atr(candle_index, length, cHigh, cLow, cClose):
	atr = (sum(sum([cHigh[-candle_index:-candle_index - length:-1] - cLow[-candle_index:-candle_index - length:-1]])) / len(cClose[-candle_index:-candle_index - length:-1]))
	atr_per = atr / (cClose[-candle_index] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	return atr_per

def ema_directed(i, cHigh, cLow, cClose):
	ema50 = talipp.indicators.EMA(period=50, input_values=list(cClose[0: len(cClose) - i]))
	ema65 = talipp.indicators.EMA(period=65, input_values=list(cClose[0: len(cClose) - i]))
	ema185 = talipp.indicators.EMA(period=185, input_values=list(cClose[0: len(cClose) - i]))
	ema200 = talipp.indicators.EMA(period=200, input_values=list(cClose[0: len(cClose) - i]))
	
	if cLow[-i] >= ema50[-1] >= ema65[-1] >= ema185[-1] >= ema200[-1]:
		return "bull"
	elif cHigh[-i] <= ema50[-1] <= ema65[-1] <= ema185[-1] <= ema200[-1]:
		return "bear"
	else:
		return "sleep"

def avg_brr(candle_index, length, cOpen, cHigh, cLow, cClose):
	br_ranges = []
	
	for b in range(candle_index + 1, candle_index + length):
		
		if (cHigh[-b] - cLow[-b]) != 0:
			br_ranges.append(abs(cOpen[-b] - cClose[-b]) / ((cHigh[-b] - cLow[-b]) / 100))
	
	if len(br_ranges) != 0:
		return sum(br_ranges) / len(br_ranges)
	else:
		return 0

def room_ttl(candle_index, cHigh, cLow):
	low_room = 0
	high_room = 0
	
	for i in range(1, 100):
		if cLow[-candle_index] <= cLow[-candle_index - i]:
			low_room += 1
		else:
			break
	
	for i in range(1, 100):
		if cHigh[-candle_index] >= cHigh[-candle_index - i]:
			high_room += 1
		else:
			break
	
	return {'low_room': low_room, 'high_room': high_room}

def bar_ratio_range(i, cOpen, cHigh, cLow, cClose):
	pin_range_percent: float
	br_ratio: float
	
	if (cHigh[-i] - cLow[-i]) != 0:
		pin_range_percent = (cHigh[-i] - cLow[-i]) / (cClose[-i] / 100)
		br_ratio = abs(cOpen[-i] - cClose[-i]) / ((cHigh[-i] - cLow[-i]) / 100)
	else:
		pin_range_percent = 0
		br_ratio = 0
	
	return {"range percent": pin_range_percent, "body/range ratio": br_ratio}

def pin(i, brr_filter, candle_part, cOpen, cHigh, cLow, cClose):
	br_ratio = bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	
	if br_ratio <= brr_filter:
		
		if cClose[-i] <= cLow[-i] + (cHigh[-i] - cLow[-i]) / candle_part:
			return "bear"
		elif cClose[-i] >= cHigh[-i] - (cHigh[-i] - cLow[-i]) / candle_part:
			return "bull"
	else:
		return "sleep"

def inbar(i, brr_filter, mb_size, min_bar_range, max_bar_range, cOpen, cHigh, cLow, cClose):
	br_ratio = bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	ib_range_percent = bar_ratio_range(i, cOpen, cHigh, cLow, cClose).get("range percent")
	
	if br_ratio >= brr_filter and min_bar_range <= ib_range_percent <= max_bar_range and abs(cOpen[-i] - cClose[-i]) * mb_size <= abs(cOpen[-i-1] - cClose[-i-1]):
		
		if cClose[-i] > cOpen[-i] and cClose[-i-1] < cOpen[-i-1]:
			return "bear"
		elif cClose[-i] < cOpen[-i] and cClose[-i-1] > cOpen[-i-1]:
			return "bull"
	else:
		return "sleep"

def order(i, direction, revert, risk, rr_ratio, cHigh, cLow, cClose):
	if direction == "bull":
		if revert:
			entry = cHigh[-i] * 1.0002
			# entry = (cHigh[-candle_index] + cLow[-candle_index]) / 2
			takeprofit = cLow[-i] * 0.9998
			stoploss = entry + abs(entry - takeprofit) * rr_ratio
		else:
			entry = cHigh[-i] * 1.0002
			# entry = (cHigh[-candle_index] + cLow[-candle_index]) / 2
			stoploss = cLow[-i] * 0.9998
			takeprofit = entry + abs(entry - stoploss) * rr_ratio
		
		risk_perc = abs(entry - stoploss) / (cClose[-i] / 100)
		p_size = risk / risk_perc * 100
		
		if revert:
			loss = float(-(risk_perc / 100) * p_size * rr_ratio - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
		else:
			loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size * rr_ratio - 0.0006 * p_size)
	
	elif direction == "bear":
		if revert:
			entry = cLow[-i] * 0.9998
			# entry = (cHigh[-candle_index] + cLow[-candle_index]) / 2
			takeprofit = cHigh[-i] * 1.0002
			stoploss = entry - abs(entry - takeprofit) * rr_ratio
		else:
			entry = cLow[-i] * 0.9998
			# entry = (cHigh[-candle_index] + cLow[-candle_index]) / 2
			stoploss = cHigh[-i] * 1.0002
			takeprofit = entry - abs(entry - stoploss) * rr_ratio
		
		risk_perc = abs(entry - stoploss) / (cClose[-i] / 100)
		p_size = risk / risk_perc * 100
		
		if revert:
			loss = float(-(risk_perc / 100) * p_size * rr_ratio - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
		else:
			loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size * rr_ratio - 0.0006 * p_size)
	
	else:
		entry = None
		stoploss = None
		takeprofit = None
		p_size = None
		loss = None
		take = None
	
	return {"entry": entry, "stoploss": stoploss, "takeprofit": takeprofit, "position size": p_size, "loss": loss, "take": take}

