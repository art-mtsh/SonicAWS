import requests

# Define the exclusion list outside of the function
exclude = ["USDCUSDT", "HNTUSDT", "CVCUSDT", "SCUSDT"]


def binance_pairs(chunks):
    url3 = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    
    response = requests.get(url3)
    response.raise_for_status()  # Check for any HTTP errors
    
    symbols_from_bi = []
    
    if response.status_code == 200:
        response_data = response.json()
        response_data = response_data.get("symbols")
        
        for sym in response_data:
            symbol = sym.get("symbol")
            if symbol in exclude:
                continue  # Skip symbols in the exclusion list
            symbols_from_bi.append(symbol)
    
    # Calculate the chunk size
    chunk_size = len(symbols_from_bi) // chunks
    
    # Split symbols_from_bi into chunks
    chunked_symbols = [symbols_from_bi[i:i + chunk_size] for i in range(0, len(symbols_from_bi), chunk_size)]
    
    return chunked_symbols


# # Example usage: Split symbols_from_bi into 5 chunks and exclude symbols in the predefined exclusion list
# chunked_symbols = binance_pairs(16)
# for chunk in chunked_symbols:
#     print(chunk)
