import time

import requests

url1 = "https://fapi.binance.com/fapi/v1/ping"
url2 = "https://fapi.binance.com/fapi/v1/time"
binance_futures = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
url4 = "https://api.binance.com/api/v3/exchangeInfo"
binance_spot = "https://api.binance.com/api/v3/ticker/bookTicker"
url10 = "https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=1"
url10 = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=5"

url6 = "https://api.bybit.com/derivatives/v3/public/instruments-info"
url7 = "https://api.bybit.com/spot/v3/public/symbols"
url8 = "https://api.bybit.com/spot/v3/public/quote/ticker/24hr"
url9 = "https://api.bybit.com/derivatives/v3/public/mark-price-kline?symbol=BTCUSD&interval=1&start=1670261100000&end=1670261280000&category=inverse"


ticksizes = {}
price_filter = 0.0000001

while True:
    try:
        response = requests.get(binance_futures)
        response.raise_for_status()
        futures = []
        if response.status_code == 200:
            response_data = response.json()
            # response_data = response_data.get("symbols")
            # print(response_data)
            for data in response_data:
            #     print(data)
                if float(data["bidPrice"]) >= price_filter and \
                        "RUB" not in data["symbol"] and \
                        "USDPUSDT" not in data["symbol"] and \
                        "EURBUSD" not in data["symbol"] and \
                        "EURUSDT" not in data["symbol"] and \
                        "TUSDUSDT" not in data["symbol"] and \
                        "TUSDBUSD" not in data["symbol"]:
                    futures.append(data["symbol"])

        response = requests.get(binance_spot)
        response.raise_for_status()  # Check for any HTTP errors
        spots = []
        if response.status_code == 200:
            response_data = response.json()
            # response_data = response_data.get("symbols")
            # print(response_data)
            for data in response_data:
                #     print(data)
                if float(data["bidPrice"]) >= price_filter and \
                        "RUB" not in data["symbol"] and \
                        "USDPUSDT" not in data["symbol"] and \
                        "EURBUSD" not in data["symbol"] and \
                        "EURUSDT" not in data["symbol"] and \
                        "TUSDUSDT" not in data["symbol"] and \
                        "TUSDBUSD" not in data["symbol"]:
                    spots.append(data["symbol"])
        
        else:
            print(f"Received status code: {response.status_code}")
        print(futures)
        print(spots)
        
        print(len(futures))
        print(len(spots))
        
        result_1 = list(set(spots).difference(futures))
        print(result_1)
        print(len(result_1))
        
        result_2 = list(set(futures).difference(spots))
        print(result_2)
        print(len(result_2))
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    time.sleep(400)
