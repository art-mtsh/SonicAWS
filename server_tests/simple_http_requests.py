import time

import requests

url1 = "https://fapi.binance.com/fapi/v1/ping"
url2 = "https://fapi.binance.com/fapi/v1/time"
binance_futures = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
url4 = "https://api.binance.com/api/v3/exchangeInfo"
binance_spot = "https://api.binance.com/api/v3/ticker/bookTicker"
url10 = "https://api.binance.com/api/v3/klines?symbol=TOMOUSDT&interval=2h&limit=5"
url11 = "https://api.binance.com/api/v3/ticker/24hr"
url12 = "https://fapi.binance.com/fapi/v1/depth?symbol=TOMOUSDT&limit=20"

url6 = "https://api.bybit.com/derivatives/v3/public/instruments-info"
url7 = "https://api.bybit.com/spot/v3/public/symbols"
url8 = "https://api.bybit.com/spot/v3/public/quote/ticker/24hr"
url9 = "https://api.bybit.com/derivatives/v3/public/mark-price-kline?symbol=BTCUSD&interval=1&start=1670261100000&end=1670261280000&category=inverse"


ticksizes = {}
price_filter = 0.0000001

while True:
    try:
        response = requests.get(url12)
        response.raise_for_status()

        if response.status_code == 200:
            response_data = response.json()
            bids = response_data.get('bids')
            asks = response_data.get('asks')
            # print(bids)
            # print(asks)
            for i in asks[::-1]:
                price = float(i[0])
                value = float(i[1])
                print(f"{value} ... {price}")

            print("| = = = = = = |")
            for i in bids:
                price = float(i[0])
                value = float(i[1])
                print(f"{value} ... {price}")

            

        else:
            print(f"Received status code: {response.status_code}")

        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
    print("")
    time.sleep(1)
