import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
from result_plot import plotting
import os

'''
Є свінг a-b
Є відкат b-c
Вхід на продовження руху - на пробиття b

Результат як завжди - хуйня
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

        next_trade_index = 0

        for a in range(91, len(c_open) - 120):

            candle_time = c_timestamp[a] / 1000
            candle_time = datetime.fromtimestamp(candle_time)
            candle_time = candle_time.strftime("%d.%m.%Y %H:%M:%S")

            """
            # ====== room to the left
            room_basis = 6
            # ====== additional room to the left
            room_additional = 54
            # ====== search forward
            search_forward = 20
            # ====== entry part
            s_part = 2
            # ====== risk reward
            risk_reward = 2
            # ====== swing range %
            swing_range_filter = 1
            # ====== signal BRR %
            signal_brr_filter = 66
            # ====== max gap %
            max_gap_filter = 0.03
            """

            # ====== room to the left
            room_basis = 1
            # ====== additional room to the left
            room_additional = 3
            # ====== search forward
            search_forward = 10
            # ====== entry part
            s_part = 3
            # ====== risk reward
            risk_reward = 4
            # ====== swing range %
            swing_range_filter = 0.10
            # ====== BRR %
            a_brr_filter = 0
            b_brr_filter = 75
            c_brr_filter = 0
            # ====== max gap %
            max_gap_filter = 0.03
            # ====== min signal range %
            signal_range_filter = 0.3

            if a < next_trade_index:
                continue

            else:
                # # ====  BULL ====
                if c_low[a] <= min(c_low[a - room_basis: a + room_basis + 1]):

                    for b in range(a+1, a+search_forward):

                        swing_range = (c_high[b] - c_low[a]) / (c_close[b] / 100)

                        if c_high[b] >= max(c_high[a - room_basis - room_additional: b + room_basis + 1]) and c_low[a] <= min(c_low[a: b]) and swing_range >= swing_range_filter:

                            for c in range(b+2, b+search_forward):

                                part = (c_high[b] - c_low[a]) / s_part

                                if c_low[c] <= min(c_low[b: c]) and c_high[b] >= max(c_high[b:c]) and c_low[c] >= c_high[b] - part:

                                    for d in range(c+1, c+search_forward):

                                        max_gap = 0
                                        for curr_index in range(d - 30, d):
                                            gap = abs(c_open[curr_index] - c_close[curr_index - 1])
                                            gap_p = 0
                                            if c_open[curr_index] != 0: gap_p = gap / (c_open[curr_index] / 100)
                                            if gap_p > max_gap: max_gap = gap_p
                                        max_gap = float('{:.3f}'.format(max_gap))

                                        a_brr = abs(c_open[a] - c_close[a]) / ((c_high[a] - c_low[a]) / 100) if (c_high[a] - c_low[a]) > 0 else 0
                                        b_brr = abs(c_open[b] - c_close[b]) / ((c_high[b] - c_low[b]) / 100) if (c_high[b] - c_low[b]) > 0 else 0
                                        c_brr = abs(c_open[c] - c_close[c]) / ((c_high[c] - c_low[c]) / 100) if (c_high[c] - c_low[c]) > 0 else 0

                                        signal_range = (c_high[b] - c_low[c]) / (c_high[b] / 100)

                                        # якщо вхід тригернувся - цикл буде завершено в будь-якому випадку!
                                        if c_high[d] >= c_high[b] * 1.0002 and c_low[c] <= min(c_low[c: d]) and \
                                            max_gap <= max_gap_filter and \
                                            signal_range >= signal_range_filter and \
                                            a_brr >= a_brr_filter and \
                                            b_brr >= b_brr_filter and \
                                            c_brr >= c_brr_filter:

                                            entry = c_high[b] * 1.0002
                                            stoploss = c_low[c] * 0.9998
                                            takeprofit = entry + risk_reward * abs(entry - stoploss)

                                            risk = 1
                                            stop_perc = abs(entry - stoploss) / (c_close[b] / 100)
                                            size = (risk * 100) / stop_perc
                                            fee = size * 0.0008

                                            # ось цей цикл завершить в будь-якому випадку!
                                            for e in range(d, len(c_open)):

                                                if c_low[e] <= stoploss:

                                                    result = -risk - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, STOP, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a], candle_time, symbol, c_low[a], c_high[b], c_low[c], size, fee, "loss", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e+1
                                                    break

                                                elif c_high[e] >= takeprofit:

                                                    result = risk_reward * risk - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, PROFIT, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a], candle_time, symbol, c_low[a], c_high[b], c_low[c], size, fee, "profit", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e+1
                                                    break


                # ====  BEAR ====
                if c_high[a] >= max(c_high[a - room_basis: a + room_basis + 1]):

                    for b in range(a + 1, a + search_forward):

                        swing_range = (c_high[a] - c_low[b]) / (c_close[b] / 100)
                        if c_low[b] <= min(c_low[a - room_basis - room_additional: b + room_basis + 1]) and c_high[a] >= max(c_high[a: b]) and swing_range >= swing_range_filter:

                            for c in range(b + 1, b + search_forward):

                                part = (c_high[a] - c_low[b]) / s_part
                                if c_high[c] >= max(c_high[b: c]) and c_low[b] <= min(c_low[b:c]) and c_high[c] <= c_low[b] + part:

                                    for d in range(c + 1, c + search_forward):

                                        max_gap = 0
                                        for curr_index in range(d - 30, d):

                                            gap = abs(c_open[curr_index] - c_close[curr_index - 1])
                                            gap_p = 0
                                            if c_open[curr_index] != 0: gap_p = gap / (c_open[curr_index] / 100)
                                            if gap_p > max_gap: max_gap = gap_p
                                        max_gap = float('{:.3f}'.format(max_gap))

                                        a_brr = abs(c_open[a] - c_close[a]) / ((c_high[a] - c_low[a]) / 100) if (c_high[a] - c_low[a]) > 0 else 0
                                        b_brr = abs(c_open[b] - c_close[b]) / ((c_high[b] - c_low[b]) / 100) if (c_high[b] - c_low[b]) > 0 else 0
                                        c_brr = abs(c_open[c] - c_close[c]) / ((c_high[c] - c_low[c]) / 100) if (c_high[c] - c_low[c]) > 0 else 0

                                        signal_range = (c_high[c] - c_low[b]) / (c_high[b] / 100)

                                        # якщо вхід тригернувся - цикл буде завершено в будь-якому випадку!
                                        if c_low[d] <= c_low[b] * 0.9998 and c_high[c] >= max(c_high[c: d]) and \
                                                max_gap <= max_gap_filter and \
                                                signal_range >= signal_range_filter and \
                                                a_brr >= a_brr_filter and \
                                                b_brr >= b_brr_filter and \
                                                c_brr >= c_brr_filter:

                                            entry = c_low[b] * 0.9998
                                            stoploss = c_high[c] * 1.0002
                                            takeprofit = entry - risk_reward * abs(entry - stoploss)
                                            risk = 1
                                            stop_perc = abs(entry - stoploss) / (c_close[b] / 100)
                                            size = (risk * 100) / stop_perc
                                            fee = size * 0.0008

                                            # ось цей цикл завершить в будь-якому випадку!
                                            for e in range(d, len(c_open)):

                                                if c_high[e] >= stoploss:
                                                    result = -risk - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, STOP, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a], candle_time, symbol, c_high[a], c_low[b], c_high[c], size, fee, "loss", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e + 1

                                                    break


                                                elif c_low[e] <= takeprofit:
                                                    result = risk_reward * risk - fee
                                                    result = float('{:.2f}'.format(result))
                                                    # print(f"{candle_time} {entry} {symbol}, {c3[2]}, PROFIT, {result} (fee {fee})")
                                                    shared_queue.put([c_timestamp[a], candle_time, symbol, c_high[a], c_low[b], c_high[c], size, fee, "profit", result, fee])
                                                    # print(result, end=", ")
                                                    next_trade_index = e + 1
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

    for m in [12]:

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
    print(f"PNL: ${int(sum([inner_list[9] for inner_list in tests_result]))}")
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
    print(f"PNL: ${int(sum([inner_list[9] for inner_list in filtered_tests_result]))}")
    profit_trades = len([inner_list[9] for inner_list in filtered_tests_result if inner_list[9] > 0])
    winrate = int(profit_trades / (len(filtered_tests_result) / 100))
    print(f"Winrate: {winrate}% ({profit_trades}/{len(filtered_tests_result)})")

    time2 = time.perf_counter()
    time3 = time2 - time1
    print(f"\nFinished in {int(time3)} seconds")

    plotting(tests_result, filtered_tests_result)

