from datetime import datetime, timedelta

binance_frame = '1m'

end_date_timestamp = datetime(2023, 9, 27).timestamp()
end_date = datetime.fromtimestamp(end_date_timestamp)
hours_to_add = 20
minutes_to_add = 0
time_to_add = timedelta(hours=hours_to_add, minutes=minutes_to_add)
new_date = end_date + time_to_add
end_date = new_date.timestamp() * 1000

# Convert the timestamp back to a datetime object
end_date = datetime.fromtimestamp(end_date / 1000)

print(end_date.strftime('%Y %m %d %H:%M:%S'))
