import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
from result_plot import plotting
import os

'''
Тест на Н1.
Спочатку код реформатує М1 в Н1
'''

def search(filtered_symbols, shared_queue):
    for pair_path in filtered_symbols:

        file_name = os.path.basename(pair_path)
        symbol = file_name.split('-')[0]
        data = read_csv_transposed(pair_path)

        start = 60
        next_trade_index = 0
        risk_reward = 1
        atr_len = 30
        part = 3
        room_ttl = 12
        brr_filter = 25

        # M1 to H1
        c_open = []
        c_high = []
        c_low = []
        c_close = []
        c_volume = []
        c_buy = []
        c_sell = []
        c_timestamp = []
        for d in range(start, len(data[6])):

            minute = int(data[6][d]) / 1000
            minute = datetime.fromtimestamp(minute)
            minute = int(minute.strftime("%M"))

            if minute == 59:
                hour_open = data[1][d - 59]
                hour_high = max(data[2][d: d-60: -1])
                hour_low = min(data[3][d: d-60: -1])
                hour_close = data[4][d]
                hour_volume = sum(data[5][d: d-60: -1])
                hour_timestamp = data[6][d]
                hour_buy_volume = sum(data[9][d: d - 60: -1])
                hour_sell_volume = hour_volume - hour_buy_volume

                c_open.append(hour_open)
                c_high.append(hour_high)
                c_low.append(hour_low)
                c_close.append(hour_close)
                c_volume.append(hour_volume)
                c_timestamp.append(hour_timestamp)
                c_buy.append(hour_buy_volume)
                c_sell.append(hour_sell_volume)

        if len(c_open) == len(c_high) == len(c_low) == len(c_close) != 0 and 0 not in c_open and 0 not in c_high and 0 not in c_low and 0 not in c_close:

            for a in range(60, len(c_open) - 5):

                if a < next_trade_index:
                    continue
                # elif symbol == "AAVEUSDT":
                else:
                    candle_time = c_timestamp[a] / 1000
                    candle_time = datetime.fromtimestamp(candle_time)
                    candle_time = candle_time.strftime("%d.%m.%Y %H:%M:%S")

                    # ==== GAP ====
                    max_gap = 0
                    for curr_index in range(a-20, a):
                        gap = abs(c_open[curr_index] - c_close[curr_index - 1])
                        gap_p = 0
                        if c_open[curr_index] != 0: gap_p = gap / (c_open[curr_index] / 100)
                        if gap_p > max_gap: max_gap = gap_p
                    max_gap = float('{:.3f}'.format(max_gap))

                    # ==== ATR % ====
                    avg_atr = [c_high[a - c] - c_low[a - c] for c in range(atr_len)]
                    avg_atr = sum(avg_atr) / len(avg_atr)
                    atr_percent = avg_atr / (c_close[a] / 100)

                    hl_range = c_high[a] - c_low[a] if c_high[a] - c_low[a] != 0 else 0.0001
                    brr_percent = abs(c_open[a] - c_close[a]) / (hl_range / 100)
                    b_range_percent = (hl_range) / (c_close[a] / 100)

                    direction = "no"
                    if min(c_open[a], c_close[a]) >= c_high[a] - hl_range / part and c_low[a] <= min(c_low[a: a-room_ttl:-1]):
                        direction = "Bull"
                    elif max(c_open[a], c_close[a]) <= c_low[a] + hl_range / part and c_high[a] >= max(c_high[a: a-room_ttl:-1]):
                        direction = "Bear"
                    else:
                        direction = "None"

                    delta = c_buy[a] - c_sell[a]

                    if brr_percent <= brr_filter and atr_percent * 1 <= b_range_percent <= atr_percent * 2:
                        if direction == "Bull" and delta < 0:

                            entry = c_high[a] * 1.0002
                            stoploss = c_low[a] * 0.9998
                            takeprofit = entry + risk_reward * abs(entry - stoploss)

                            risk = 10
                            stop_perc = abs(entry - stoploss) / (c_close[a-1] / 100)
                            size = (risk * 100) / stop_perc
                            fee = size * 0.0008

                            if c_high[a+1] >= entry >= c_low[a+1]:

                                for e in range(a+1, len(c_close)):

                                    if c_high[e] >= stoploss >= c_low[e]:

                                        loss = abs(entry - stoploss) / (entry / 100)
                                        loss = size * (loss / 100)

                                        result = -loss - fee
                                        result = float('{:.2f}'.format(result))
                                        # print(f"{candle_time} {symbol}, LOSS, {result} (fee {fee}) EMA {ema}")
                                        shared_queue.put([c_timestamp[a], candle_time, symbol, entry, stoploss, takeprofit, size, fee, "loss", result, fee])
                                        # print(result, end=", ")
                                        next_trade_index = e + 3
                                        break

                                    elif c_high[e] >= takeprofit >= c_low[e]:

                                        result = risk_reward * risk - fee
                                        result = float('{:.2f}'.format(result))

                                        # print(f"{candle_time} {symbol}, PROFIT, {result} (fee {fee}) EMA {ema}")
                                        shared_queue.put([c_timestamp[a], candle_time, symbol, entry, stoploss, takeprofit, size, fee, "profit", result, fee])
                                        # print(result, end=", ")
                                        next_trade_index = e + 5
                                        break

                        if direction == "Bear" and delta > 0:

                            entry = c_low[a] * 0.9998
                            stoploss = c_high[a] * 1.0002
                            takeprofit = entry - risk_reward * abs(entry - stoploss)

                            risk = 10
                            stop_perc = abs(entry - stoploss) / (c_close[a-1] / 100)
                            size = (risk * 100) / stop_perc
                            fee = size * 0.0008

                            if c_high[a+1] >= entry >= c_low[a+1]:

                                for e in range(a+1, len(c_close)):

                                    if c_high[e] >= stoploss >= c_low[e]:

                                        loss = abs(entry - stoploss) / (entry / 100)
                                        loss = size * (loss / 100)

                                        result = -loss - fee
                                        result = float('{:.2f}'.format(result))
                                        # print(f"{candle_time} {symbol}, LOSS, {result} (fee {fee}) EMA {ema}")
                                        shared_queue.put([c_timestamp[a], candle_time, symbol, entry, stoploss, takeprofit, size, fee, "loss", result, fee])
                                        # print(result, end=", ")
                                        next_trade_index = e + 3
                                        break

                                    elif c_high[e] >= takeprofit >= c_low[e]:

                                        result = risk_reward * risk - fee
                                        result = float('{:.2f}'.format(result))

                                        # print(f"{candle_time} {symbol}, PROFIT, {result} (fee {fee}) EMA {ema}")
                                        shared_queue.put([c_timestamp[a], candle_time, symbol, entry, stoploss, takeprofit, size, fee, "profit", result, fee])
                                        # print(result, end=", ")
                                        next_trade_index = e + 5
                                        break

        else:
            print("Damaged data through translating from M1 to H1")

if __name__ == '__main__':

    manager = Manager()
    shared_queue = manager.Queue()

    chunks = 16
    directory = r"D:\Binance_DATA"
    s = None
    timeframe = "1m"
    year = 2023
    # month = 11

    print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
    time1 = time.perf_counter()
    # print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs\n")

    for m in range(1, 13):

        the_processes = []

        pairs = pairs_files(chunks, directory, None, timeframe, year, m)

        for proc_number in range(chunks):
            process = Process(target=search, args=(pairs[proc_number], shared_queue,))
            the_processes.append(process)

        for pro in the_processes:
            pro.start()

        for pro in the_processes:
            pro.join()

    tests_result = []

    while not shared_queue.empty():
        data = shared_queue.get()
        tests_result.append(data)

    unique_dict = {}
    tests_result = [unique_dict.setdefault(sublist[0], sublist) for sublist in tests_result if sublist[0] not in unique_dict]

    tests_result = sorted(tests_result, key=lambda x: x[0])

    print("\nТоргівля до кінця:")

    for i in tests_result:
        print(i)

    print(f"{len(tests_result)} trades")

    fees = int(sum([inner_list[10] for inner_list in tests_result]))
    pnl = int(sum([inner_list[9] for inner_list in tests_result]))
    print(f"PNL: ${pnl} (fees: ${fees}) or ${-(pnl + fees)-fees}")

    profit_trades = len([inner_list[9] for inner_list in tests_result if inner_list[9] > 0])
    winrate = int(profit_trades / (len(tests_result) / 100))
    print(f"Winrate: {winrate}% ({profit_trades}/{len(tests_result)})")


    print("\nОбмеження втрат на день:")


    filtered_tests_result = []
    day_res = 0
    test_day = 0

    for i in tests_result:
        d = i[0]
        d = d / 1000  # Convert milliseconds to seconds
        date = datetime.utcfromtimestamp(d).strftime('%d.%m.%Y')

        if test_day != date:
            test_day = date
            day_res = i[7]
            filtered_tests_result.append(i)
            # print(i)
            # print(day_res)

        else:
            if 4 >= day_res >= -2:
                day_res += i[9]
                filtered_tests_result.append(i)
                # print(i)
                # print(day_res)

    print(f"{len(filtered_tests_result)} trades")
    fees = int(sum([inner_list[10] for inner_list in filtered_tests_result]))
    pnl = int(sum([inner_list[9] for inner_list in filtered_tests_result]))
    print(f"PNL: ${pnl} (fees: ${fees}) or ${-(pnl + fees)-fees}")

    profit_trades = len([inner_list[9] for inner_list in filtered_tests_result if inner_list[9] > 0])
    winrate = int(profit_trades / (len(filtered_tests_result) / 100))
    print(f"Winrate: {winrate}% ({profit_trades}/{len(filtered_tests_result)})")

    time2 = time.perf_counter()
    time3 = time2 - time1
    print(f"\nFinished in {int(time3)} seconds")

    plotting(tests_result, filtered_tests_result)


