from datetime import datetime

timestamp = 1703865659999.0 / 1000  # Convert milliseconds to seconds
date_object = datetime.utcfromtimestamp(timestamp).strftime('%d.%m.%Y')

print(date_object)
