import websocket
import threading
import json

class SocketConnectionBinance(websocket.WebSocketApp):
	def __init__(self, url, sv1):
		super().__init__(url=url, on_open=self.on_open)
		
		self.sv1 = sv1
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
		# self.sv1.put(asks_price[0])
		print(f"Бубанс прайс: {asks_price[0]}")

binance_symbol = "trbusdt"
binance_url = f"wss://fstream.binance.com/ws/{binance_symbol}@depth5@100ms"
#
tr1 = threading.Thread(target=SocketConnectionBinance, args=(binance_url, 2))
tr1.start()
