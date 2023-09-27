import requests
import time

bybit_ticksize_url = "https://api.bybit.com/derivatives/v3/public/instruments-info"
bybit_ticker_url = "https://api.bybit.com/v5/market/tickers?category=linear"

binance_ticksize_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
binance_ticker_url = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"

urls = [bybit_ticksize_url, bybit_ticker_url, binance_ticksize_url, binance_ticker_url]

while True:
    urls = [bybit_ticksize_url, bybit_ticker_url, binance_ticksize_url, binance_ticker_url]
    
    for url in urls:
        # Send a GET request to the Binance API
        start_time = time.time()  # Record the start time
        response = requests.get(url)
        end_time = time.time()    # Record the end time
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Print the response time
        print(f"{url} response: {response_time} seconds")
    
        time.sleep(2)
        
    print("")