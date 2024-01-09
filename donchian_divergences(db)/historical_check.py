import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
# from result_plot import plotting
import os

'''
Скріпт, який збирає перехаї та перелої на історії 
аби перевірити чи працює взаємнонаправлений вхід по двом інструментам в одну і ту ж хвилину, 
якщо один був з перехаєм, а інший з перелоєм.

Проблема виявилась в швидкостях - коли один інструмент вже досяг стопу, а інший ще не "розкачався" аби кудись піти.

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

        next_trade_index = 0

        donchian_length = 120

        for a in range(donchian_length+2, len(c_open)):

            candle_time = c_timestamp[a] / 1000
            candle_time = datetime.fromtimestamp(candle_time)
            candle_time = candle_time.strftime("%d.%m.%Y %H:%M:%S")

            max_gap = 0

            # ==== GAP ====
            for curr_index in range(a-donchian_length, a):
                gap = abs(c_open[curr_index] - c_close[curr_index - 1])
                gap_p = 0
                if c_open[curr_index] != 0: gap_p = gap / (c_open[curr_index] / 100)
                if gap_p > max_gap: max_gap = gap_p
            max_gap = float('{:.3f}'.format(max_gap))

            # ==== DONCHIAN RANGE ====
            d_range = max(c_high[a-donchian_length: a]) - min(c_low[a-donchian_length: a])
            d_range = d_range / (c_close[a] / 100)
            d_range = float('{:.2f}'.format(d_range))


            if c_high[a] >= max(c_high[a-donchian_length: a]) and max_gap <= 0.03 and d_range >= 2:
                # print(f"{c_timestamp[a]}, {candle_time}, {symbol}")
                shared_queue_overbougth.put([c_timestamp[a], candle_time, symbol, d_range])

            elif c_low[a] <= min(c_low[a-donchian_length: a]) and max_gap <= 0.03 and d_range >= 2:
                # print(f"{c_timestamp[a]}, {candle_time}, {symbol}")
                shared_queue_oversold.put([c_timestamp[a], candle_time, symbol, d_range])

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

    overbougth_result = []
    oversold_result = []

    while not shared_queue_overbougth.empty():
        data = shared_queue_overbougth.get()
        # print(data)
        overbougth_result.append(data)

    while not shared_queue_oversold.empty():
        data = shared_queue_oversold.get()
        # print(data)
        oversold_result.append(data)

    for first_list in overbougth_result:
        for second_list in oversold_result:
            if first_list[0] == second_list[0]:

                print(f"{first_list[1]}: {first_list[2]} ({first_list[3]}%) - {second_list[2]} ({second_list[3]}%)")



    # unique_dict = {}
    # tests_result = [unique_dict.setdefault(sublist[0], sublist) for sublist in tests_result if sublist[0] not in unique_dict]
    #
    # tests_result = sorted(tests_result, key=lambda x: x[0])
    #
    # for i in tests_result:
    #     print(i)
    #
    # print(f"{len(tests_result)} trades")
    # print(f"PNL: ${int(sum([inner_list[7] for inner_list in tests_result]))}")
    # profit_trades = len([inner_list[7] for inner_list in tests_result if inner_list[7] > 0])
    # winrate = int(profit_trades / (len(tests_result) / 100))
    # print(f"Winrate: {winrate}% ({profit_trades}/{len(tests_result)})")

        
    time2 = time.perf_counter()
    time3 = time2 - time1
    print(f"\nFinished in {int(time3)} seconds")

    # plotting(tests_result)


