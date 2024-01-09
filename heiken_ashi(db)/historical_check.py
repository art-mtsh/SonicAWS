import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
from result_plot import plotting
import os

'''
Як і зі стратегією на продовження руху по тренду визначеного ЗігЗагом,
в цій стратегії використані три зростаючі свічки Haikin Ashi, одна відкатом
і вхід на пробиття цієї свічки.

Серед фільтрів спробував:
- ATR зростаючих свічок
- ATR сигнальної
- сигнальний як inside bar
- EMA фільтр
- Donchian 60 та 30 фільтр
- BRR у сигнальної свічки, 33 та 66
- обмеження сигнальної свічки для скорочення комісії

Також спробував обмежувати втрати на день, та перепробував дуже багато варіацій з RR.

Як результат: жоден з фільтрів не вплинув значною мірою на вінрейт,
RR впливав на вінрейт, але кінцевий PNL залишався таким самим.

Висновок: стратегія нульова (PNL-FEE=0), перевороти неможливі.
'''

def search(filtered_symbols, shared_queue_overbougth, shared_queue_oversold):
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

        # ======= HEIKIN ASHI ==========
        ha_open = []
        ha_close = [(c_open[i] + c_high[i] + c_low[i] + c_close[i]) / 4 for i in range(len(c_open))]
        for i in range(0, len(c_close)):
            if i == 0:
                o = (c_open[0] + ha_close[0]) / 2
            else:
                o = (ha_open[i-1] + ha_close[i-1]) / 2
            ha_open.append(o)
        ha_high = [max(c_high[i], ha_open[i], ha_close[i]) for i in range(len(c_open))]
        ha_low = [min(c_low[i], ha_open[i], ha_close[i]) for i in range(len(c_open))]

        start = 122
        next_trade_index = 0

        for a in range(start, len(ha_open)):

            if a < next_trade_index:
                continue
            else:
                ema_period = 60
                sma = sum(c_close[a-ema_period-ema_period: a-ema_period]) / len(c_close[a-ema_period-ema_period: a-ema_period])
                ema_list = []
                for e in range(a-ema_period, a):
                    if len(ema_list) == 0:
                        ema_value = (c_close[e] * (2 / (ema_period + 1))) + sma * (1 - (2 / (ema_period + 1)))
                        ema_list.append(ema_value)
                    else:
                        ema_value = (c_close[e] * (2 / (ema_period + 1))) + ema_list[-1] * (1 - (2 / (ema_period + 1)))
                        ema_list.append(ema_value)
                ema = ema_list[-1]

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

                # last_range = abs(c_close[a-2] - c_open[a-4]) / (c_open[a-4] / 100)
                # last_range = float('{:.2f}'.format(last_range))

                signal_range = (c_high[a-1] - c_low[a-1]) / (c_high[a-1] / 100)
                signal_range = float('{:.2f}'.format(signal_range))

                atr_len = 30

                avg_atr = [c_high[a - c] - c_low[a - c] for c in range(atr_len)]
                avg_atr = sum(avg_atr) / len(avg_atr)
                atr_percent = avg_atr / (c_close[a] / 100)

                # =========== HEIKEN ASHI RISING PATTERN ============
                if ha_low[a-4] == ha_open[a-4] < ha_close[a-4] and \
                    ha_low[a-3] == ha_open[a-3] < ha_close[a-3] and \
                    ha_low[a-2] == ha_open[a-2] < ha_close[a-2] and \
                    ha_open[a-1] > ha_close[a-1]:

                    # =========== GAP AND SIGNAL RANGE FILTER ============
                    if max_gap <= 0.03 and atr_percent >= signal_range >= 0.25:

                        if True:

                            if True:


                            # =========== ATR FILTER ============
                            # На вінрейт не вплинув, тільки зменшив кількість трейдів вчетверо

                            # if (ha_high[a-4] - ha_low[a-4]) >= 1.5 * avg_atr and \
                            #     (ha_high[a-3] - ha_low[a-3]) >= 1.5 * avg_atr and \
                            #     (ha_high[a-2] - ha_low[a-2]) >= 1.5 * avg_atr:

                            # =========== SIGNAL BAR as INSIDE BAR ============
                            # if ha_high[a-2] >= ha_high[a-1] >= ha_low[a-1] >= ha_low[a-2]:
                            # Знижує вінрейт на 6% та значно зменшує к-ть трейдів

                            # =========== EMA FILTER ============
                            # if ema <= ha_low[a-4]:
                            # просто скорочує кількість трейдів

                            # =========== DONCHIAN FILTER ============
                            # if c_high[a-4] >= max(c_high[a-30:a-4]):
                            # Майже не впливає на вінрейт, але значно ріже кі-ть трейдів

                            # =========== SIGNAL BRR FILTER ============
                            # signal_brr = abs(ha_open[a-1] - ha_close[a-1]) / (abs(ha_high[a-1] - ha_low[a-1]) / 100)
                            # if signal_brr >= 0:
                            # Значно скорочує кількість трейдів

                            # =========== EVERY RISING CANDLE ATR FILTER ============
                            # if ha_high[a - 4] - ha_low[a - 4] >= 0.5 * avg_atr and \
                            #     ha_high[a - 3] - ha_low[a - 3] >= 0.5 * avg_atr and \
                            #     ha_high[a - 2] - ha_low[a - 2] >= 0.5 * avg_atr:

                                risk_reward = 1

                                entry = c_high[a-1] * 1.0002
                                stoploss = c_low[a-1] * 0.9998
                                takeprofit = entry + risk_reward * abs(entry - stoploss)

                                risk = 1
                                stop_perc = abs(entry - stoploss) / (c_close[a-1] / 100)
                                size = (risk * 100) / stop_perc
                                fee = size * 0.0008

                                if c_high[a] >= entry >= c_low[a]:

                                    for e in range(a, len(c_open)):

                                        if c_high[e] >= stoploss >= c_low[e]:

                                            loss = abs(entry - stoploss) / (entry / 100)
                                            loss = size * (loss / 100)

                                            result = -loss - fee
                                            result = float('{:.2f}'.format(result))
                                            # print(f"{candle_time} {symbol}, LOSS, {result} (fee {fee}) EMA {ema}")
                                            shared_queue_overbougth.put([c_timestamp[a], candle_time, symbol, stoploss, entry, takeprofit, "loss", result, fee])
                                            # print(result, end=", ")
                                            next_trade_index = e + 5
                                            break

                                        elif c_high[e] >= takeprofit >= c_low[e]:

                                            result = risk_reward * risk - fee
                                            result = float('{:.2f}'.format(result))

                                            # print(f"{candle_time} {symbol}, PROFIT, {result} (fee {fee}) EMA {ema}")
                                            shared_queue_overbougth.put([c_timestamp[a], candle_time, symbol, stoploss, entry, takeprofit, "profit", result, fee])
                                            # print(result, end=", ")
                                            next_trade_index = e + 5
                                            break

                                # print(f"{c_timestamp[a]}, "
                                #       f"{candle_time}, "
                                #       f"{symbol}, "
                                #       f"{ha_open[a]}, "
                                #       f"{ha_high[a]}, "
                                #       f"{ha_low[a]}, "
                                #       f"{ha_close[a]}, "
                                #       f"{last_range}%")

                # if c_high[a] >= max(c_high[a-donchian_length: a]) and max_gap <= 0.03 and d_range >= 2:
                #     # print(f"{c_timestamp[a]}, {candle_time}, {symbol}")
                #     shared_queue_overbougth.put([c_timestamp[a], candle_time, symbol, d_range])
                #
                # elif c_low[a] <= min(c_low[a-donchian_length: a]) and max_gap <= 0.03 and d_range >= 2:
                #     # print(f"{c_timestamp[a]}, {candle_time}, {symbol}")
                #     shared_queue_oversold.put([c_timestamp[a], candle_time, symbol, d_range])

                    # result = -risk - fee
                    # result = float('{:.2f}'.format(result))
                    # # print(f"{candle_time} {entry} {symbol}, {c3[2]}, STOP, {result} (fee {fee})")
                    # shared_queue_overbougth.put([c_timestamp[a], candle_time, symbol, c_low[a], c_high[b], c_low[c], "loss", result, fee])
                    # # print(result, end=", ")
                    # next_trade_index = e+1
                    # break


if __name__ == '__main__':

    manager = Manager()
    shared_queue_overbougth = manager.Queue()
    shared_queue_oversold = manager.Queue()

    chunks = 16
    directory = r"D:\Binance_DATA"
    s = None
    timeframe = "1m"
    year = 2023
    # month = 11

    print(datetime.now().strftime('%H:%M:%S.%f')[:-3])
    time1 = time.perf_counter()
    # print(f"Start search for {sum(len(inner_list) for inner_list in pairs)} pairs\n")

    for m in range(12, 13):

        the_processes = []

        pairs = pairs_files(chunks, directory, None, timeframe, year, m)

        for proc_number in range(chunks):
            process = Process(target=search, args=(pairs[proc_number], shared_queue_overbougth, shared_queue_oversold,))
            the_processes.append(process)

        for pro in the_processes:
            pro.start()

        for pro in the_processes:
            pro.join()

    tests_result = []
    # oversold_result = []

    while not shared_queue_overbougth.empty():
        data = shared_queue_overbougth.get()
        tests_result.append(data)

    # while not shared_queue_oversold.empty():
    #     data = shared_queue_oversold.get()
    #     # print(data)
    #     oversold_result.append(data)
    #
    # for first_list in overbougth_result:
    #     for second_list in oversold_result:
    #         if first_list[0] == second_list[0]:
    #
    #             print(f"{first_list[1]}: {first_list[2]} ({first_list[3]}%) - {second_list[2]} ({second_list[3]}%)")

    unique_dict = {}
    tests_result = [unique_dict.setdefault(sublist[0], sublist) for sublist in tests_result if sublist[0] not in unique_dict]

    tests_result = sorted(tests_result, key=lambda x: x[0])

    # for i in tests_result:
    #     print(i)

    print("\nТоргівля до кінця:")

    print(f"{len(tests_result)} trades")
    print(f"PNL: ${int(sum([inner_list[7] for inner_list in tests_result]))}")
    profit_trades = len([inner_list[7] for inner_list in tests_result if inner_list[7] > 0])
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
            if 6 >= day_res >= -4:
                day_res += i[7]
                filtered_tests_result.append(i)
                # print(i)
                # print(day_res)

    print(f"{len(filtered_tests_result)} trades")
    print(f"PNL: ${int(sum([inner_list[7] for inner_list in filtered_tests_result]))}")
    profit_trades = len([inner_list[7] for inner_list in filtered_tests_result if inner_list[7] > 0])
    winrate = int(profit_trades / (len(filtered_tests_result) / 100))
    print(f"Winrate: {winrate}% ({profit_trades}/{len(filtered_tests_result)})")

    time2 = time.perf_counter()
    time3 = time2 - time1
    print(f"\nFinished in {int(time3)} seconds")

    plotting(filtered_tests_result)


