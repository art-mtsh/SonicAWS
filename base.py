import pandas as pd
from requests import get
from multiprocessing import Process
import telebot
import time
import datetime
from module_sonic import sonic_signal
from module_get_pairs import get_pairs

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

timeinterval = '5m'


def calculation(instr, atr_filter, cloud_filter):

	for symbol in instr:
		# try:
		# --- DATA ---
		url_klines = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + timeinterval + '&limit=500'
		data1 = get(url_klines).json()
		
		d1 = pd.DataFrame(data1)
		d1.columns = [
			'open_time',
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
			'is_best_match'
		]
		df1 = d1
		df1['cOpen'] = df1['cOpen'].astype(float)
		df1['cHigh'] = df1['cHigh'].astype(float)
		df1['cLow'] = df1['cLow'].astype(float)
		df1['cClose'] = df1['cClose'].astype(float)
		
		cOpen = df1['cOpen'].to_numpy()
		cHigh = df1['cHigh'].to_numpy()
		cLow = df1['cLow'].to_numpy()
		cClose = df1['cClose'].to_numpy()
		
		sonic = sonic_signal(cHigh=cHigh, cLow=cLow, cClose=cClose, cloud_filter=cloud_filter)
		
		if sonic[1] >= atr_filter: #and avgvolume_60 >= volume_filter
			if 'Sleep' not in sonic[0] and '🟢' not in sonic[0] and '🔴' not in sonic[0]:
				print(f"{sonic[0]} {symbol}, ATR: {sonic[1]}%, {sonic[2]};")
				bot1.send_message(662482931, f'{sonic[0]} {symbol}, ATR: {sonic[1]}%, {sonic[2]}')
			
			elif '🟢' in sonic[0] or '🔴' in sonic[0]:
				print(f"---------------------> {symbol};")
				bot3.send_message(662482931, f'{sonic[0]}{symbol}, ATR: {sonic[1]}%, {sonic[2]}')
					
		# except telebot.apihelper.ApiTelegramException as ex:
		# 	print(f'Telegram error for {symbol}: {ex}')
		# 	bot2.send_message(662482931, f'Telegram error for {symbol}: {ex}')
		#
		# except Exception as exy:
		# 	print(f'Error main module for {symbol}: {exy}')
		# 	bot2.send_message(662482931, f'Error main module for {symbol}: {exy}')

def search_activale(price_filter, ticksize_filter, volume_filter, atr_filter, cloud_filter):
	time1 = time.perf_counter()
	print(f"Starting processes at {datetime.datetime.now().strftime('%H:%M:%S')}")
	instr = get_pairs(price_filter, ticksize_filter, num_chunks=8)
	total_count = sum(len(sublist) for sublist in instr)
	bot1.send_message(662482931, f'️️{total_count} coins {timeinterval}: <${price_filter}, <{ticksize_filter}%, >{atr_filter}%, >{cloud_filter} cds')
	# bot3.send_message(662482931, '.')
	print(f"{total_count} coins {timeinterval}: Price <= ${price_filter}, Tick <= {ticksize_filter}%, avg.ATR >= {atr_filter}%, Cloud >= {cloud_filter} candles")
	
	p1 = Process(target=calculation, args=(instr[0], atr_filter, cloud_filter,))
	p2 = Process(target=calculation, args=(instr[1], atr_filter, cloud_filter,))
	p3 = Process(target=calculation, args=(instr[2], atr_filter, cloud_filter,))
	p4 = Process(target=calculation, args=(instr[3], atr_filter, cloud_filter,))
	p5 = Process(target=calculation, args=(instr[4], atr_filter, cloud_filter,))
	p6 = Process(target=calculation, args=(instr[5], atr_filter, cloud_filter,))
	p7 = Process(target=calculation, args=(instr[6], atr_filter, cloud_filter,))
	p8 = Process(target=calculation, args=(instr[7], atr_filter, cloud_filter,))
	# p9 = Process(target=calculation, args=(instr[8], volume_filter, atr_filter, cloud_filter,))
	# p10 = Process(target=calculation, args=(instr[9], volume_filter, atr_filter, cloud_filter,))
	# p11 = Process(target=calculation, args=(instr[10], volume_filter, atr_filter, cloud_filter,))
	# p12 = Process(target=calculation, args=(instr[11], volume_filter, atr_filter, cloud_filter,))
	# p13 = Process(target=calculation, args=(instr[12], volume_filter, atr_filter, cloud_filter,))
	# p14 = Process(target=calculation, args=(instr[13], volume_filter, atr_filter, cloud_filter,))
	# p15 = Process(target=calculation, args=(instr[14], volume_filter, atr_filter, cloud_filter,))
	# p16 = Process(target=calculation, args=(instr[15], volume_filter, atr_filter, cloud_filter,))
	
	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()
	p6.start()
	p7.start()
	p8.start()
	# p9.start()
	# p10.start()
	# p11.start()
	# p12.start()
	# p13.start()
	# p14.start()
	# p15.start()
	# p16.start()

	
	p1.join()
	p2.join()
	p3.join()
	p4.join()
	p5.join()
	p6.join()
	p7.join()
	p8.join()
	# p9.join()
	# p10.join()
	# p11.join()
	# p12.join()
	# p13.join()
	# p14.join()
	# p15.join()
	# p16.join()


	p1.close()
	p2.close()
	p3.close()
	p4.close()
	p5.close()
	p6.close()
	p7.close()
	p8.close()
	# p9.close()
	# p10.close()
	# p11.close()
	# p12.close()
	# p13.close()
	# p14.close()
	# p15.close()
	# p16.close()
	
	
	time2 = time.perf_counter()
	time3 = time2 - time1
	bot1.send_message(662482931, f'🍌 {int(time3)} seconds 🍌')
	print(f"Finished processes in {int(time3)} seconds, at {datetime.datetime.now().strftime('%H:%M:%S')}\n")

def waiting():
	while True:
		now = datetime.datetime.now()
		last_hour_digit = int(now.strftime('%H'))
		last_minute_digit = int(now.strftime('%M')[-1])
		last_second_digit = int(now.strftime('%S'))
		if last_hour_digit in list(range(8, 23)):
			if last_minute_digit == 4 or last_minute_digit == 9:
				if last_second_digit == 25:
					break
		time.sleep(0.1)

if __name__ == '__main__':
	
	price_filter = 3000 #int(input('Pice less than: '))
	ticksize_filter = 0.025 #float(input('Ticksize less than: '))
	volume_filter = 1 #int(input('Volume more than: '))
	atr_filter = 0.2 #float(input('ATR more than: '))
	cloud_filter = 10 #int(input('Cloud length: '))
	
	while True:
		search_activale(
		    price_filter=price_filter,
		    ticksize_filter=ticksize_filter,
		    volume_filter=volume_filter,
		    atr_filter=atr_filter,
			cloud_filter=cloud_filter
		)
		time.sleep(60)
		waiting()