from datetime import datetime

f = {1223: 342.32, 4431: 434.43}

f.update({3323: 312.33})

print(f)

print(f.keys())

keys = f.keys()

count = sum(value == 312.33 for value in f.values())

print(count)
print(datetime.now().strftime('%H:%M'))

f.clear()
print(f)