from datetime import datetime

now = datetime.now()
# last_hour_digit = int(now.strftime('%H'))
last_minute_digit = now.strftime('%M')
last_second_digit = now.strftime('%S')


print(int(last_minute_digit[-1]) == 5)
