import keys
import telebot
from binance import ThreadedWebsocketManager
from time import sleep
from pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket

api_key = keys.BINANCE_API
api_secret = keys.BINANCE_SECRET

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

def main():
	
	binance_mark_bid = 0
	binance_mark_ask = 0

	bybit_mark_bid = 0
	bybit_mark_ask = 0
	def bin_socket_message(msg):
		nonlocal binance_mark_bid  # Use nonlocal to update the outer variable
		nonlocal binance_mark_ask  # Use nonlocal to update the outer variable
		
		symb = msg.get("data").get("s")
		bids = msg.get("data").get("b")[0]
		asks = msg.get("data").get("a")[0]
		
		binance_mark_bid = float(bids[0])  # Update the bid price
		binance_mark_ask = float(asks[0])  # Update the bid price
	
	def bit_socket_message(msg):
		nonlocal bybit_mark_bid  # Use nonlocal to update the outer variable
		nonlocal bybit_mark_ask  # Use nonlocal to update the outer variable
		
		symb = msg.get("data").get("s")
		bids = msg.get("data").get("b")[0]
		asks = msg.get("data").get("a")[0]
		
		bybit_mark_bid = float(bids[0])  # Update the bid price
		bybit_mark_ask = float(asks[0])
		

	binance_ws.start_futures_depth_socket(callback=bin_socket_message, symbol=symbol, depth=5)
	bybit_ws.orderbook_stream(depth=1, symbol=symbol, callback=bit_socket_message)
	
	sleep(3)
	
	while True:

		binance_higher = (binance_mark_bid - bybit_mark_ask) / (bybit_mark_ask / 100)
		binance_higher = float('{:.2f}'.format(binance_higher))
		bybit_higher = (bybit_mark_bid - binance_mark_ask) / (binance_mark_ask / 100)
		bybit_higher = float('{:.2f}'.format(bybit_higher))
		
		print(f"Binance {binance_mark_ask}/{binance_mark_bid}, bybit {bybit_mark_ask}/{bybit_mark_bid}. Difference: {binance_higher}%/{bybit_higher}%")
		if binance_higher >= 0.3 or bybit_higher >= 0.3:
			bot3.send_message(662482931, f"Binance {binance_mark_ask}/{binance_mark_bid}, bybit {bybit_mark_ask}/{bybit_mark_bid}. Difference: {binance_higher}%/{bybit_higher}%")
			sleep(600)
			
if __name__ == "__main__":
	main()