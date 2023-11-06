
n = 100000002.010

decimal_places = len(str(n).split('.')[-1].rstrip('0'))

mpl = 10 ** decimal_places

nn = n * mpl

print(n)
print(decimal_places)
print(mpl)
print(nn)
print(nn % 10 == 0)