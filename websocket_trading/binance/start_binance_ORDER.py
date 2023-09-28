import websocket
import json
import threading
import time
import keys
from rest_arbitrage.binance_order import binance_market_trade
from binance_account_info import binance_positions

# Binance API Key and Secret
api_key = keys.BINANCE_API
api_secret = keys.BINANCE_SECRET

sym = "BLZUSDT"

sent_positions = {}

def on_message_depth(ws, message):
    global sent_positions
    
    data = json.loads(message)
    asks = float(data.get('a')[0][0])
    bids = float(data.get('b')[0][0])
    
    print(f"{asks}, {bids}")

    quantity = 29

    if asks > 0.10:
        if asks > 0.182 and f"Binance-{sym}-BUY" not in sent_positions.keys():

            response = binance_market_trade(sym.upper(), "BUY", quantity,,
            sent_positions.update({f"Binance-{sym}-BUY" : response.get('orderId')})

            print("Market Order Response:", response)
            print(f"Current sent dict: {sent_positions}")

        elif asks <= 0.182 and f"Binance-{sym}-SELL" not in sent_positions.keys():

            response = binance_market_trade(sym.upper(), "SELL", quantity,,
            sent_positions.update({f"Binance-{sym}-SELL": response.get('orderId')})

            print("Market Order Response:", response)
            print(f"Current sent dict: {sent_positions}")
    
    
    time.sleep(5)
    
    for i in binance_positions():
        if i.get('symbol') == sym:
            quantity = i.get('positionAmt')
            
            if sent_positions.get(f"Binance-{sym}-BUY") is not None:
                
                response = binance_market_trade(sym.upper(), "SELL", quantity,,
                sent_positions.pop(f"Binance-{sym}-BUY")
                print("Market Order Response:", response)
                print(f"Current sent dict: {sent_positions}")

            elif sent_positions.get(f"Binance-{sym}-SELL") is not None:
                
                response = binance_market_trade(sym.upper(), "BUY", quantity,,
                sent_positions.pop(f"Binance-{sym}-SELL")
                print("Market Order Response:", response)
                print(f"Current sent dict: {sent_positions}")
                
def on_error_depth(ws, error):
    print("WebSocket Error (Depth):", error)

def on_close_depth(ws, close_status_code, close_msg):
    print("WebSocket (Depth) Closed")

def on_open_depth(ws):
    print("Binance WebSocket (Depth) Opened")


if __name__ == "__main__":
    # WebSocket for bids/asks (Depth)
    url_depth = f"wss://fstream.binance.com/ws/{sym.lower()}@depth5@100ms"
    ws_depth = websocket.WebSocketApp(url_depth, on_message=on_message_depth, on_error=on_error_depth, on_close=on_close_depth)
    ws_depth.on_open = on_open_depth
   
    ws_depth = threading.Thread(target=ws_depth.run_forever)
    ws_depth.start()
    ws_depth.join()
    
