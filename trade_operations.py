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


def average_atr(candle_index, cHigh, cLow, cClose):
	atr = (sum(sum([cHigh[-candle_index:-candle_index - 24:-1] - cLow[-candle_index:-candle_index - 24:-1]])) / len(cClose[-candle_index:-candle_index - 24:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	return atr_per

def ema_directed(candle_index, cClose):
	ema33 = talipp.indicators.EMA(period=33, input_values=list(cClose[0: len(cClose) - candle_index]))
	ema66 = talipp.indicators.EMA(period=66, input_values=list(cClose[0: len(cClose) - candle_index]))
	ema100 = talipp.indicators.EMA(period=100, input_values=list(cClose[0: len(cClose) - candle_index]))
	ema133 = talipp.indicators.EMA(period=133, input_values=list(cClose[0: len(cClose) - candle_index]))
	ema166 = talipp.indicators.EMA(period=166, input_values=list(cClose[0: len(cClose) - candle_index]))
	ema200 = talipp.indicators.EMA(period=200, input_values=list(cClose[0: len(cClose) - candle_index]))

	if ema33[-1] >= ema66[-1] >= ema100[-1] >= ema133[-1] >= ema166[-1] >= ema200[-1]:
		return "bull"
	elif ema33[-1] <= ema66[-1] <= ema100[-1] <= ema133[-1] <= ema166[-1] <= ema200[-1]:
		return "bear"
	else:
		return "sleep"
	
def donchian_middle(candle_index, length, cHigh, cLow):
	d_min = min(cLow[-candle_index:-length - candle_index:-1])
	d_max = max(cHigh[-candle_index:-length - candle_index:-1])
	d_mid = (d_min + d_max) / 2
	
	return d_mid

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

def curr_brr(candle_index, cOpen, cHigh, cLow, cClose):
	pin_range_percent: float
	br_ratio: float
	
	if (cHigh[-candle_index] - cLow[-candle_index]) != 0:
		pin_range_percent = (cHigh[-candle_index] - cLow[-candle_index]) / (cClose[-candle_index] / 100)
		br_ratio = abs(cOpen[-candle_index] - cClose[-candle_index]) / ((cHigh[-candle_index] - cLow[-candle_index]) / 100)
	else:
		pin_range_percent = 0
		br_ratio = 0
	
	return {"range percent": pin_range_percent, "body/range ratio": br_ratio}

def inside_bar(candle_index, cOpen, cHigh, cLow, cClose):
	if cOpen[-candle_index-1] <= cClose[-candle_index-1] and cLow[-candle_index] >= cLow[-candle_index-1]:
		return "bull"
	elif cOpen[-candle_index-1] >= cClose[-candle_index-1] and cHigh[-candle_index] <= cHigh[-candle_index-1]:
		return "bear"
	else:
		return "sleep"

def pin(candle_index, brr_filter, candle_part, min_bar_range, max_bar_range, cOpen, cHigh, cLow, cClose):
	br_ratio = curr_brr(candle_index, cOpen, cHigh, cLow, cClose).get("body/range ratio")
	range_percent = curr_brr(candle_index, cOpen, cHigh, cLow, cClose).get("range percent")
	
	if min_bar_range <= range_percent <= max_bar_range:
		
		if br_ratio <= brr_filter and cClose[-candle_index] <= cLow[-candle_index] + (cHigh[-candle_index] - cLow[-candle_index]) / candle_part:
			return "bear"
		elif br_ratio <= brr_filter and cClose[-candle_index] >= cHigh[-candle_index] - (cHigh[-candle_index] - cLow[-candle_index]) / candle_part:
			return "bull"
	else:
		return "sleep"
	
def order(candle_index, direction, revert, risk, rr_ratio, cHigh, cLow, cClose):
	
	if direction == "bull":
		if revert:
			entry = cHigh[-candle_index] * 1.0003
			takeprofit = cLow[-candle_index] * 0.9997
			stoploss = entry + abs(entry - takeprofit) * rr_ratio
		else:
			entry = cHigh[-candle_index] * 1.0003
			stoploss = cLow[-candle_index] * 0.9997
			takeprofit = entry + abs(entry - stoploss) * rr_ratio
		
		risk_perc = abs(entry - stoploss) / (cClose[-candle_index] / 100)
		p_size = risk / risk_perc * 100
		
		if revert:
			loss = float(-(risk_perc / 100) * p_size * rr_ratio - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size - 0.0006 * p_size)
		else:
			loss = float(-(risk_perc / 100) * p_size - 0.0008 * p_size)
			take = float((risk_perc / 100) * p_size * rr_ratio - 0.0006 * p_size)

	elif direction == "bear":
		if revert:
			entry = cLow[-candle_index] * 0.9997
			takeprofit = cHigh[-candle_index] * 1.0003
			stoploss = entry - abs(entry - takeprofit) * rr_ratio
		else:
			entry = cLow[-candle_index] * 0.9997
			stoploss = cHigh[-candle_index] * 1.0003
			takeprofit = entry - abs(entry - stoploss) * rr_ratio
		
		risk_perc = abs(entry - stoploss) / (cClose[-candle_index] / 100)
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

	