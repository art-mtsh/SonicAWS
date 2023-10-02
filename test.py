import requests

symbol = 'BTCUSDT'
binance_frame = '1m'
request_limit_length = 1000

url = f'https://api.binance.com/api/v3/aggTrades?symbol={symbol}&limit={request_limit_length}'
response = requests.get(url)
data = response.json()

# print(data)
candles = []
buy_volume = 0
sell_volume = 0

for trade in data:
    trade_time = trade.get('T') // 1000  # Convert milliseconds to seconds
    trade_volume = float(trade['q'])
    is_buyer_market_maker = trade['m']  # True for buyer market maker, False for seller market maker

    if is_buyer_market_maker:
        buy_volume += trade_volume
    else:
        sell_volume += trade_volume

    candles.append({
        'timestamp': trade_time,
        'buy_volume': buy_volume,
        'sell_volume': sell_volume
    })

for c in candles:
	print(c)
#