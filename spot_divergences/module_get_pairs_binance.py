import requests

def binance_pairs(chunks):
    def binance_tick_sizes():
        binance_ticksize_url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(binance_ticksize_url)
        response_data = response.json()
        response_data = response_data.get("symbols")
        
        # Use a dictionary comprehension to create the binance_tick_sizes dictionary
        binance_tick_sizes = {
            s.get("symbol"): [
                float(s.get("filters")[0].get("tickSize")),
                (s.get("filters")[1]).get("minQty")
            ]
            for s in response_data
        }
        return binance_tick_sizes
    
    def binance_prices():
        binance_ticker_url = "https://api.binance.com/api/v3/ticker/bookTicker"
        response = requests.get(binance_ticker_url)
        response_data = response.json()
        
        # Use a dictionary comprehension to create the binance_prices dictionary
        binance_prices = {
            data["symbol"]: [float(data["bidPrice"]), float(data["askPrice"])]
            for data in response_data
        }
        return binance_prices
    
    ticksize_dictionary = binance_tick_sizes()
    prices_dictionary = binance_prices()
    filtered_dictionary = []
    
    for s, vals in ticksize_dictionary.items():
        if s in prices_dictionary.keys():
            bid = prices_dictionary.get(s)[0]
            ask = prices_dictionary.get(s)[1]
            if bid != 0 and ask != 0 and "RUB" not in s:
                
                tick_size = ticksize_dictionary.get(s)[0]
                minimum_size = ticksize_dictionary.get(s)[1]
                
                tick_size_percent = tick_size / (bid / 100) if bid != 0 else 100
                spread = abs(bid - ask)
                spread_percent = spread / (bid / 100) if bid != 0 else 100
                
                if bid >= 0.0001 and tick_size_percent <= 0.1:
                    filtered_dictionary.append(s)
    
    # Calculate the chunk size
    chunk_size = len(filtered_dictionary) // chunks
    
    # Split symbols_from_bi into chunks
    chunked_symbols = [filtered_dictionary[i:i + chunk_size] for i in range(0, len(filtered_dictionary), chunk_size)]
    
    return chunked_symbols