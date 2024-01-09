from datetime import datetime

import matplotlib.pyplot as plt

def plotting(data):

    # Extracting the 4th column values
    results = [row[7] for row in data]
    fees = [row[8] for row in data]

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
