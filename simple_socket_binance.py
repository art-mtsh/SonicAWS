import time
import keys

from binance import ThreadedWebsocketManager

api_key = keys.BINANCE_API
api_secret = keys.BINANCE_SECRET

def main():

    symbol = 'TRBUSDT'

    binance_ws = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    binance_ws.start()

    def handle_socket_message(msg):
        symb = msg.get("data").get("s")
        bids = msg.get("data").get("b")[0]
        asks = msg.get("data").get("a")[0]
        
        print(f"{symb}: {bids[0]}, {asks[0]}")
        

    binance_ws.start_futures_depth_socket(callback=handle_socket_message, symbol=symbol, depth=5)
    
    """
    https://python-binance.readthedocs.io/en/latest/websockets.html
    
    """

    binance_ws.join()


if __name__ == "__main__":
   main()