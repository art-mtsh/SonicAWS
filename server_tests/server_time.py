import requests
import time

bybit_time = "https://api.bybit.com/v5/market/time"

time_now = time.time()
response = requests.get(bybit_time)

print(response.content)
print(time_now)
