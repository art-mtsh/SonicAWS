import talipp.indicators.EMA


def sonic_signal(cHigh, cLow, cClose, cloud_filter, first_point, second_point):

	# INDICATORS
	ema34_basis = talipp.indicators.EMA(period=34, input_values=cClose)
	ema34_low = talipp.indicators.EMA(period=34, input_values=cLow)
	ema34_high = talipp.indicators.EMA(period=34, input_values=cHigh)
	ema89 = talipp.indicators.EMA(period=89, input_values=cClose)
	ema233 = talipp.indicators.EMA(period=233, input_values=cClose)
	
	# AVERAGE ATR
	atr = (sum(sum([cHigh[-1:-37:-1] - cLow[-1:-37:-1]])) / len(cClose[-1:-37:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	# TREND
	rising_dragon = ema34_low[-1] >= ema89[-1] >= ema233[-1]
	falling_dragon = ema34_high[-1] <= ema89[-1] <= ema233[-1]
	
	# CLOUDS
	cloud_above = 0
	cloud_below = 0

	for i in range(1, cloud_filter+1):
		if cLow[-i] < ema34_high[-i] or ema34_low[-i] < ema89[-i] or ema89[-i] < ema233[-i]:
			cloud_above += 1

		if cHigh[-i] > ema34_low[-i] or ema34_high[-i] > ema89[-i] or ema89[-i] > ema233[-1]:
			cloud_below += 1
	
	# FRESH
	# fresh_above = False
	# fresh_below = False
	#
	# for i in range(2, cloud_filter*2 + 2):
	# 	if ema34_high[-i] >= ema89[-i]:
	# 		fresh_above = True
	#
	# 	if ema34_low[-i] <= ema89[-i]:
	# 		fresh_below = True

	
	# ANGLE COEFFICIENT
	# angle = abs(ema34_basis[-1] - ema34_basis[-cloud_filter*2-1]) / (cClose[-1] / 100)
	# angle = float('{:.2f}'.format(angle))
	#
	# angle_coeficient: float
	#
	# if atr_per != 0:
	# 	angle_coeficient = angle / atr_per
	# else:
	# 	angle_coeficient = angle / 1
	#
	# angle_coeficient = float('{:.2f}'.format(angle_coeficient))
	
	# FLAG
	
	search_range = 36
	
	farer_high = 0
	closer_high = 0
	farer_high_index = 0
	
	for i in range(first_point, search_range+1):
		if cHigh[-i] >= max(cHigh[-1:-i-3:-1]): # cHigh[-i-2] <= cHigh[-i-1] <= cHigh[-i] >= cHigh[-i+1] >= cHigh[-i+2]:
			for b in range(i + second_point, search_range + 1):
				if cHigh[-b] >= max(cHigh[-1:-b-3:-1]): # cHigh[-b-2] <= cHigh[-b-1] <= cHigh[-b] >= cHigh[-b+1] >= cHigh[-b+2]:
					if cHigh[-b] >= cHigh[-i]:
					
						falling_coefficient = (cHigh[-b] - cHigh[-i]) / (b - i)
						clean_high = True
						
						for g in range(1, b):
							if cHigh[-g] > cHigh[-b] - (b - g) * falling_coefficient:
								clean_high = False
								break
						
						if clean_high:
							farer_high = cHigh[-b]
							closer_high = cHigh[-i]
							farer_high_index = b
	
	farer_low = 0
	closer_low = 0
	farer_low_index = 0
	
	for i in range(first_point, search_range+1):
		if cLow[-i] <= min(cLow[-1:-i-3:-1]): #cLow[-i-2] >= cLow[-i-1] >= cLow[-i] <= cLow[-i+1] <= cLow[-i+2]:
			for b in range(i + second_point, search_range + 1):
				if cLow[-b] <= min(cLow[-1:-b-3:-1]): # cLow[-b-2] >= cLow[-b-1] >= cLow[-b] <= cLow[-b+1] <= cLow[-b+2]:
					if cLow[-b] <= cLow[-i]:
					
						rising_coefficient = (cLow[-i] - cLow[-b]) / (b - i)
						clean_low = True
						
						for g in range(1, b):
							if cLow[-g] < cLow[-b] + (b - g) * rising_coefficient:
								clean_low = False
								break
						
						if clean_low:
							farer_low = cLow[-b]
							closer_low = cLow[-i]
							farer_low_index = b

	# flag = closer_low != 0 and \
	# 		closer_high != 0 and \
	# 		farer_low != 0 and \
	# 		farer_high != 0
	# 		# farer_low <= closer_low <= cLow[-1] and farer_high >= closer_high >= cHigh[-1]
	
	# RESULT
	
	
	high_to_fh = (farer_high - cHigh[-1]) / (cClose[-1] / 100)
	high_to_ch = (closer_high - cHigh[-1]) / (cClose[-1] / 100)
	
	low_to_fl = (cLow[-1] - farer_low) / (cClose[-1] / 100)
	low_to_cl = (cLow[-1] - closer_low) / (cClose[-1] / 100)
	
	high_to_fh = float('{:.2f}'.format(high_to_fh))
	high_to_ch = float('{:.2f}'.format(high_to_ch))
	
	low_to_fl = float('{:.2f}'.format(low_to_fl))
	low_to_cl = float('{:.2f}'.format(low_to_cl))
	
	close_to_dragon = abs(cClose[-1] - ema34_basis[-1]) / (cClose[-1] / 100)
	close_to_dragon = float('{:.2f}'.format(close_to_dragon))
	
	if rising_dragon and farer_low != 0 and farer_high != 0 and farer_low >= ema34_high[-farer_low_index]:
		return ['🟢', atr_per, f'far_low {farer_low} close_low {closer_low} far_high {farer_high} close_high {closer_high}']
	
	elif falling_dragon and farer_low != 0 and farer_high != 0 and farer_high <= ema34_low[-farer_high_index]:
		return ['🔴', atr_per, f'far_low {farer_low} close_low {closer_low} far_high {farer_high} close_high {closer_high}']
		
	elif cloud_above == 0 or cloud_below == 0:
		return ['☁️', atr_per, f'{close_to_dragon}% t/dragon']
		
	# elif flag:
	# 	return ['🚩', atr_per, f"fl:{farer_low}, cl:{closer_low}, fh:{farer_high}, ch:{closer_high}"]
		
	else:
		return ['Sleep', atr_per, f'far_low {farer_low} close_low {closer_low} far_high {farer_high} close_high {closer_high}']
	