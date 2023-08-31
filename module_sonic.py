import talipp.indicators.EMA


def sonic_signal(cHigh, cLow, cClose, cloud_filter):

	# INDICATORS
	ema34_basis = talipp.indicators.EMA(period=34, input_values=cClose)
	ema34_low = talipp.indicators.EMA(period=34, input_values=cLow)
	ema34_high = talipp.indicators.EMA(period=34, input_values=cHigh)
	ema89 = talipp.indicators.EMA(period=89, input_values=cClose)
	ema233 = talipp.indicators.EMA(period=233, input_values=cClose)
	
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
			
	# AVERAGE ATR
	atr = (sum(sum([cHigh[-1:-37:-1] - cLow[-1:-37:-1]])) / len(cClose[-1:-37:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
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
	
	first_point = 3 # МІНІМУМ 3
	search_range = 48
	distance_between = 5 # МІНІМУМ 5
	
	farer_high = 0
	closer_high = 0
	
	for i in range(first_point, search_range+1):
		if cHigh[-i] >= max(cHigh[-1:-i-3:-1]): # cHigh[-i-2] <= cHigh[-i-1] <= cHigh[-i] >= cHigh[-i+1] >= cHigh[-i+2]:
			for b in range(i+distance_between, search_range+1):
				if cHigh[-b] >= max(cHigh[-1:-b-3:-1]): # cHigh[-b-2] <= cHigh[-b-1] <= cHigh[-b] >= cHigh[-b+1] >= cHigh[-b+2]:
					if cHigh[-b] >= cHigh[-i]:
					
						falling_coefficient = (cHigh[-b] - cHigh[-i]) / (b - i)
						
						clean_high = True
						
						for g in range(1, b):
							if cHigh[-g] > cHigh[-b] - (b - g) * falling_coefficient:
								clean_high = False
								break
								
						if clean_high == True:
							farer_high = cHigh[-b]
							closer_high = cHigh[-i]
						
	
	farer_low = 0
	closer_low = 0
	
	for i in range(first_point, search_range+1):
		if cLow[-i] <= min(cLow[-1:-i-3:-1]): #cLow[-i-2] >= cLow[-i-1] >= cLow[-i] <= cLow[-i+1] <= cLow[-i+2]:
			for b in range(i+distance_between, search_range+1):
				if cLow[-b] <= min(cLow[-1:-b-3:-1]): # cLow[-b-2] >= cLow[-b-1] >= cLow[-b] <= cLow[-b+1] <= cLow[-b+2]:
					if cLow[-b] <= cLow[-i]:
					
						rising_coefficient = (cLow[-i] - cLow[-b]) / (b - i)
						
						clean_low = True
						
						for g in range(1, b):
							if cLow[-g] < cLow[-b] + (b - g) * rising_coefficient:
								clean_low = False
						
						if clean_low == True:
							farer_low = cLow[-b]
							closer_low = cLow[-i]


	flag = closer_low != 0 and \
			closer_high != 0 and \
			farer_low != 0 and \
			farer_high != 0
			# farer_low <= closer_low <= cLow[-1] and farer_high >= closer_high >= cHigh[-1]
	
	dit_to_low = 0
	
	if farer_low != 0 and cClose[-1] != 0 and atr_per != 0:
		dist_in_perc = (cClose[-1] - farer_low) / (cClose[-1] / 100)
		dit_to_low = dist_in_perc / atr_per
	
	dit_to_high = 0
	
	if farer_high != 0 and cClose[-1] != 0 and atr_per != 0:
		dist_in_perc = (farer_high - cClose[-1]) / (cClose[-1] / 100)
		dit_to_high = dist_in_perc / atr_per
		
	
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
	#z
	# else:
	# 	return ['Sleep', atr_per, angle_coeficient]
	
	
	# RESULT. Варіант з первинним відходом від dragon, одразу ж після перетину
	
	if rising_dragon and farer_high != 0 and cLow[-1] >= ema34_high[-1]:
		return ['🟢', atr_per, f"{int(dit_to_high)} atr's, f:{farer_high}, c:{closer_high}"]
	
	elif falling_dragon and  farer_low != 0 and cHigh[-1] <= ema34_low[-1]:
		return ['🔴', atr_per, f"{int(dit_to_high)} atr's, f:{farer_low}, c:{closer_low}"]
		
	elif cloud_above == 0 or cloud_below == 0:
		return ['☁️', atr_per, "Cloud"]
		
	elif flag:
		return ['🚩', atr_per, f"fl:{farer_low}, cl:{closer_low}, fh:{farer_high}, ch:{closer_high}"]
		
	else:
		return ['Sleep', atr_per, f'far_low {farer_low} close_low {closer_low} far_high {farer_high} close_high {closer_high}']
	