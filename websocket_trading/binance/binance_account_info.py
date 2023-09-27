import requests
import hashlib
import hmac
import time
from websocket_trading import keys


# API credentials
api_key = keys.BINANCE_API
api_secret = keys.BINANCE_SECRET
def binance_positions():
    url = 'https://fapi.binance.com/fapi/v2/account'
    timestamp = int(time.time() * 1000)
    params = {
        'timestamp': timestamp,
    }
    query_string = '&'.join([f'{key}={params[key]}' for key in sorted(params.keys())])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    headers = {
        'X-MBX-APIKEY': api_key
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        account_info = response.json()
        positions = account_info.get("positions")
        opened = []
        for i in positions:
            if float(i.get("unrealizedProfit")) != 0:
                opened.append(i)
        # print(opened)
        return opened
        
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)

