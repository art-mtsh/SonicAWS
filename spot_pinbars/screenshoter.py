import telebot
import matplotlib.pyplot as plt
from os import remove
# import requests

# --- TELEGRAM ---
TELEGRAM_TOKEN = '6077915522:AAFuMUVPhw-cEaX4gCuPOa-chVwwMTpsUz8'
bot1 = telebot.TeleBot(TELEGRAM_TOKEN)


def screenshoter_send(symbol, cOpen: list, cHigh: list, cLow: list, cClose: list, chart_title):
    # Create a Matplotlib figure for the candlestick chart
    fig, ax = plt.subplots()
    fig.set_facecolor("#F0F0F0")
    ax.set_facecolor("#E6E1BE")
    

    for i in range(len(cClose)):
        body_up = cClose[i] - cOpen[i] if cClose[i] != cOpen[i] else cOpen[i] * 0.0001
        body_dn = cOpen[i] - cClose[i] if cClose[i] != cOpen[i] else cClose[i] * 0.0001
        
        if cClose[i] >= cOpen[i]:
            # Up candles
            plt.bar(x=i, height=body_up, width=0.9, bottom=cOpen[i], color='#008080')
            plt.bar(x=i, height=cHigh[i] - cClose[i], width=0.07, bottom=cClose[i], color='#008080')
            plt.bar(x=i, height=cOpen[i] - cLow[i], width=0.07, bottom=cLow[i], color='#008080')
        else:
            # Down candles
            plt.bar(x=i, height=body_dn, width=0.9, bottom=cClose[i], color='#696969')
            plt.bar(x=i, height=cHigh[i] - cOpen[i], width=0.07, bottom=cOpen[i], color='#696969')
            plt.bar(x=i, height=cClose[i] - cLow[i], width=0.07, bottom=cLow[i], color='#696969')
            
        # grid
        plt.grid(color='grey', linestyle='-', linewidth=0.1)

    # Customize the chart title
    plt.suptitle(chart_title)

    # Show the plot
    # plt.show()
    
    # SAVE AND SEND
    plt.savefig(f'FT{symbol}_{cOpen[-1]}_{cClose[-1]}.png', dpi=400, bbox_inches='tight', pad_inches=0.2)
    pic = open(f'FT{symbol}_{cOpen[-1]}_{cClose[-1]}.png', 'rb')
    bot1.send_photo(662482931, pic)

    # CLEANING
    pic.close()
    remove(f'FT{symbol}_{cOpen[-1]}_{cClose[-1]}.png')
    plt.cla()
    plt.clf()

    # print("Screenshoter work is done.")

# symbol = "BTCUSDT"
# timeinterval = "5m"
# distancetoSR = 10  # Replace with your desired value
# direction = "UP"  # Replace with your desired direction
#
# request_limit_length = 48
#
# futures_klines = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeinterval}&limit={request_limit_length}'
# klines = requests.get(futures_klines)
#
# if klines.status_code == 200:
#     response_length = len(klines.json()) if klines.json() is not None else 0
#     if response_length == request_limit_length:
#         binance_candle_data = klines.json()
#         cOpen = [float(entry[1]) for entry in binance_candle_data]
#         cHigh = [float(entry[2]) for entry in binance_candle_data]
#         cLow = [float(entry[3]) for entry in binance_candle_data]
#         cClose = [float(entry[4]) for entry in binance_candle_data]
#
#         screenshoter_send(symbol, cOpen, cHigh, cLow, cClose, chart_title="btc\nparameters1\nparameters2\nparameters3")
