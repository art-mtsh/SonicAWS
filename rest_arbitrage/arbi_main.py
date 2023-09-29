import threading
import requests
import time
import telebot
import keys
from datetime import datetime
from queue import Queue
from binance_order import binance_market_trade
from bybit_order import bybit_market_trade
from ticksize_dictionary import ticksize_dictionary

TOKEN1 = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TOKEN1)

binance_key = keys.BINANCE_API
binance_secret = keys.BINANCE_SECRET
bybit_key = keys.BYBIT_API
bybit_secret = keys.BYBIT_SECRET

dictionary_manager = Queue()

bybit_pr_done = False
binance_pr_done = False

trades = {}
keep_trading = True

alert = 0.6
exit_div = 0.1

risk_dollars = 10


def bybit_prices():
    global bybit_pr_done
    
    try:
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
    except Exception as e:
        print(f"bybit_prices\n{e}")


def binance_prices():
    global binance_pr_done
    
    try:
        
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
        
    except Exception as e:
        print(f"binance_prices\n{e}")
    
    
def calculating(filtered_pairs_ready_to_trade):
    global bybit_pr_done, binance_pr_done, keep_trading
    
    binance_prices = {}
    bybit_prices = {}
    
    while bybit_pr_done is False or binance_pr_done is False:
        try:
            dict_type, dict_data = dictionary_manager.get()

            if dict_type == "binance_prices":
                binance_prices = dict_data
                
            if dict_type == "bybit_prices":
                bybit_prices = dict_data
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            dictionary_manager.task_done()
    
    divs = []
    
    for key, value in filtered_pairs_ready_to_trade.items():
        if binance_prices and bybit_prices:
        
            binance_bid = binance_prices.get(key)[0]
            binance_ask = binance_prices.get(key)[1]
            bybit_bid = bybit_prices.get(key)[0]
            bybit_ask = bybit_prices.get(key)[1]
            
            qty = risk_dollars / binance_ask
            format_map = {
                0.00000001: f"{qty:.8f}",
                0.0000001: f"{qty:.7f}",
                0.000001: f"{qty:.6f}",
                0.00001: f"{qty:.5f}",
                0.0001: f"{qty:.4f}",
                0.001: f"{qty:.3f}",
                0.01: f"{qty:.2f}",
                0.1: f"{qty:.1f}",
                1: str(int(qty)),
                10: str(int(qty / 10) * 10),
                100: str(int(qty / 100) * 100),
                1000: str(int(qty / 1000) * 1000),
                10000: str(int(qty / 10000) * 10000),
                100000: str(int(qty / 100000) * 100000),
            }

            qty_uni = format_map.get(max([value[0], value[1]]), "Invalid qty input")
            
            # if key == "TRBUSDT": print(max(['{:.2f}'.format((binance_bid - bybit_ask) / (binance_bid / 100)), '{:.2f}'.format((bybit_bid - binance_ask) / (bybit_bid / 100))]))
            divs.append(max(['{:.2f}'.format((binance_bid - bybit_ask) / (binance_bid / 100)), '{:.2f}'.format((bybit_bid - binance_ask) / (bybit_bid / 100))]))
            
            if key not in trades.keys():
                
                if (binance_bid - bybit_ask) / (binance_bid / 100) >= alert or (bybit_bid - binance_ask) / (bybit_bid / 100) >= alert:
                    trades.update({key: 1})
                
                # higher = ""
                #
                # bin_data = {}
                # byb_data = {}
                #
                # tried_to_trade = False
                #
                # if (binance_bid - bybit_ask) / (binance_bid / 100) >= alert:
                #     higher = "Binance"
                #     bin_data = binance_market_trade(key, "SELL", qty_uni, binance_key, binance_secret)
                #     byb_data = bybit_market_trade(key, "Buy", qty_uni, bybit_key, bybit_secret)
                #     tried_to_trade = True
                #
                #     trades.update({key: {"type": "binance_higher", "binance_sell_price": binance_bid, "bybit_buy_price": bybit_ask}})
                #     bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                #                                  f"Open trades. Div: {float('{:.2f}'.format((binance_bid - bybit_ask) / (binance_bid / 100)))}%")
                #
                # elif (bybit_bid - binance_ask) / (bybit_bid / 100) >= alert:
                #     higher = "Bybit"
                #     bin_data = binance_market_trade(key, "BUY", qty_uni, binance_key, binance_secret)
                #     byb_data = bybit_market_trade(key, "Sell", qty_uni, bybit_key, bybit_secret)
                #     tried_to_trade = True
                #
                #     trades.update({key: {"type": "bybit_higher", "bybit_sell_price": bybit_bid, "binance_buy_price": binance_ask}})
                #     bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                #                                  f"Open trades. Div: {float('{:.2f}'.format((bybit_bid - binance_ask) / (bybit_bid / 100)))}%")
                #
                # if tried_to_trade:
                #     if not('status' in bin_data.keys() and bin_data['status'] == 'FILLED') or \
                #             not('retMsg' in byb_data.keys() and byb_data['retMsg'] == 'OK'):
                #         keep_trading = False
                #         if not('status' in bin_data.keys() and bin_data['status'] == 'FILLED'):
                #             binance_market_trade(symbol=key,
                #                                  side="BUY" if higher == "Binance" else "SELL",
                #                                  quantity=qty_uni,
                #                                  binance_key=binance_key,
                #                                  binance_secret=binance_secret)
                #         else:
                #             bybit_market_trade(symbol=key,
                #                                side="Sell" if higher == "Binance" else "Buy",
                #                                quantity=qty_uni,
                #                                api_key=bybit_key,
                #                                api_secret=bybit_secret)
                #
                #         bot1.send_message(662482931, f"{key}\nBinance response:\n{bin_data}\nBybit response:\n{byb_data}")
            
            elif key in trades.keys():
                
                if (binance_bid - bybit_ask) / (binance_bid / 100) >= alert or (bybit_bid - binance_ask) / (bybit_bid / 100) >= alert:
                    old_val = trades.get(key)
                    trades.update({key: old_val+1})
                else:
                    trades.pop(key)
                
                if trades.get(key):
                    if trades.get(key) >= 5:
                        bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}\n"
                                                     f"{key} is wait above {alert}%, qty {qty_uni} coins\n"
                                                     f"Bin high: {'{:.2f}'.format((binance_bid - bybit_ask) / (binance_bid / 100))}%, diff {binance_bid - bybit_ask}\n"
                                                     f"Byb high: {'{:.2f}'.format((bybit_bid - binance_ask) / (bybit_bid / 100))}%, diff{bybit_bid - binance_ask}")
                        trades.pop(key)

                # bin_data = {}
                # byb_data = {}
                #
                # tried_to_trade = False
                #
                # if trades.get(key).get("type") == "binance_higher" and abs(binance_ask - bybit_bid) / (binance_ask / 100) < exit_div:
                #
                #     bin_data = binance_market_trade(key, "BUY", qty_uni, binance_key, binance_secret)
                #     byb_data = bybit_market_trade(key, "Sell", qty_uni, bybit_key, bybit_secret)
                #     tried_to_trade = True
                #
                #     trades.pop(key)
                #     bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                #                                  f"Closed trades. Binance buy at {binance_ask}, Bybit sell at {bybit_bid}")
                #
                # elif trades.get(key).get("type") == "bybit_higher" and abs(bybit_ask - binance_bid) / (bybit_ask / 100) < exit_div:
                #
                #     bin_data = binance_market_trade(key, "SELL", qty_uni, binance_key, binance_secret)
                #     byb_data = bybit_market_trade(key, "Buy", qty_uni, bybit_key, bybit_secret)
                #     tried_to_trade = True
                #
                #     trades.pop(key)
                #     bot1.send_message(662482931, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {key}.\n"
                #                                  f"Closed trades. Binance sell at {binance_bid}, Bybit buy at {bybit_ask}")
                #
                # if tried_to_trade:
                #     if not('status' in bin_data.keys() and bin_data['status'] == 'FILLED') or \
                #             not('retMsg' in byb_data.keys() and byb_data['retMsg'] == 'OK'):
                #         keep_trading = False
                #         bot1.send_message(662482931, f"{key}\nBinance response:\n{bin_data}\nBybit response:\n{byb_data}")
                    
        else:
            print(f"{key} is fucked")
        
    if len(divs) != 0:
        print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}, max div: {max(divs)}%, ({len(divs)} coins). Watchlist: {trades}")
        
    bybit_pr_done = False
    binance_pr_done = False


if __name__ == '__main__':
    
    print("Starting...")
    pairs = ticksize_dictionary(ticksize_filter=0.07, price_filter=200)
    print(f"Start dictionary done...{len(pairs)} coins")
    time.sleep(1)
    
    while keep_trading:
        
        now = datetime.now()
        last_minute_digit = int(now.strftime('%M'))
        last_second_digit = int(now.strftime('%S'))

        if last_minute_digit % 30 == 0 and 5 > last_second_digit > 0:
            pairs = ticksize_dictionary(ticksize_filter=0.07, price_filter=200)
            print(f"Start dictionary updated...{len(pairs)} coins")
        
        bybit_pr_thread = threading.Thread(target=bybit_prices)
        binance_pr_thread = threading.Thread(target=binance_prices)
        calculating_thread = threading.Thread(target=calculating, args=(pairs,))
        
        bybit_pr_thread.start()
        binance_pr_thread.start()
        calculating_thread.start()

        bybit_pr_thread.join()
        binance_pr_thread.join()
        calculating_thread.join()
        
        time.sleep(10)
