import websocket
import json

sym = "TRBUSDT"
def on_message_binance(ws, message):
	data = json.loads(message)
	# print(data)
	asks = data.get('a')[0][0]
	bids = data.get('b')[0][0]

def on_error(ws, error):
	print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
	print("WebSocket Closed")
	
def on_open(ws):
	print("Binance WebSocket Opened")


if __name__ == "__main__":
	url_binance = f"wss://fstream.binance.com/ws/{sym.lower()}@depth5@100ms"
	
	ws_binance = websocket.WebSocketApp(url_binance, on_message=on_message_binance, on_error=on_error, on_close=on_close)
	ws_binance.on_open = on_open
	ws_binance.run_forever()
