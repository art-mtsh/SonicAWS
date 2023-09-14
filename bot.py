# import pandas as pd
# from requests import get
# from multiprocessing import Process, Queue
# import telebot
# import time
# import datetime
# from module_get_pairs import get_pairs
# from module_pinbar import pinbar_analysis
# import talipp.indicators.EMA
# from talipp.ohlcv import OHLCV
# from trade_operations import williams_pr
#
# url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + 'TOMOUSDT' + '&interval=' + '1m' + '&limit=50'
# data1 = get(url_klines).json()
#
# d1 = pd.DataFrame(data1)
# d1.columns = [
# 			'open_time',
# 			'cOpen',
# 			'cHigh',
# 			'cLow',
# 			'cClose',
# 			'cVolume',
# 			'close_time',
# 			'qav',
# 			'num_trades',
# 			'taker_base_vol',
# 			'taker_quote_vol',
# 			'is_best_match'
# 				]
# df1 = d1
#
# df1['cOpen'] = df1['cOpen'].astype(float)
# df1['cHigh'] = df1['cHigh'].astype(float)
# df1['cLow'] = df1['cLow'].astype(float)
# df1['cClose'] = df1['cClose'].astype(float)
# df1['cVolume'] = df1['cVolume'].astype(float)
#
# cOpen = df1['cOpen'].to_numpy()
# cHigh = df1['cHigh'].to_numpy()
# cLow = df1['cLow'].to_numpy()
# cClose = df1['cClose'].to_numpy()
# cVolume = df1['cVolume'].to_numpy()
# #
# # while True:
# # 	print(williams_pr(12, 10, cHigh, cLow, cClose))
# # 	print(cClose[-12])
# # 	time.sleep(1)
#
# # print(len(cHigh[-20:-10 - 20:-1]))

for i in range(9, 22, 12):
	print(i)