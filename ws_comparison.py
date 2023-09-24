# import threading
# import time
# import websocket
# import threading
# import json
# import _thread
# import websocket
# import threading
# import json
import queue

from ws_binance import SocketConnectionBinance
from ws_bybit import SocketConnectionBybit
from multiprocessing import Process, Queue

# Function to increment the shared value and update it
# def update_value(shared_value):
#     with shared_value.get_lock():
#         shared_value.value += 1
#
# # Function for further calculations using the updated value
# def calculate(shared_value):
#     with shared_value.get_lock():
#         result = shared_value.value * 2
#     return result

if __name__ == "__main__":
    # Create a shared integer value
    sv1 = Queue()
    sv2 = Queue()
    
    binance_symbol = "trbusdt"
    binance_url = f"wss://fstream.binance.com/ws/{binance_symbol}@depth5@100ms"
    
    bybit_symbol = "orderbook.1.TRBUSDT"
    bybit_url = f'wss://stream.bybit.com/v5/public/linear'

    # Create two processes, passing the shared value as an argument
    # process1 = Process(target=SocketConnectionBinance, args=(binance_url, sv1, ))
    # process2 = Process(target=SocketConnectionBybit, args=(bybit_url, [bybit_symbol], sv2, ))
    
    sv1_list = []
    sv2_list = []
    
    while not sv1.empty():
        sv1_list.append(sv1.get())
    
    while not sv2.empty():
        sv2_list.append(sv2.get())
        
    def diff():
        binance_data = SocketConnectionBinance(binance_url, sv1)
        bybit_data = SocketConnectionBybit(bybit_url, sv2)
        
        print(binance_data)
    
    while True:
        diff()
    
    # Start the processes
    # process1.start()
    # process2.start()
    #
    # # Wait for processes to finish
    # process1.join()
    # process2.join()

    # print("->>>>>>>>>>>>>>>>>>>>>Shared Value 1:", sv1)
    # print("->>>>>>>>>>>>>>>>>>>>>Shared Value 2:", sv2)