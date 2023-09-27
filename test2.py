d1 = {"a": 10, "b": 20, "c": 30}
d2 = {"b": 25, "c": 35, "d": 45}

if "a" in d1.keys():
    print(d1.keys())
    
d1.pop("a")

print(d1)