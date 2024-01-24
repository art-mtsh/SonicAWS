import os
import glob
import csv

def pairs_files(chunks, directory, symbol, timeframe, year, month):

    if symbol != None:
        pattern = os.path.join(directory, f"{symbol}\{symbol}-{timeframe}-{year}-{month:02}.csv")
        files = glob.glob(pattern)

        return [files]

    else:
        pattern = os.path.join(directory, f"*\*-{timeframe}-{year}-{month:02}.csv")
        files = glob.glob(pattern)

        # Calculate the chunk size
        chunk_size = len(files) // chunks

        # Split symbols_from_bi into chunks
        chunked_symbols = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

        return chunked_symbols


def read_csv_transposed(file_path: str):


    column_names = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "count",
        "taker_buy_volume",
        "taker_buy_quote_volume",
        "ignore"
    ]

    # Initialize a dictionary to store lists for each column
    columns = {name: [] for name in column_names}

    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)

            # Read the rows and append data to respective columns
            for row in csv_reader:
                for column_name in column_names:
                    columns[column_name].append(float(row[column_name]))

        # Convert the dictionary values to a list of lists
        result = [columns[name] for name in column_names]

        return result

    except:
        print(f"Trouble with {file_path}")


# chunks = 16
# directory = r"D:\Binance_DATA"
# s = "ZENUSDT"
# timeframe = "1m"
# year = 2023
# month = 1
#
# matching_files = pairs_files(chunks, directory, None, timeframe, year, month)
#
# for i in matching_files[2]:
#     # print(i)
#     data = read_csv_transposed(i)
#
#     file_name = os.path.basename(i)
#     symbol = file_name.split('-')[0]
#
#     c_open = data[1]
#     c_high = data[2]
#     c_low = data[3]
#     c_close = data[4]
#     c_volume = data[5]
#     c_timestamp = data[6]
#
#     print(symbol)
#     print(c_open[-1])

