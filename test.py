
risk_dollars = 8
binance_ask = 50.440

qty_bin = 0.1
qty_byb = 0.01


qty = risk_dollars / binance_ask

format_map = {
	0.00000001: f"{qty:.8f}",
	0.0000001: f"{qty:.7f}",
	0.000001: f"{qty:.6f}",
	0.00001: f"{qty:.5f}",
	0.0001: f"{qty:.4f}",
	0.001: f"{qty:.3f}",
	0.01: f"{qty:.2f}",
	0.1: f"{qty:.1f}",
	1: str(int(qty)),
	10: str(int(qty / 10) * 10),
	100: str(int(qty / 100) * 100),
	1000: str(int(qty / 1000) * 1000),
	10000: str(int(qty / 10000) * 10000),
	100000: str(int(qty / 100000) * 100000),
}

qty_binance = format_map.get(qty_bin, "Invalid qty input")
qty_bybit = format_map.get(qty_byb, "Invalid qty input")
qty = format_map.get(max([qty_bin, qty_byb]), "Invalid qty input")

print(qty_binance)
print(qty_bybit)
print(qty)