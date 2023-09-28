import requests
import time

bybit_ticksize_url = "https://api.bybit.com/v5/market/time"

time_now = time.time()
response = requests.get(bybit_ticksize_url)

print(response.content)
print(time_now)


# Convert milliseconds to hh:mm:ss format
def milliseconds_to_hh_mm_ss(milliseconds):
	seconds, milliseconds = divmod(milliseconds, 1000)
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	
	return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# Provided numbers
number1 = 1695835725665
number2 = 1695835724274

# Convert and print in hh:mm:ss format
formatted_time1 = milliseconds_to_hh_mm_ss(number1)
formatted_time2 = milliseconds_to_hh_mm_ss(number2)

print("Formatted Time 1:", formatted_time1)
print("Formatted Time 2:", formatted_time2)
