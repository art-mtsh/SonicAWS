import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
from result_plot import plotting
import os

'''
Три ростучі (падаючі) свічки + одна свічка відкату, вхід на продовження руху.

Результат - мінус з будь-якого перевертання.
'''

def search(filtered_symbols, shared_queue):
    for pair_path in filtered_symbols:

        file_name = os.path.basename(pair_path)
        symbol = file_name.split('-')[0]

        data = read_csv_transposed(pair_path)

        c_open = data[1]
        c_high = data[2]
        c_low = data[3]
        c_close = data[4]
        # c_volume = data[5]
        c_timestamp = data[6]

        def candle(coordi):
            range_one = c_high[coordi] - c_low[coordi]
            per_range_one = range_one / (c_close[coordi] / 100)
            brr_one = abs(c_open[coordi] - c_close[coordi]) / (range_one / 100) if range_one != 0 else 0
            direction_one = "Bull" if c_close[coordi] > c_open[coordi] else "Bear"
            return [per_range_one, brr_one, direction_one]

        next_trade_index = 0

        for a in range(61, len(c_open) - 120):

            if a < next_trade_index:
                continue

            else:

                c1 = candle(a)
                c2 = candle(a + 1)
                c3 = candle(a + 2)
                c4 = candle(a + 3)

                gaps = [
                    abs(c_close[a] - c_open[a + 1]),
                    abs(c_close[a + 1] - c_open[a + 2]),
                    abs(c_close[a + 2] - c_open[a + 3])
                ]

                # room to the left
                room_to_the_left = 60

                # gap in atr's
                max_gap_in_atrs = 0.20
                # min range %
                min_range_in_perc = 0.10

                # swing range
                swing_range_in_atrs = 2
                # part of swing for signal
                part_of_swing_for_sig = 5

                # trade
                risk_reward = 1
                atr_len = 30
                atr_mpl = 1.5

                avg_atr = [c_high[a - c] - c_low[a - c] for c in range(atr_len)]
                avg_atr = sum(avg_atr) / len(avg_atr)
                atr_per = avg_atr / (c_close[a] / 100)

                candle_time = c_timestamp[a + 4] / 1000
                candle_time = datetime.fromtimestamp(candle_time)
                candle_time = candle_time.strftime("%d.%m.%Y %H:%M:%S")

                # === room to the left filter
                if (
                        (
                            c_high[a] >= max(c_high[a - room_to_the_left:a]) and
                            c_high[a + 1] >= max(c_high[a + 1 - room_to_the_left:a + 1]) and
                            c_high[a + 2] >= max(c_high[a + 2 - room_to_the_left:a + 2])
                        ) or
                        (
                            c_low[a] <= min(c_low[a - room_to_the_left:a]) and
                            c_low[a + 1] <= min(c_low[a + 1 - room_to_the_left:a + 1]) and
                            c_low[a + 2] <= min(c_low[a + 2 - room_to_the_left:a + 2])
                        )
                ):

                    # === same direction filter
                    if c1[2] == c2[2] == c3[2]: # and c3[2] != c4[2]: # (c_high[a + 2] >= c_high[a + 3] >= c_high[a + 3] >= c_high[a + 2] or c3[2] != c4[2]):

                        # === body/range ratio filters
                        if c1[1] >= 75 and c2[1] >= 75 and c3[1] >= 75 and c4[1] >= 0:

                            # === gaps filter
                            if max(gaps) <= max_gap_in_atrs * avg_atr:

                                # === volatility filters
                                if c4[0] >= min_range_in_perc and sum([c1[0], c2[0], c3[0]]) >= atr_per * swing_range_in_atrs:

                                    part_inside = (abs(c_high[a] - c_low[a]) + abs(c_high[a + 1] - c_low[a + 1]) + abs(c_high[a + 2] - c_low[a + 2])) / part_of_swing_for_sig

                                    # === relativity filters
                                    if c_high[a + 2] >= c_high[a + 3] >= c_low[a + 3] >= c_high[a + 2] - part_inside or \
                                        c_low[a + 2] <= c_low[a + 3] <= c_high[a + 3] <= c_low[a + 2] + part_inside:

                                        signal_part = (c_high[a+3] - c_low[a+3]) / 8
                                        signal_mid = (c_high[a+3] + c_low[a+3]) / 2

                                        entry = c_high[a+3] + signal_part if c3[2] == "Bull" else c_low[a+3] - signal_part
                                        entr_stoploss = signal_mid - atr_mpl * avg_atr if c3[2] == "Bull" else signal_mid + atr_mpl * avg_atr
                                        takeprofit = entry + risk_reward * abs(entry - entr_stoploss) if c3[2] == "Bull" else entry - risk_reward * abs(entry - entr_stoploss)

                                        # entry = c_high[a+3] if c3[2] == "Bull" else c_low[a+3]
                                        # takeprofit = c_low[a+3] if c3[2] == "Bull" else c_high[a+3]
                                        # stoploss = entry + abs(entry - takeprofit) if c3[2] == "Bull" else entry - abs(entry - takeprofit)

                                        # entry = low[a + 3] if c3[2] == "Bull" else high[a + 3]
                                        # stoploss = high[a + 3] if c3[2] == "Bull" else low[a + 3]
                                        # takeprofit = entry - abs(entry - stoploss) if c3[2] == "Bull" else entry + abs(entry - stoploss)

                                        risk = 1
                                        stop_perc = abs(entry - entr_stoploss) / (c_close[a+4] / 100)
                                        size = (risk * 100) / stop_perc
                                        fee = size * 0.0008

                                        if c_high[a+4] >= entry >= c_low[a+4]:

                                            # if c_open[a + 4] <= entry <= c_close[a + 4] or c_open[a + 4] >= entry >= c_close[a + 4]:
                                            #
                                            #     if c_high[a + 4] >= takeprofit >= c_low[a + 4]:
                                            #         result = risk_reward * risk - fee
                                            #         result = float('{:.2f}'.format(result))
                                            #         # print(f"{candle_time} {entry} {symbol}, {c3[2]}, PROFIT, {result} (fee {fee})")
                                            #         shared_queue.put([candle_time, symbol, stoploss, entry, takeprofit, "profit", result, fee])
                                            #         # print(result, end=", ")
                                            #         next_trade_index = e + 1
                                            #
                                            #
                                            #     elif c_high[a + 4] >= stoploss >= c_low[a + 4]:
                                            #         continue

                                            stoploss = entr_stoploss

                                            for e in range(a+4, len(c_open)):

                                                signal_mid = (c_high[e-1] + c_low[e-1]) / 2
                                                sl = signal_mid - atr_mpl * avg_atr if c3[2] == "Bull" else signal_mid + atr_mpl * avg_atr
                                                if c3[2] == "Bull" and sl > stoploss: stoploss = sl
                                                if c3[2] == "Bear" and sl < stoploss: stoploss = sl

                                                if c_high[e] >= stoploss >= c_low[e]:

                                                    loss = abs(entry - stoploss) / (entry / 100)
                                                    loss = size * (loss / 100)

                                                    result = -loss - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, STOP, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a + 4], candle_time, symbol, avg_atr, entr_stoploss, stoploss, entry, takeprofit, "loss", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e+1
                                                    break

                                                elif c_high[e] >= takeprofit >= c_low[e]:

                                                    result = risk_reward * risk - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, PROFIT, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a + 4], candle_time, symbol, avg_atr, entr_stoploss, stoploss, entry, takeprofit, "profit", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e+1
                                                    break

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

    for m in range(9, 13):

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

    for i in tests_result:
        print(i)

    print(f"{len(tests_result)} trades")
    print(f"PNL: ${int(sum([inner_list[9] for inner_list in tests_result]))}")
    profit_trades = len([inner_list[9] for inner_list in tests_result if inner_list[9] > 0])
    winrate = int(profit_trades / (len(tests_result) / 100))
    print(f"Winrate: {winrate}% ({profit_trades}/{len(tests_result)})")

        
    time2 = time.perf_counter()
    time3 = time2 - time1
    print(f"\nFinished in {int(time3)} seconds")

    plotting(tests_result)


