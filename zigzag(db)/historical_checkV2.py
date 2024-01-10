import time
from datetime import datetime
from multiprocessing import Process, Manager
from module_get_pairs_from_database import pairs_files, read_csv_transposed
from result_plot import plotting
import os

'''

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

            if a < next_trade_index:
                continue

            else:
                pass
                # if c_high[a] >= max(c_high[a-5:a]):
                #
                #     for b in range(a: len(c_open) - 120)


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

