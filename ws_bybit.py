import _thread
import websocket
import threading
import json

class SocketConnectionBybit(websocket.WebSocketApp):
    def __init__(self, url, params=[], shared_val_1=None):
        super().__init__(url=url, on_open=self.on_open)

        self.params = params
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print("Error", e)
        self.on_close = lambda ws: print("Closing")

        self.run_forever()

    def on_open(self, ws):
        print("WebSocket was opened")

        def run(*args):
            tradeStr = {"op": "subscribe", "args": self.params}
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
        
        if self.shared_val_1 is not None:
            with self.shared_val_1.get_lock():
                self.shared_val_1.value = the_price[0]
                
        print(f'{symb}: the price {the_price[0]}, size {the_price[1]}')


# bybit_symbol = "orderbook.1.TRBUSDT"
# bybit_url = f'wss://stream.bybit.com/v5/public/linear'
#
# tr1 = threading.Thread(target=SocketConnectionBybit, args=(bybit_url, [bybit_symbol]))
# tr1.start()
