import os
import glob
import csv

def find_files_by_date(chunks, directory, symbol, timeframe, year, month):

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

chunks = 16
directory = r"D:\Binance_DATA"
s = "ZENUSDT"
timeframe = "1m"
year = 2023
month = 1

matching_files = find_files_by_date(chunks, directory, None, timeframe, year, month)


# # print(matching_files)
# for i in matching_files:
#     print(i)
#     print(len(i))

# def read_csv_transposed(file_path, column_names):
#     # Initialize a dictionary to store lists for each column
#     columns = {name: [] for name in column_names}
#
#     with open(file_path, 'r') as file:
#         csv_reader = csv.DictReader(file)
#
#         # Read the rows and append data to respective columns
#         for row in csv_reader:
#             for column_name in column_names:
#                 columns[column_name].append(row[column_name])
#
#     # Convert the dictionary values to a list of lists
#     result = [columns[name] for name in column_names]
#
#     return result
#
# # Example usage
# directory = r"D:\Binance_DATA"
# symbol = "ZENUSDT"
# timeframe = "1m"
# year = 2023
# month = 1
#
#
#
#
# if matching_files:
#     print("Matching files:")
#     for file_path in matching_files:
#
#         column_indexes = [
#             "open_time",
#             "open",
#             "high",
#             "low",
#             "close",
#             "volume",
#             "close_time",
#             "quote_volume",
#             "count",
#             "taker_buy_volume",
#             "taker_buy_quote_volume",
#             "ignore"
#         ]
#
#         # Get CSV data as a list of lists without column names
#         result = read_csv_transposed(file_path, column_indexes)
#
#         # Display the result
#         for column_data in result:
#             print(column_data[0: 20])
#
# else:
#     print("No matching files found.")
