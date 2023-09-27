import time
import requests
import telebot

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

ticksize_filter = 0.03



def check_for_arbi():
    # =============================== BYBIT TICK SIZES
    
    bybit_tick_sizes = {}
    bybit_ticksize_url = "https://api.bybit.com/derivatives/v3/public/instruments-info"
    response = requests.get(bybit_ticksize_url)
    response_data = response.json()
    response_data = response_data.get("result").get("list")
    
    for s in response_data:
        symbol = s.get("symbol")
        tick_size_bybit = float(s.get("priceFilter").get("tickSize"))
        
        bybit_tick_sizes.update({symbol: tick_size_bybit})
    
    # =============================== BYBIT TICK PRICES
    
    bybit_prices = {}
    bybit_ticker_url = "https://api.bybit.com/v5/market/tickers?category=linear"
    response = requests.get(bybit_ticker_url)
    response_data = response.json()
    response_data = response_data.get("result").get("list")
    
    for data in response_data:
        symbol = data.get("symbol")
        bid_price = float(data.get("bid1Price"))
        ask_price = float(data.get("ask1Price"))
        
        bybit_prices.update({symbol: [bid_price, ask_price]})
    
    # =============================== BINANCE TICK SIZES
    
    binance_tick_sizes = {}
    binance_ticksize_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(binance_ticksize_url)
    response_data = response.json()
    response_data = response_data.get("symbols")
    
    for s in response_data:
        symbol = s.get("symbol")
        tick_size_binance = s.get("filters")[0]
        tick_size_binance = float(tick_size_binance.get("tickSize"))
        
        binance_tick_sizes.update({symbol: tick_size_binance})
    
    # =============================== BINANCE TICK PRICES
    
    binance_prices = {}
    binance_ticker_url = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
    response = requests.get(binance_ticker_url)
    response_data = response.json()
    
    for data in response_data:
        symbol = data.get("symbol")
        bid_price = float(data.get("bidPrice"))
        ask_price = float(data.get("askPrice"))
        
        binance_prices.update({symbol: [bid_price, ask_price]})
    
    # Find common keys between the first set of dictionaries
    common_keys_in_ticksizes = set(bybit_tick_sizes.keys()) & set(binance_tick_sizes.keys())
    
    # Find common keys between the second set of dictionaries
    common_keys_in_prices = set(bybit_prices.keys()) & set(binance_prices.keys())
    
    # Initialize dictionaries to store max values for common keys
    max_tss = {}
    max_pss = {}
    
    # Calculate max values for the first set of dictionaries
    for key in common_keys_in_ticksizes:
        max_tss[key] = max(bybit_tick_sizes[key], binance_tick_sizes[key])
    
    # Calculate max values for the second set of dictionaries
    for key in common_keys_in_prices:
        max_pss[key] = max(max(bybit_prices[key]), max(binance_prices[key]))
    
    # Divide values of the second set of max values by values of the first set
    result = {}
    
    for key, value in max_tss.items():
        if key in max_pss.keys():
            ts = max_tss[key] / (max_pss[key] / 100)
            ts = float('{:.3f}'.format(ts))
            
            if ts <= ticksize_filter:
                result[key] = ts
    
    for key, value in result.items():
        
        binance_bid = binance_prices.get(key)[0]
        binance_ask = binance_prices.get(key)[1]
        bybit_bid = bybit_prices.get(key)[0]
        bybit_ask = bybit_prices.get(key)[1]
        
        binance_higher = binance_bid - bybit_ask
        bybit_higher = bybit_bid - binance_ask
        
        binance_higher = float('{:.5f}'.format(binance_higher))
        bybit_higher = float('{:.5f}'.format(bybit_higher))
        
        binance_higher_p = binance_higher / (binance_bid / 100)
        bybit_higher_p = bybit_higher / (bybit_bid / 100)
        
        binance_higher_p = float('{:.3f}'.format(binance_higher_p))
        bybit_higher_p = float('{:.3f}'.format(bybit_higher_p))
        
        fee = 0.18
        spread = 0.14
        slippage = 0.0
        profit = 0.2
        alert = fee + spread + slippage + profit
        
        if binance_higher_p >= alert:
            print(f"{key}. bin_bid {binance_bid} - byb_ask {bybit_ask} = {binance_higher} ({binance_higher_p}%)")
            # bot3.send_message(662482931, f"{key}. bin_bid {binance_bid} - byb_ask {bybit_ask} = {binance_higher} ({binance_higher_p}%)")
            
        elif bybit_higher_p >= alert:
            print(f"{key}. byb_bid {bybit_bid} - bin_ask {binance_ask} = {bybit_higher} ({bybit_higher_p}%)")
            # bot3.send_message(662482931, f"{key}. byb_bid {bybit_bid} - bin_ask {binance_ask} = {bybit_higher} ({bybit_higher_p}%)")
            
        # else:
        #     print(f"{key}: {max([binance_higher_p, bybit_higher_p])}%")

if __name__ == '__main__':
    while True:
        time1 = time.perf_counter()
        
        check_for_arbi()
        
        time2 = time.perf_counter()
        time3 = time2 - time1
        
        print(f"Finished processes in {time3} seconds")
        
        time.sleep(60)
