from multiprocessing import Process
import requests

"""
volatility = (max(day) - min(day) / 100%
volume daily = 20+ M
minute ATR%
ticksize %
change daily
trades daily

"""

excluded = ['SOLUSDT', 'TRBUSDT']

def calculate(dict_of_pairs):
    
    request_limit_length = 288
    frame = '5m'
    
    for symbol, ts in dict_of_pairs.items():
        futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
        # spot_klines = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={frame}&limit={request_limit_length}'
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
    
                daily_volatility = (max(high) - min(low)) / (close[-1] / 100)
                daily_volatility = float('{:.2f}'.format(daily_volatility))
    
                daily_change = (close[-1] - close[0]) / (close[-1] / 100)
                daily_change = float('{:.2f}'.format(daily_change))
    
                daily_volume = sum(volume) / 1000000
                daily_volume = float('{:.2f}'.format(daily_volume))
    
                daily_trades = int(sum(trades) / 1000)
    
                avg_atr_per = [(high[-c] - low[-c]) / (close[-c] / 100) for c in range(int(request_limit_length / 2))]
                avg_atr_per = float('{:.2f}'.format(sum(avg_atr_per) / len(avg_atr_per)))
    
                ts_percent = float(ts) / (close[-1] / 100)
                ts_percent = float('{:.4f}'.format(ts_percent))
                
                if daily_volume >= 3 and daily_trades >= 30 and avg_atr_per >= 0.8 and ts_percent <= 0.04 and symbol not in excluded:
                    # print(f"{symbol} volatility: {daily_volatility}%, day change: {daily_change}%, volume: {daily_volume}M, trades: {daily_trades}K, atr5m: {avg_atr_per}%, ticksize: {ts_percent}%")
                    print(symbol, end=", ")
                # if symbol == 'BTCUSDT':
                #     print(f" ======>>> {symbol} volatility: {daily_volatility}%, day change: {daily_change}%, volume: {daily_volume}M, trades: {daily_trades}K, atr5m: {avg_atr_per}%, ticksize: {ts_percent}%")
                    
def split_dict(input_dict, num_parts):
    avg = len(input_dict) // num_parts
    remainder = len(input_dict) % num_parts
    result = []
    start = 0

    for i in range(num_parts):
        end = start + avg + (1 if i < remainder else 0)
        result.append({k: input_dict[k] for k in list(input_dict)[start:end]})
        start = end

    return result


if __name__ == '__main__':
    
    ts_dict = {}
    
    futures_exchange_info_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    
    response = requests.get(futures_exchange_info_url)
    response_data = response.json()
    response_data = response_data.get("symbols")
    for data in response_data:
        symbol = data['symbol']
        filters = data['filters']
        tick_size = filters[0]['tickSize']
        quoteAsset = data['quoteAsset']
        if quoteAsset == "USDT":
            ts_dict.update({symbol: tick_size})
    
    list_of_dicts = split_dict(ts_dict, 16)

    the_processes = []
    for dict_of_pairs in list_of_dicts:
        process = Process(target=calculate,
                          args=(
                              dict_of_pairs,
                          ))
        the_processes.append(process)
    
    for pro in the_processes:
        pro.start()
    
    for pro in the_processes:
        pro.join()
    
    for pro in the_processes:
        pro.close()

