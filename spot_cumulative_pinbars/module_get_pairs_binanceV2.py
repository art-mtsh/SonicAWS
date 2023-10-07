import requests

def binance_pairs(chunks, price_filter):
    excluded_substrings = ["RUB", "USDPUSDT", "EURBUSD", "EURUSDT", "TUSDUSDT", "TUSDBUSD", "FDUSDBUSD", "USDCUSDT", "FDUSDUSDT", "BETH", "TRY"]
    
    binance_ticker_url = "https://api.binance.com/api/v3/ticker/bookTicker"
    response = requests.get(binance_ticker_url)
    response_data = response.json()
    filtered_symbols = []
    for data in response_data:
        if float(data["bidPrice"]) >= price_filter and not any(substring in data["symbol"] for substring in excluded_substrings):
            filtered_symbols.append(data["symbol"])
    
    # Calculate the chunk size
    chunk_size = len(filtered_symbols) // chunks
    
    # Split symbols_from_bi into chunks
    chunked_symbols = [filtered_symbols[i:i + chunk_size] for i in range(0, len(filtered_symbols), chunk_size)]
    
    return chunked_symbols

# for i in binance_pairs(16, 0.0001):
#     print(i)