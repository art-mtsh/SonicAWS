import pandas as pd
from requests import get
from typing import List
import talipp



# --- FUNCTION ---
def screensaver(symbol: str, timeinterval: str) -> List:
	
	req_len = 800
	# --- DATA ---
	url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + timeinterval + f'&limit={req_len}'
	data1 = get(url_klines).json()

	# --- K-LINE ---
	D1 = pd.DataFrame(data1)
	D1.columns = ['open_time',
				  'cOpen',
				  'cHigh',
				  'cLow',
				  'cClose',
				  'cVolume',
				  'close_time',
				  'qav',
				  'num_trades',
				  'taker_base_vol',
				  'taker_quote_vol',
				  'is_best_match']
	df1 = D1
	df1['cOpen'] = df1['cOpen'].astype(float)
	df1['cHigh'] = df1['cHigh'].astype(float)
	df1['cLow'] = df1['cLow'].astype(float)
	df1['cClose'] = df1['cClose'].astype(float)
	df1['cVolume'] = df1['cVolume'].astype(float)

	# Lists:
	cOpen = df1['cOpen'].to_numpy()
	cHigh = df1['cHigh'].to_numpy()
	cLow = df1['cLow'].to_numpy()
	cClose = df1['cClose'].to_numpy()
	cVolume = df1['cVolume'].to_numpy()
	atrper = (sum(sum([cHigh - cLow])) / len(cClose)) / (cClose[-1] / 100)
	atrper = float('{:.2f}'.format(atrper))
	
	cOpen = list(cOpen)
	cClose = list(cClose)
	
	atr_num = 10
	
	atr_values = []
	
	for i in range(atr_num, req_len):
		print(cOpen[i])
		
		print(atr_values[i])

	
	
	
screensaver("AAVEUSDT", "5m")
