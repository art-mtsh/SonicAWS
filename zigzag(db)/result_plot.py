from datetime import datetime

import matplotlib.pyplot as plt


def plotting(data1, data2):
    # Extracting the 4th column values for both groups
    results1 = [row[7] for row in data1]
    fees1 = [row[8] for row in data1]
    dates1 = [datetime.strptime(row[1], '%d.%m.%Y %H:%M:%S') for row in data1]
    cumulative_results1 = [sum(results1[:i + 1]) for i in range(len(results1))]
    cumulative_fees1 = [sum(fees1[:i + 1]) for i in range(len(fees1))]

    results2 = [row[7] for row in data2]
    fees2 = [row[8] for row in data2]
    dates2 = [datetime.strptime(row[1], '%d.%m.%Y %H:%M:%S') for row in data2]
    cumulative_results2 = [sum(results2[:i + 1]) for i in range(len(results2))]
    cumulative_fees2 = [sum(fees2[:i + 1]) for i in range(len(fees2))]

    # Creating subplots for two charts
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.15)

    # Plotting the first chart
    ax1.plot(dates1, cumulative_results1, label='Group 1 Equity')
    ax1.plot(dates1, cumulative_fees1, label='Group 1 Fees')
    ax1.set_ylabel('All trades took into account')
    ax1.legend()

    # Plotting the second chart
    ax2.plot(dates2, cumulative_results2, label='Group 2 Equity')
    ax2.plot(dates2, cumulative_fees2, label='Group 2 Fees')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Fixed loss/profit per day')
    ax2.legend()

    # Rotate x-axis labels for the second chart
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.suptitle('Equity Charts - Group 1 and Group 2')
    plt.show()


# plotting(data1)
