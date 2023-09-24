import _thread
from time import sleep
import websocket
import json
import threading


class SocketConnectionBybit(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)

        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print("Error", e)
        self.on_close = lambda ws: print("Closing")
        self.run_forever()
    
    def on_open(self, ws):
        print("WebSocket was opened")
        
        def run(*args):
            tradeStr = {"op": "subscribe", "args": "orderbook.1.TRBUSDT"}
            ws.send(json.dumps(tradeStr))
        
        _thread.start_new_thread(run, ())
        
    def message(self, msg):
        msg = json.loads(msg)
        msg = msg.get("data")
        
        symb = msg.get("s")
        bids = msg.get("b")
        asks = msg.get("a")
        
        bids = 0 if not bids else bids[0]
        asks = 0 if not asks else asks[0]
        
        the_price = asks if bids == 0 else bids
        self.sv2.put(the_price[0])
        # print(f"Байбіт прайс: {the_price[0]}")
    
bybit_symbol = "orderbook.1.TRBUSDT"
bybit_url = 'wss://stream.bybit.com/v5/public/linear'
#
# # while True:
tr1 = threading.Thread(target=SocketConnectionBybit(bybit_url))

tr1.start()

# Wait for the_price to be updated
# the_p.price_ready_event.wait()

# Access the updated the_price
# while True:
#     print(the_p.the_price)