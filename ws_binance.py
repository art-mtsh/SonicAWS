import websocket
import threading
import json

class SocketConnectionBinance(websocket.WebSocketApp):
	def __init__(self, url):
		super().__init__(url=url, on_open=self.on_open, shared_val_2=None)
		
		self.on_message = lambda ws, msg: self.message(msg)
		self.on_error = lambda ws, e: print("Error", e)
		self.on_close = lambda ws: print("Closing")
		
		self.run_forever()
		
	def on_open(self, ws,):
		print("Websocket was opened")
	
	def message(self, msg):
		msg = json.loads(msg)
		bids_price = msg.get("b")[0]
		asks_price = msg.get("a")[0]
		
		if self.shared_val_2 is not None:
			with self.shared_val_2.get_lock():
				self.shared_val_2.value = asks_price[0]

		print(f'{msg.get("s")}: the price {asks_price[0]}, size {asks_price[1]}')

		
# binance_symbol = "trbusdt"
# binance_url = f"wss://fstream.binance.com/ws/{binance_symbol}@depth5@100ms"
#
# tr1 = threading.Thread(target=SocketConnectionBinance, args=(binance_url,))
# tr1.start()
