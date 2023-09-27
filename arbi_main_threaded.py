import threading
from datetime import datetime
import time
import requests
import telebot
from queue import Queue

TOKEN1 = '5657267406:AAExhEvjG3tjb0KL6mTM9otoFiL6YJ_1aSA'
bot1 = telebot.TeleBot(TOKEN1)

TOKEN2 = '5947685641:AAEofMStDGj0M0nGhVdlMEEEFP-dOAgOPaw'
bot2 = telebot.TeleBot(TOKEN2)

TOKEN3 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot3 = telebot.TeleBot(TOKEN3)

dictionary_manager = Queue()

ticksize_filter = 0.03

bybit_ts_done = False
bybit_pr_done = False
binance_ts_done = False
binance_pr_done = False

trades = {}


def bybit_tick_sizes():
    global bybit_ts_done
    
    bybit_tick_sizes = {}
    bybit_ticksize_url = "https://api.bybit.com/derivatives/v3/public/instruments-info"
    response = requests.get(bybit_ticksize_url)
    response_data = response.json()
    response_data = response_data.get("result").get("list")
    
    for s in response_data:
        symbol = s.get("symbol")
        tick_size_bybit = float(s.get("priceFilter").get("tickSize"))
        
        bybit_tick_sizes.update({symbol: tick_size_bybit})
    
    dictionary_manager.put(("bybit_tick_sizes", bybit_tick_sizes))
    bybit_ts_done = True


def bybit_prices():
    global bybit_pr_done
    
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
    
    dictionary_manager.put(("bybit_prices", bybit_prices))
    bybit_pr_done = True


def binance_tick_sizes():
    global binance_ts_done
    
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
    
    dictionary_manager.put(("binance_tick_sizes", binance_tick_sizes))
    binance_ts_done = True


def binance_prices():
    global binance_pr_done
    
    binance_prices = {}
    binance_ticker_url = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
    response = requests.get(binance_ticker_url)
    response_data = response.json()
    
    for data in response_data:
        symbol = data.get("symbol")
        bid_price = float(data.get("bidPrice"))
        ask_price = float(data.get("askPrice"))
        
        binance_prices.update({symbol: [bid_price, ask_price]})
    
    dictionary_manager.put(("binance_prices", binance_prices))
    binance_pr_done = True


def calculating():
    global bybit_ts_done, bybit_pr_done, binance_ts_done, binance_pr_done
    
    bybit_tick_sizes = {}
    binance_tick_sizes = {}
    
    bybit_prices = {}
    binance_prices = {}
    
    while bybit_ts_done is False or bybit_pr_done is False or binance_ts_done is False or binance_pr_done is False:
        
        try:
            dict_type, dict_data = dictionary_manager.get()
            
            if dict_type == "bybit_tick_sizes":
                bybit_tick_sizes = dict_data
            if dict_type == "binance_tick_sizes":
                binance_tick_sizes = dict_data
            if dict_type == "bybit_prices":
                bybit_prices = dict_data
            if dict_type == "binance_prices":
                binance_prices = dict_data
        
        except Exception as e:
            print(f"Error processing message: {e}")
        
        finally:
            dictionary_manager.task_done()
    
    common_keys_in_ticksizes = set(bybit_tick_sizes.keys()) & set(binance_tick_sizes.keys())
    common_keys_in_prices = set(bybit_prices.keys()) & set(binance_prices.keys())
    
    max_tss = {}
    max_pss = {}
    
    for key in common_keys_in_ticksizes:
        max_tss[key] = max(bybit_tick_sizes[key], binance_tick_sizes[key])
    
    for key in common_keys_in_prices:
        max_pss[key] = max(max(bybit_prices[key]), max(binance_prices[key]))
    
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
        
        start_point = 0.1
        fee = 0.18
        slippage = 0.0
        profit = 0.2
        alert = start_point + fee + slippage + profit
        
        if binance_higher_p >= alert and key not in trades.keys():
            
            trades.update(
                {key: {
                    "type": "binance_higher",
                    "binance_sell_price": binance_bid,
                    "bybit_buy_price": bybit_ask
                }}
            )
            
            print(f"{key}. Open trades. Binance sell at {binance_bid}, Bybit buy at {bybit_ask} ({binance_higher_p}%)")
            bot3.send_message(662482931, f"{key}. Open trades. Binance sell at {binance_bid}, Bybit buy at {bybit_ask} ({binance_higher_p}%)")
        
        elif bybit_higher_p >= alert and key not in trades.keys():
            
            trades.update(
                {key: {
                    "type": "bybit_higher",
                    "bybit_sell_price": bybit_bid,
                    "binance_buy_price": binance_ask
                }}
            )
            
            print(f"{key}. Open trades. Bybit sell at {bybit_bid}, Binance buy at {binance_ask} ({bybit_higher_p}%)")
            bot3.send_message(662482931, f"{key}. Open trades. Bybit sell at {bybit_bid}, Binance buy at {binance_ask} ({bybit_higher_p}%)")
        
        elif key in trades.keys():
            if trades.get(key).get("type") == "binance_higher":
                entry_div = (trades.get(key).get("binance_sell_price") - trades.get(key).get("bybit_buy_price")) / (
                            trades.get(key).get("binance_sell_price") / 100)
                current_div = abs((binance_ask - bybit_bid) / (max([binance_ask, bybit_bid]) / 100))
                
                entry_div = float('{:.2f}'.format(entry_div))
                current_div = float('{:.2f}'.format(current_div))
                
                unrealized_range = entry_div - current_div
                unrealized_range = float('{:.2f}'.format(unrealized_range))
                
                if entry_div - current_div >= profit + fee:
                    print(f"{key}. Closed trades with div range {unrealized_range}%")
                    bot3.send_message(662482931, f"{key}. Closed trades with div range {unrealized_range}%")
                    trades.pop(key)
            
            
            elif trades.get(key).get("type") == "bybit_higher":
                entry_div = (trades.get(key).get("bybit_sell_price") - trades.get(key).get("binance_buy_price")) / (
                            trades.get(key).get("bybit_sell_price") / 100)
                current_div = abs((binance_bid - bybit_ask) / (max([binance_bid, bybit_ask]) / 100))
                
                entry_div = float('{:.2f}'.format(entry_div))
                current_div = float('{:.2f}'.format(current_div))
                
                unrealized_range = entry_div - current_div
                unrealized_range = float('{:.2f}'.format(unrealized_range))
                
                if entry_div - current_div >= profit + fee:
                    print(f"{key}. Closed trades with div range {unrealized_range}%")
                    bot3.send_message(662482931, f"{key}. Closed trades with div range {unrealized_range}%")
                    trades.pop(key)
                    
    print(f"{datetime.now().strftime('%H:%M:%S')} {trades}")
    
    bybit_ts_done = False
    bybit_pr_done = False
    binance_ts_done = False
    binance_pr_done = False


if __name__ == '__main__':
    
    print("Starting...")
    
    while True:
        bybit_ts_thread = threading.Thread(target=bybit_tick_sizes)
        bybit_pr_thread = threading.Thread(target=bybit_prices)
        binance_ts_thread = threading.Thread(target=binance_tick_sizes)
        binance_pr_thread = threading.Thread(target=binance_prices)
        calculating_thread = threading.Thread(target=calculating)
        
        bybit_ts_thread.start()
        bybit_pr_thread.start()
        binance_ts_thread.start()
        binance_pr_thread.start()
        calculating_thread.start()
        
        bybit_ts_thread.join()
        bybit_pr_thread.join()
        binance_ts_thread.join()
        binance_pr_thread.join()
        calculating_thread.join()
        
        time.sleep(2)
