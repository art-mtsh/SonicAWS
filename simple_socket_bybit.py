from pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket
import keys
from time import sleep
import json

"""
https://dev.to/kylefoo/pybit-v5-how-to-subscribe-to-websocket-topics-1iem
"""

api_key = keys.BYBIT_API
api_secret = keys.BYBIT_SECRET


bybit_ws = WebSocket(testnet=False, channel_type="linear",)
def handle_message(msg):
   
    symb = msg.get("data").get("s")
    bids = msg.get("data").get("b")[0]
    asks = msg.get("data").get("a")[0]

    print(f"{symb}: {bids[0]}, {asks[0]}")

    
bybit_ws.orderbook_stream(
    depth=1,
    symbol="TRBUSDT",
    callback=handle_message
)
while True:
    sleep(1)