import time
from datetime import datetime, timedelta
from multiprocessing import Process
import requests
from module_get_pairs_binanceV3 import binance_pairs

ver = []

def buy_trade(dist_a, dist_b, dist_c, w):

    for a in range(dist_b + 2, request_length):

        if low[a] == min(low[a - dist_a: a + dist_a]):

            first_low = low[a]
            first_low_index = a

            for b in range(a + w, request_length):

                if high[b] == max(high[a - dist_b: b + dist_a]):

                    second_high = high[b]
                    second_high_index = b

                    a_b_range = abs(high[b] - low[a])
                    a_b_range_percent = abs(high[b] - low[a]) / (high[b] / 100)

                    if a_b_range_percent >= 0.40:

                        third_low = 100000
                        third_low_index = 100000

                        for c in range(b + w, request_length):

                            if low[c] == min(low[b: c + dist_c]) and \
                                    low[a] == min(low[a - dist_a: c + dist_c]) and \
                                    high[b] == max(high[a - dist_a: c + dist_c]) and \
                                    low[c] >= high[b] - (a_b_range / 2) and \
                                    low[c] < third_low:
                                third_low = low[c]
                                third_low_index = c

                        if third_low != 100000:

                            # print(f"{symbol}: "
                            # 	  f"first_low: {first_low} - {first_low_index}, "
                            # 	  f"second_high: {second_high} - {second_high_index}, "
                            # 	  f"third_low: {third_low} - {third_low_index}")

                            for d in range(third_low_index, request_length):
                                # print(f"{symbol} {d}")

                                if high[d] >= high[second_high_index] and low[third_low_index] == min(low[second_high_index: d]):

                                    entry = high[second_high_index]
                                    stoploss = low[third_low_index]
                                    takeprofit = high[second_high_index] + (high[second_high_index] - low[third_low_index])

                                    for e in range(d, request_length):

                                        if stoploss >= low[e]:
                                            print(f"{symbol}: "
                                                  f"first_low: {first_low} - {first_low_index}, "
                                                  f"second_high: {second_high} - {second_high_index}, "
                                                  f"third_low: {third_low} - {third_low_index}")
                                            print("--- Stopped ---\n")
                                            break

                                        elif high[e] >= takeprofit:
                                            print(f"{symbol}: "
                                                  f"first_low: {first_low} - {first_low_index}, "
                                                  f"second_high: {second_high} - {second_high_index}, "
                                                  f"third_low: {third_low} - {third_low_index}")
                                            print("--- Profit ---\n")
                                            break

                                    break
                            break
                        break
                    break
            break
