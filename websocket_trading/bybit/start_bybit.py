import websocket
import json

sym = "TRBUSDT"

def on_message_bybit(ws, message):
	data = json.loads(message)
	# print(data)
	data = data.get('data')
	symbol = data.get('s')
	bids = data.get('b')[0][0] if len(data.get('b')) > 0 else 0
	asks = data.get('a')[0][0] if len(data.get('a')) > 0 else 0

	print(f"Bybit ask {asks}, bid {bids}")


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
	