import requests


def extremum(symbol, frame, request_limit_length):
    futures_klines = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={request_limit_length}'
    klines = requests.get(futures_klines)
    
    if klines.status_code == 200:
        
        response_length = len(klines.json()) if klines.json() != None else 0
        print(futures_klines)
    
    else:
        print(f"TROUBLES WITH {symbol} DATA, status code {klines.status_code}")
        
extremum('BTCUSDT', '1m', 10)

