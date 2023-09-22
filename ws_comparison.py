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
import multiprocessing

# Function to increment the shared value and update it
def update_value(shared_value):
    with shared_value.get_lock():
        shared_value.value += 1

# Function for further calculations using the updated value
def calculate(shared_value):
    with shared_value.get_lock():
        result = shared_value.value * 2
    return result

if __name__ == "__main__":
    # Create a shared integer value
    shared_val_2 = multiprocessing.Value('d', 0.0)
    shared_val_1 = multiprocessing.Value('d', 0.0)
    
    binance_symbol = "trbusdt"
    binance_url = f"wss://fstream.binance.com/ws/{binance_symbol}@depth5@100ms"
    
    bybit_symbol = "orderbook.1.TRBUSDT"
    bybit_url = f'wss://stream.bybit.com/v5/public/linear'

    # Create two processes, passing the shared value as an argument
    process1 = multiprocessing.Process(target=SocketConnectionBinance, args=(binance_url, shared_val_2,))
    process2 = multiprocessing.Process(target=SocketConnectionBybit, args=(bybit_url, [bybit_symbol], shared_val_1,))

    # Start the processes
    process1.start()
    process2.start()

    # Wait for processes to finish
    process1.join()
    process2.join()
