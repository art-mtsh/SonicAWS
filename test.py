import requests


def extremum(symbol, frame, request_limit_length):
    futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
    klines = requests.get(futures_klines)
    
    if klines.status_code == 200:
        
        response_length = len(klines.json()) if klines.json() != None else 0
        
        if response_length == request_limit_length:
            
            binance_candle_data = klines.json()
            open = list(float(i[1]) for i in binance_candle_data)
            high = list(float(i[2]) for i in binance_candle_data)
            low = list(float(i[3]) for i in binance_candle_data)
            close = list(float(i[4]) for i in binance_candle_data)
            volume = list(float(i[5]) for i in binance_candle_data)
            trades = list(int(i[8]) for i in binance_candle_data)
            buy_volume = list(float(i[9]) for i in binance_candle_data)
            sell_volume = [volume[0] - buy_volume[0]]
            
            print(max(high), min(low))
    
    else:
        print(f"TROUBLES WITH {symbol} DATA, status code {klines.status_code}")
        
extremum('1000PEPEUSDT', '1m', 10)

