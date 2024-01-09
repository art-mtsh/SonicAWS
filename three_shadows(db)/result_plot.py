from datetime import datetime

import matplotlib.pyplot as plt

# data1 = [['29.12.2023 20:30:59', '1000RATSUSDT', 0.34327, 0.75, 0.2518165137614597],
# ['30.12.2023 00:10:59', 'HOTUSDT', 0.002655, 0.76, 0.23573333333332472],
# ['30.12.2023 02:50:59', 'BSVUSDT', 95.13, 0.86, 0.1385745454545426],
# ['30.12.2023 11:32:59', 'SSVUSDT', 27.49, 0.76, 0.24426666666666708],
# ['30.12.2023 11:53:59', 'BSVUSDT', 95.58, 0.82, 0.18259047619047544],
# ['30.12.2023 12:37:59', 'HIFIUSDT', 0.7317, 0.78, 0.22467692307691906],
# ['30.12.2023 14:19:59', 'LDOUSDT', 2.9458, 0.8, 0.19964067796610116],
# ['30.12.2023 14:42:59', 'SSVUSDT', 27.41, -1.22, 0.2192799999999969],
# ['30.12.2023 15:15:59', 'SEIUSDT', 0.5594, -1.18, 0.17881599999999587],
# ['30.12.2023 18:08:59', 'SSVUSDT', 27.89, -1.22, 0.22375999999999682],
# ['30.12.2023 18:22:59', 'SSVUSDT', 28.37, 0.77, 0.22679999999999684],
# ['30.12.2023 18:38:59', 'AUCTIONUSDT', 32.27, 0.78, 0.21526666666667124],
# ['30.12.2023 21:28:59', 'RUNEUSDT', 5.023, -1.19, 0.1911619047619056],
# ['31.12.2023 00:52:59', 'SEIUSDT', 0.605, -1.2, 0.20163333333332756],
# ['31.12.2023 02:30:59', 'QNTUSDT', 146.3, 0.75, 0.25448695652175046],
# ['31.12.2023 05:36:59', 'ONTUSDT', 0.2869, 0.84, 0.16388571428571283],
# ['31.12.2023 07:37:59', 'BANDUSDT', 2.0832, 0.79, 0.21083544303796825],
# ['31.12.2023 07:48:59', 'BANDUSDT', 2.0729, -1.23, 0.2334422535211306],
# ['31.12.2023 10:22:59', 'SEIUSDT', 0.6031, 0.76, 0.24151999999999976],
# ['31.12.2023 11:13:59', 'BANDUSDT', 2.1686, 0.81, 0.19270222222222444],
# ['31.12.2023 13:45:59', 'ARBUSDT', 1.6351, -1.21, 0.21158709677419413],
# ['31.12.2023 14:34:59', 'CHRUSDT', 0.1985, 0.82, 0.17626666666666435],
# ['31.12.2023 14:50:59', 'XVGUSDT', 0.0041, 0.75, 0.25286153846153864],
# ['31.12.2023 18:06:59', 'XVGUSDT', 0.004234, -1.13, 0.12542222222222169],
# ['31.12.2023 19:11:59', 'PERPUSDT', 1.1567, 0.83, 0.17364528301886525],
# ['31.12.2023 20:03:59', 'QTUMUSDT', 3.753, 0.81, 0.18764999999999984]]

def plotting(data):

    # Extracting the 4th column values
    results = [row[9] for row in data]
    fees = [row[10] for row in data]

    # Extracting dates from the first column and converting them to datetime objects
    dates = [datetime.strptime(row[1], '%d.%m.%Y %H:%M:%S') for row in data]

    # Calculating cumulative results
    cumulative_results = [sum(results[:i + 1]) for i in range(len(results))]
    cumulative_fees = [sum(fees[:i + 1]) for i in range(len(fees))]

    # Creating the equity chart with rotated x-axis labels and dots style
    # plt.plot(dates, cumulative_results, , label='Equity Curve')
    plt.plot(dates, cumulative_results, label='Equity')
    plt.plot(dates, cumulative_fees, label='Fees')

    plt.xlabel('Date')
    plt.ylabel('Cumulative Result')
    plt.title('Equity Chart')

    # Rotate x-axis labels
    plt.xticks(rotation=45)

    plt.legend()
    plt.show()

# plotting(data1)
