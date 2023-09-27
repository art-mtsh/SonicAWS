d1 = {"a": 10, "b": 20, "c": 30}
d2 = {"b": 25, "c": 35, "d": 45}

common_keys = set(d1.keys()) & set(d2.keys())  # Find common keys
print(common_keys)

max_values = {}  # Dictionary to store max values for common keys

for key in common_keys:
    max_values[key] = max(d1[key], d2[key])

print(max_values)