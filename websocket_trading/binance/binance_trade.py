import requests
import time
import hmac
import hashlib
from websocket_trading import keys

# Binance API Key and Secret
api_key = keys.BINANCE_API
api_secret = keys.BINANCE_SECRET


def binance_trade(symbol, side, quantity):
    base_url = "https://fapi.binance.com"  # Binance Futures API endpoint
    endpoint = "/fapi/v1/order"
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000),
        "newOrderRespType": "RESULT"  # Set the response type
    }

    headers = {
        "X-MBX-APIKEY": api_key
    }

    # Create a signature for the request
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params["signature"] = signature

    response = requests.post(base_url + endpoint, params=params, headers=headers)

    return response.json()
