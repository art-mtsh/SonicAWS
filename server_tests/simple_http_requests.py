import time

import requests

url1 = "https://fapi.binance.com/fapi/v1/ping"
url2 = "https://fapi.binance.com/fapi/v1/time"
url3 = "https://fapi.binance.com/fapi/v1/exchangeInfo"
url4 = "https://api.binance.com/api/v3/exchangeInfo"
url5 = "https://api.binance.com/api/v3/ticker/bookTicker"
url10 = "https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=1"
url10 = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=5"

url6 = "https://api.bybit.com/derivatives/v3/public/instruments-info"
url7 = "https://api.bybit.com/spot/v3/public/symbols"
url8 = "https://api.bybit.com/spot/v3/public/quote/ticker/24hr"
url9 = "https://api.bybit.com/derivatives/v3/public/mark-price-kline?symbol=BTCUSD&interval=1&start=1670261100000&end=1670261280000&category=inverse"


ticksizes = {}

while True:
    try:
        response = requests.get(url10)
        response.raise_for_status()  # Check for any HTTP errors
    
        if response.status_code == 200:
            response_data = response.json()
            # response_data = response_data.get("result").get("list")
            for binance_candle_data in response_data:
                
                timestamp = binance_candle_data[0]
                open = float(binance_candle_data[1])
                high = binance_candle_data[2]
                low = binance_candle_data[3]
                close = float(binance_candle_data[4])
                volume = float(binance_candle_data[5])
                quote_asset_volume = float(binance_candle_data[7])
                buy_volume = float(binance_candle_data[9])
                taker_buy_quote_volume = float(binance_candle_data[10])
                
                print(f"volume {volume}, quote_asset_volume {quote_asset_volume}, taker_buy_asset_volume {buy_volume}, taker_buy_quote_volume {taker_buy_quote_volume}")
                print(f"volume {volume}, buys {buy_volume}, sells {volume - buy_volume}")
                print("")
            # for data in response_data:
            #     symbol = data.get("s")
            #     bid = data.get("bp")
            #     ask = data.get("ap")
            #     print(f"{symbol}, {bid}, {ask}")
            #     # tick_size = data.get("priceFilter").get("tickSize")
            #     minQtySell = data.get("minTradeQty")
            #     minPricePrecision = data.get("minPricePrecision")
            # #     mintradeQty = data.get("lotSizeFilter").get("minTradingQty")
            #     print(f"{symbol}, {minQtySell}, {minPricePrecision}")
            
            # response_data = response_data.get("symbols")
            # print(response_data)
            # syms = []
            # for sym in response_data:
            #     symbol = sym.get("symbol")
            #     filters = sym.get("filters")
            #     tick_size = sym.get("filters")[0].get("tickSize")
            #     minQty = sym.get("filters")[1].get("minQty")
            #     syms.append(sym)
            #     print(f"{symbol}, {tick_size}, {minQty}")
            
            # for sym in response_data:
            #     symbol = sym.get("symbol")
            #     bid = float(sym.get("bidPrice"))
            #     ask = float(sym.get("askPrice"))
            #     spread: float
            #     if bid != 0:
            #         spread = abs(bid - ask) / (bid / 100)
            #
            #     if 1000 >= float(bid) >= 0.0001 and spread < 0.2:
            #         print(f"{symbol}: {bid}")
            #         syms.append(sym)
            #
            # print(len(syms))
            
        else:
            print(f"Received status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    time.sleep(400)
