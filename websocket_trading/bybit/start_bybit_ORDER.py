import websocket
import json
import time
from websocket_trading import keys
from pybit.unified_trading import HTTP

api_key = keys.BYBIT_API_V2
api_secret = keys.BYBIT_SECRET_V2

bybit_session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret,
)

sym = "BLZUSDT"

sent_positions = {}

def on_message_bybit(ws, message):
	data = json.loads(message)
	data = data.get('data')
	symbol = data.get('s')
	bids = data.get('b')[0][0] if len(data.get('b')) > 0 else 0
	asks = data.get('a')[0][0] if len(data.get('a')) > 0 else 0
	
	print(f"Bybit ask {asks}, bid {bids}")
	
	quantity = 28
	
	if float(asks) > 0.10:
		print("=========== OPENING ORDER =============")
		if float(asks) > 0.182 and f"Bybit-{sym}-BUY" not in sent_positions.keys():
			
			response = bybit_session.place_order(
			    category="linear",
			    symbol=sym,
			    side="Buy",
			    orderType="Market",
			    qty=str(quantity),
			    timeInForce="PostOnly",
			    orderLinkId=str(time.time()),
			)
			
			sent_positions.update({f"Bybit-{sym}-BUY": "orderID"})
			
			print("Market Order Response:", response)
			print(f"Current sent dict: {sent_positions}")
			
		elif float(asks) <= 0.180 and f"Bybit-{sym}-SELL" not in sent_positions.keys():
		
			response = bybit_session.place_order(
			    category="linear",
			    symbol=sym,
			    side="Sell",
			    orderType="Market",
			    qty=str(quantity),
			    timeInForce="PostOnly",
			    orderLinkId=str(time.time()),
			)
			
			sent_positions.update({f"Bybit-{sym}-SELL": "orderID"})
			
			print("Market Order Response:", response)
			print(f"Current sent dict: {sent_positions}")
		
		print("=========== order opened, sleep =============")
		print("")
	time.sleep(10)
	
	
	
	data = bybit_session.get_positions(
		category="linear",
		symbol=sym,
	)
	
	result = data.get("result")
	bybit_positions = result.get("list")
	
	print("=========== CHECKING POSITIONS =============")
	print(bybit_positions)
	print("")
	
	for i in bybit_positions:
		print(f"Taken this position\n"
		      f"{i}\n")
		
		if i.get("symbol") == sym:
			quantity = i.get("size")
			
			if sent_positions.get(f"Bybit-{sym}-BUY") is not None:
				
				response = bybit_session.place_order(
					category="linear",
					symbol=sym,
					side="Sell",
					orderType="Market",
					qty=str(quantity),
					timeInForce="PostOnly",
					orderLinkId=str(time.time()),
				)
				sent_positions.pop(f"Bybit-{sym}-BUY")
				
				print("Market Order Response:", response)
				print(f"Current sent dict: {sent_positions}")
				
				
			elif sent_positions.get(f"Binance-{sym}-SELL") is not None:
				
				response = bybit_session.place_order(
			    category="linear",
			    symbol=sym,
			    side="Buy",
			    orderType="Market",
			    qty=str(quantity),
			    timeInForce="PostOnly",
			    orderLinkId=str(time.time()),
			)
				sent_positions.pop(f"Binance-{sym}-SELL")
				
				print("Market Order Response:", response)
				print(f"Current sent dict: {sent_positions}")

def on_error(ws, error):
	print("WebSocket Error:", error)


def on_close(ws, close_status_code, close_msg):
	print(f"WebSocket connection closed with code {close_status_code}")


def on_open_bybit(ws):
	print("Bybit WebSocket Opened")
	# Subscribe to the order book for a specific trading pair
	subscribe_message = {
		"req_id": "test9292929",
		"op": "subscribe",
		"args": [f"orderbook.1.{sym}"]
	}
	ws.send(json.dumps(subscribe_message))


if __name__ == "__main__":
	url_bybit = "wss://stream.bybit.com/v5/public/linear"
	
	ws_bybit = websocket.WebSocketApp(url_bybit, on_message=on_message_bybit, on_error=on_error, on_close=on_close)
	ws_bybit.on_open = on_open_bybit  # Add an on_open callback
	ws_bybit.run_forever()
