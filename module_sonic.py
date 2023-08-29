import talipp.indicators.EMA


def sonic_signal(cHigh, cLow, cClose, cloud_filter):

	# INDICATORS
	ema34_basis = talipp.indicators.EMA(period=34, input_values=cClose)
	ema34_low = talipp.indicators.EMA(period=34, input_values=cLow)
	ema34_high = talipp.indicators.EMA(period=34, input_values=cHigh)
	ema89 = talipp.indicators.EMA(period=89, input_values=cClose)
	ema233 = talipp.indicators.EMA(period=233, input_values=cClose)
	
	# TREND
	rising_dragon = ema34_low[-1] > ema89[-1] > ema233[-1]
	falling_dragon = ema34_high[-1] < ema89[-1] < ema233[-1]
	
	# CLOUDS
	cloud_above = 0
	cloud_below = 0
	
	for i in range(2, cloud_filter+2):
		if cLow[-i] < ema34_high[-i] or ema34_low[-i] < ema89[-i] or ema89[-i] < ema233[-i]:
			cloud_above += 1

		if cHigh[-i] > ema34_low[-i] or ema34_high[-i] > ema89[-i] or ema89[-i] > ema233[-1]:
			cloud_below += 1
	
	# FRESH
	fresh_above = False
	fresh_below = False
	
	for i in range(2, cloud_filter*2 + 2):
		if ema34_high[-i] >= ema89[-i]:
			fresh_above = True
		
		if ema34_low[-i] <= ema89[-i]:
			fresh_below = True
			
	# AVERAGE ATR
	atr = (sum(sum([cHigh[-1:-cloud_filter * 2 - 1:-1] - cLow[-1:-cloud_filter * 2 - 1:-1]])) / len(cClose[-1:-cloud_filter * 2 - 1:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	# ANGLE
	angle = abs(ema34_basis[-1] - ema34_basis[-cloud_filter*2-1]) / (cClose[-1] / 100)
	angle = float('{:.2f}'.format(angle))
	
	# ANGLE COEFFICIENT
	angle_coeficient: float
	
	if atr_per != 0:
		angle_coeficient = angle / atr_per
	else:
		angle_coeficient = angle / 1

	angle_coeficient = float('{:.2f}'.format(angle_coeficient))
	
	# RESULT. Варіант з опорою на мінімальний cloud, на ПРОДОВЖЕННЯ руху
	# if rising_dragon and cloud_above == 0 and fresh_below:
	# 	if ema34_high[-1] >= cLow[-1] >= ema89[-1]:
	# 		return ['🟢', atr_per, angle_coeficient]
	# 	return ['↗️', atr_per, angle_coeficient]
	#
	# elif falling_dragon and cloud_below == 0 and fresh_above:
	# 	if ema34_low[-1] <= cHigh[-1] <= ema89[-1]:
	# 		return ['🔴', atr_per, angle_coeficient]
	# 	return ['↘️', atr_per, angle_coeficient]
	#
	# else:
	# 	return ['Sleep', atr_per, angle_coeficient]
	
	# RESULT. Варіант з первинним відходом від dragon, одразу ж після перетину
	if rising_dragon and fresh_below and cLow[-1] >= ema34_high[-1]:
		return ['↗️', atr_per, angle_coeficient]
	
	elif falling_dragon and fresh_above and cHigh[-1] <= ema34_low[-1]:
		return ['↘️', atr_per, angle_coeficient]
	
	else:
		return ['Sleep', atr_per, angle_coeficient]