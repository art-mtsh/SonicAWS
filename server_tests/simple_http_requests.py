import requests

url1 = "https://fapi.binance.com/fapi/v1/ping"
url2 = "https://fapi.binance.com/fapi/v1/time"
url3 = "https://fapi.binance.com/fapi/v1/exchangeInfo"
url4 = "https://api.bybit.com/derivatives/v3/public/instruments-info"
url5 = "https://api.bybit.com/derivatives/v3/public/mark-price-kline?symbol=BTCUSD&interval=1&start=1670261100000&end=1670261280000&category=inverse"


ticksizes = {}

try:
    response = requests.get(url3)
    response.raise_for_status()  # Check for any HTTP errors

    if response.status_code == 200:
        response_data = response.json()
        # response_data = response_data.get("result").get("list")
        # print(response_data)
        
        # for data in response_data:
        #     symbol = data.get("symbol")
        #     tick_size = data.get("priceFilter").get("tickSize")
        #     minQty = data.get("lotSizeFilter").get("qtyStep")
        #     mintradeQty = data.get("lotSizeFilter").get("minTradingQty")
        #     if float(minQty) != float(mintradeQty):
        #         print(f"{symbol}, {tick_size}, step: {minQty}, min trade: {mintradeQty}")
            # print(f"{symbol}, {tick_size}, step: {minQty}, min trade: {mintradeQty}")
            
        response_data = response_data.get("symbols")
        print(response_data)
        
        for sym in response_data:
            symbol = sym.get("symbol")
            tick_size = sym.get("filters")[0].get("tickSize")
            quantityPrecision = sym.get("quantityPrecision")
            scale = sym.get("filters")[1]
            scale = scale.get("minQty")
            notional = sym.get("filters")[5]
            notional = notional.get("notional")
            
            
            
        #     # ticksizes.update({symbol: tick_size})
        #
            print(f"{symbol}, {tick_size}, {scale}, notional {notional}")
        
    else:
        print(f"Received status code: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

