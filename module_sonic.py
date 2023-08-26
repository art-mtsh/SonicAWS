import talipp.indicators.EMA as ema


def sonic_signal(cHigh, cLow, cClose, cloud_filter):

	ema34_basis = ema(period=34, input_values=cClose)
	ema34_low = ema(period=34, input_values=cLow)
	ema34_high = ema(period=34, input_values=cHigh)
	ema89 = ema(period=89, input_values=cClose)
	ema233 = ema(period=233, input_values=cClose)
	
	rising_dragon = ema34_low[-1] > ema89[-1] > ema233[-1]
	falling_dragon = ema34_high[-1] < ema89[-1] < ema233[-1]
	
	dragon_distance_k: float
	if ema34_high[-1] != ema34_low[-1]:
		dragon_distance_k = abs(ema34_basis[-1] - ema89[-1]) / (ema34_high[-1] - ema34_low[-1])
	else:
		dragon_distance_k = 0
	
	cloud_above = 0
	cloud_below = 0
	
	for i in range(2, cloud_filter+2):
		if cLow[-i] < ema34_high[-i] or ema34_low[-i] < ema89[-i] or ema89[-i] < ema233[-i]:
			cloud_above += 1
			
	for i in range(2, cloud_filter+2):
		if cHigh[-i] > ema34_low[-i] or ema34_high[-i] > ema89[-i] or ema89[-i] > ema233[-1]:
			cloud_below += 1
			
			
	angle = abs(ema34_basis[-1] - ema34_basis[-25]) / (cClose[-1] / 100)
	angle = float('{:.1f}'.format(angle))
	
	
	if dragon_distance_k > 1:
		if rising_dragon and cloud_above == 0:
			if ema34_high[-1] >= cLow[-1] >= ema89[-1]:
				return ['🟢', angle]
			return ['↗️', angle]
		elif falling_dragon and cloud_below == 0:
			if ema34_low[-1] <= cHigh[-1] <= ema89[-1]:
				return ['🔴', angle]
			return ['↘️', angle]
		else:
			return ['Sleep', angle]
	else:
		return ['Sleep', angle]
