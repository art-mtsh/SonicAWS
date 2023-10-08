from datetime import datetime
from time import sleep

while True:
	now = datetime.now()
	last_hour_digit = int(now.strftime('%H'))
	last_minute_digit = now.strftime('%M')
	last_second_digit = now.strftime('%S')
	
	if int(last_hour_digit) % 2 != 0:
		print(False)
	else:
		print(int(last_second_digit))
	
	sleep(1)