import json
import threading
from datetime import datetime
import time
import requests
import telebot
from queue import Queue
import keys
from pybit.unified_trading import HTTP
from rest_arbitrage.binance_order import binance_market_trade

TOKEN1 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TOKEN1)

binance_key = keys.BINANCE_API
binance_secret = keys.BINANCE_SECRET
bybit_key = keys.BYBIT_API
bybit_secret = keys.BYBIT_SECRET

bybit_session = HTTP(testnet=False, api_key=bybit_key, api_secret=bybit_secret,)

dictionary_manager = Queue()
ticksize_filter = 0.03

bybit_ts_done = False
bybit_pr_done = False
binance_ts_done = False
binance_pr_done = False

trades = {}
keep_trading = True

# start_point = 0.1
# fee = 0.18
# slippage = 0.0
# profit = 0.2
alert = 0.7
exit_div = 0.1
price_filter = 100
risk_dollars = 6

def bybit_tick_sizes():
    global bybit_ts_done
    
    bybit_ticksize_url = "https://api.bybit.com/derivatives/v3/public/instruments-info"
    response = requests.get(bybit_ticksize_url)
    response_data = response.json()
    response_data = response_data.get("result").get("list")
    
    # Use a dictionary comprehension to create the bybit_tick_sizes dictionary
    bybit_tick_sizes = {
        s.get("symbol"): float(s.get("priceFilter").get("tickSize"))
        for s in response_data
    }
    
    dictionary_manager.put(("bybit_tick_sizes", bybit_tick_sizes))
    bybit_ts_done = True
def bybit_prices():
    global bybit_pr_done
    
    bybit_ticker_url = "https://api.bybit.com/v5/market/tickers?category=linear"
    response = requests.get(bybit_ticker_url)
    response_data = response.json()
    response_data = response_data.get("result").get("list")
    
    # Use a dictionary comprehension to create the bybit_prices dictionary
    bybit_prices = {
        data.get("symbol"): [float(data.get("bid1Price")), float(data.get("ask1Price"))]
        for data in response_data
    }
    
    dictionary_manager.put(("bybit_prices", bybit_prices))
    bybit_pr_done = True
def binance_tick_sizes():
    global binance_ts_done
    
    binance_ticksize_url = "https:/fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(binance_ticksize_url)
    response_data = response.json()
    response_data = response_data.get("symbols")
    
    # Use a dictionary comprehension to create the binance_tick_sizes dictionary
    binance_tick_sizes = {
        s.get("symbol"): float(s.get("filters")[0].get("tickSize"))
        for s in response_data
    }
    
    dictionary_manager.put(("binance_tick_sizes", binance_tick_sizes))
    binance_ts_done = True
def binance_prices():
    global binance_pr_done
    
    binance_ticker_url = "https://fapi.binance.com/fapi/v1/ticker/bookTicker"
    response = requests.get(binance_ticker_url)
    response_data = response.json()
    
    # Use a dictionary comprehension to create the binance_prices dictionary
    binance_prices = {
        data["symbol"]: [float(data["bidPrice"]), float(data["askPrice"])]
        for data in response_data
    }
    
    dictionary_manager.put(("binance_prices", binance_prices))
    binance_pr_done = True
def calculating():
    global bybit_ts_done, bybit_pr_done, binance_ts_done, binance_pr_done, keep_trading
    
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
    
    max_tss = {key: max(bybit_tick_sizes[key], binance_tick_sizes[key]) for key in common_keys_in_ticksizes}
    max_pss = {key: max(max(bybit_prices[key]), max(binance_prices[key])) for key in common_keys_in_prices}
    
    result = {}
    
    for key, value in max_tss.items():
        if key in max_pss.keys():
            ts = max_tss[key] / (max_pss[key] / 100)
            ts = float('{:.3f}'.format(ts))
            
            if ts <= ticksize_filter and max_pss[key] <= price_filter:
                result[key] = ts
    
    for key, value in result.items():
        
        binance_bid = binance_prices.get(key)[0]
        binance_ask = binance_prices.get(key)[1]
        bybit_bid = bybit_prices.get(key)[0]
        bybit_ask = bybit_prices.get(key)[1]
        
        qty = int(float('{:.1f}'.format(risk_dollars/ binance_bid)))
        
        if key not in trades.keys():
            
            higher = ""
            
            bin_data = None
            byb_data = None
            
            if (binance_bid - bybit_ask / (binance_bid / 100)) >= alert:
                higher = "Binance"
                bin_trade = binance_market_trade(key, "SELL", qty, binance_key, binance_secret)
                byb_trade = bybit_session.place_order(category="linear", symbol=key, side="Buy", orderType="Market", qty=str(qty))
                bin_data = json.loads(bin_trade)
                byb_data = json.loads(bin_trade)
            
            elif (bybit_bid - binance_ask / (bybit_bid / 100)) >= alert:
                higher = "Bybit"
                bin_trade = binance_market_trade(key, "BUY", qty, binance_key, binance_secret)
                byb_trade = bybit_session.place_order(category="linear", symbol=key, side="Sell", orderType="Market", qty=str(qty))
                bin_data = json.loads(bin_trade)
                byb_data = json.loads(bin_trade)
            
                
            if (bin_data and bin_data.get("status") != "FILLED") or (byb_data and byb_data.get("retMsg") != "OK"):
                keep_trading = False
                if bin_trade.get("status") == "FILLED":
                    binance_market_trade(symbol=key, side="BUY" if higher == "Binance" else "SELL", quantity=qty, binance_key=binance_key,
                                         binance_secret=binance_secret)
                else:
                    bybit_session.place_order(category="linear",
                                              symbol=key,
                                              side="Sell" if higher == "Binance" else "Buy",
                                              orderType="Market",
                                              qty=str(qty))
                bot1.send_message(662482931, f"{key}\nBinance response:\n{bin_trade}\nBybit response:\n{byb_trade}")
                print(f"{key}\nBinance response:\n{bin_trade}\nBybit response:\n{byb_trade}")
                
            elif bin_data and byb_data:
                trades.update({key: {"type": "binance_higher", "binance_sell_price": binance_bid, "bybit_buy_price": bybit_ask}})
            
                print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                      f"Open trades. Binance sell at {binance_bid}, Bybit buy at {bybit_ask}")
                
                bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                                             f"Open trades. Binance sell at {binance_bid}, Bybit buy at {bybit_ask}")
                
                time.sleep(20)

        
        elif key in trades.keys():
            
            bin_trade = json
            byb_trade = json
            
            if trades.get(key).get("type") == "binance_higher":
                
                if abs(binance_ask - bybit_bid) / (binance_ask / 100) < exit_div:
                    
                    bin_trade = binance_market_trade(key, "BUY", qty, binance_key, binance_secret)
                    byb_trade = bybit_session.place_order(category="linear", symbol=key, side="Sell", orderType="Market", qty=str(qty))
            
            elif trades.get(key).get("type") == "bybit_higher":
                
                if abs(bybit_ask - binance_bid) / (bybit_ask / 100) < exit_div:
                    
                    bin_trade = json.loads(binance_market_trade(key, "SELL", qty, binance_key, binance_secret))
                    byb_trade = json.loads(bybit_session.place_order(category="linear", symbol=key, side="Buy", orderType="Market", qty=str(qty)))
                    
            if (bin_trade.get("status") != "FILLED" or byb_trade.get("retMsg") != "OK") and len(bin_trade) != 0:
                keep_trading = False
                bot1.send_message(662482931, f"{key}\nBinance response:\n{bin_trade}\nBybit response:\n{byb_trade}")
                print(f"{key}\nBinance response:\n{bin_trade}\nBybit response:\n{byb_trade}")
            else:
                print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key} trade closed")
                bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key} trade closed")
                trades.pop(key)
    
    bybit_ts_done = False
    bybit_pr_done = False
    binance_ts_done = False
    binance_pr_done = False


if __name__ == '__main__':
    
    print("Starting...")
    
    while keep_trading:
        
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
        
        time.sleep(1)
