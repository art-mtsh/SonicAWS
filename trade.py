import threading

from pybit.unified_trading import HTTP
import time
import keys


def bin():

	from rest_arbitrage.binance_order import binance_market_trade
	
	binance_key = keys.BINANCE_API
	binance_secret = keys.BINANCE_SECRET
	
	
	try:
		trade = binance_market_trade("blzusdt", "BUY", 33, binance_key, binance_secret)
	except Exception:
		print(f"Binance ERROR!!!{Exception}")
	else:
		print(trade)
# ===========================================================================================================

def byb():
	current_time = str(int(time.time() * 1000))
	print(current_time)
	
	bybit_key = keys.BYBIT_API
	bybit_secret = keys.BYBIT_SECRET
	
	bybit_session = HTTP(
		testnet=False,
		api_key=bybit_key,
		api_secret=bybit_secret,
	)

	try:
		trade = bybit_session.place_order(
			category="linear",
			symbol="BLZUSDT",
			side="Buy",
			orderType="Market",
			qty="32",
		)
	except Exception:
		print(f"Bybit ERROR!!!{Exception}")
	else:
		print(trade)

# ===========================================================================================================

start_time = time.time()  # Record the start time

binance = threading.Thread(target=byb())
bybit = threading.Thread(target=bin())

binance.start()
bybit.start()

binance.join()
bybit.join()

end_time = time.time()  # Record the end time

# Calculate the response time
response_time = end_time - start_time

# Print the response time
print(f"Done in: {response_time} seconds")