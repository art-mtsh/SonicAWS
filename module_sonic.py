import talipp.indicators.EMA
import pandas as pd
from requests import get


dragon_length = 34
trend_length = 89
supertrend_length = 233

atr_length = 24

flag_search_range = 24

brratio_lengh = 36
brratio_filter = 40


def sonic_signal(cOpen, cHigh, cLow, cClose, cloud_filter, first_point, second_point):

	# INDICATORS
	ema34_basis = talipp.indicators.EMA(period=dragon_length, input_values=cClose)
	ema34_low = talipp.indicators.EMA(period=dragon_length, input_values=cLow)
	ema34_high = talipp.indicators.EMA(period=dragon_length, input_values=cHigh)
	ema89 = talipp.indicators.EMA(period=trend_length, input_values=cClose)
	ema233 = talipp.indicators.EMA(period=supertrend_length, input_values=cClose)
	
	# AVERAGE ATR

	atr = (sum(sum([cHigh[-1:-atr_length-1:-1] - cLow[-1:-atr_length-1:-1]])) / len(cClose[-1:-atr_length-1:-1]))
	atr_per = atr / (cClose[-1] / 100)
	atr_per = float('{:.2f}'.format(atr_per))
	
	# TREND
	rising_dragon = ema34_low[-1] >= ema89[-1] >= ema233[-1]
	falling_dragon = ema34_high[-1] <= ema89[-1] <= ema233[-1]
	
	# CLOUDS
	# cloud_above = 0
	# cloud_below = 0
	#
	# for i in range(1, cloud_filter+1):
	# 	if cLow[-i] < ema34_high[-i] or ema34_low[-i] < ema89[-i] or ema89[-i] < ema233[-i]:
	# 		cloud_above += 1
	#
	# 	if cHigh[-i] > ema34_low[-i] or ema34_high[-i] > ema89[-i] or ema89[-i] > ema233[-1]:
	# 		cloud_below += 1
	
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
	
	farer_high = 0
	closer_high = 0
	farer_high_index = 0
	closer_high_index = 0
	
	for i in range(first_point, flag_search_range+1):
		if cHigh[-i] >= max(cHigh[-1:-i-4:-1]): # cHigh[-i-2] <= cHigh[-i-1] <= cHigh[-i] >= cHigh[-i+1] >= cHigh[-i+2]:
			for b in range(i + second_point, flag_search_range + 1):
				if cHigh[-b] >= max(cHigh[-1:-b-4:-1]): # cHigh[-b-2] <= cHigh[-b-1] <= cHigh[-b] >= cHigh[-b+1] >= cHigh[-b+2]:
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
							closer_high_index = i
	
	farer_low = 0
	closer_low = 0
	farer_low_index = 0
	closer_low_index = 0
	
	for i in range(first_point, flag_search_range+1):
		if cLow[-i] <= min(cLow[-1:-i-4:-1]): #cLow[-i-2] >= cLow[-i-1] >= cLow[-i] <= cLow[-i+1] <= cLow[-i+2]:
			for b in range(i + second_point, flag_search_range + 1):
				if cLow[-b] <= min(cLow[-1:-b-4:-1]): # cLow[-b-2] >= cLow[-b-1] >= cLow[-b] <= cLow[-b+1] <= cLow[-b+2]:
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
							closer_low_index = i
	
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
	
	# BODY/RANGE RATIO
	br_ratio = 0
	
	if farer_high != 0 or farer_low != 0:
		br_ratios = []
		for i in range(1, brratio_lengh):
			body = abs(cOpen[-i] - cClose[-i])
			candle_range = (cHigh[-i] - cLow[-i])
			one_percent = candle_range / 100
			
			if body != 0 and one_percent != 0:
				ratio = body / one_percent
				br_ratios.append(ratio)
				
		if len(br_ratios) != 0:
			br_ratio = int(sum(br_ratios) / len(br_ratios))
		
	# RESULT
	
	if rising_dragon:
		if closer_high != 0:
			if closer_low != 0:
				if closer_low >= ema34_high[-closer_low_index]:
					return ['✅✅✅', atr_per, f'BR: {br_ratio}%']
				return ['✅✅⬜️', atr_per, f'BR: {br_ratio}%']
			return ['✅⬜️⬜️', atr_per, f'BR: {br_ratio}%']
		else:
			return ['Sleep', atr_per, f'\n fl:{farer_low}, \n cl:{closer_low}, \n fh:{farer_high}, \n ch:{closer_high}']
			
	elif falling_dragon:
		if closer_low != 0:
			if closer_high != 0:
				if closer_high <= ema34_low[-closer_high_index]:
					return ['✅✅✅', atr_per, f'BR: {br_ratio}%']
				return ['✅✅⬜️', atr_per, f'BR: {br_ratio}%']
			return ['✅⬜️⬜️', atr_per, f'BR: {br_ratio}%']
		else:
			return ['Sleep', atr_per, f'\n fl:{farer_low}, \n cl:{closer_low}, \n fh:{farer_high}, \n ch:{closer_high}']
		
	elif closer_low != 0 and closer_high != 0:
		return ['🚩', atr_per, f'BR: {br_ratio}%']
	
	# elif cloud_above == 0 or cloud_below == 0:
	
	else:
		return ['Sleep', atr_per, f'\n fl:{farer_low}, \n cl:{closer_low}, \n fh:{farer_high}, \n ch:{closer_high}']
		
# url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + 'TOMOUSDT' + '&interval=' + '5m' + '&limit=300'
# data1 = get(url_klines).json()
#
# d1 = pd.DataFrame(data1)
# d1.columns = [
# 'open_time',
# 'cOpen',
# 'cHigh',
# 'cLow',
# 'cClose',
# 'cVolume',
# 'close_time',
# 'qav',
# 'num_trades',
# 'taker_base_vol',
# 'taker_quote_vol',
# 'is_best_match'
# ]
# df1 = d1
#
# df1['cOpen'] = df1['cOpen'].astype(float)
# df1['cHigh'] = df1['cHigh'].astype(float)
# df1['cLow'] = df1['cLow'].astype(float)
# df1['cClose'] = df1['cClose'].astype(float)
#
# cOpen = df1['cOpen'].to_numpy()
# cHigh = df1['cHigh'].to_numpy()
# cLow = df1['cLow'].to_numpy()
# cClose = df1['cClose'].to_numpy()
#
# print(sonic_signal(cOpen, cHigh, cLow, cClose, 12, 3, 6))