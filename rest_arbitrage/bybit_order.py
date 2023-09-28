import json
import requests
import time
import bybit_prepare_payload
import bybit_auth_hash
import keys

def bybit_market_trade(symbol, side, quantity, api_key, api_secret):
	# Bybit API endpoint for creating market orders
	endpoint = "https://api.bybit.com/v5/order/create"
	
	# Create the request payload
	request_payload = {
		"category": "linear",
		"symbol": symbol,
		"side": side,
		"order_type": "Market",
		"qty": str(quantity),
		"time_in_force": "PostOnly",  # Adjust as needed
		"orderLinkId": str(time.time()),
		"reduce_only": False,  # Set to True for reduce-only orders if needed
		"close_on_trigger": False  # Set to True for TP/SL orders if needed
	}
	
	timestamp = int(time.time() * 1000)
	
	req_params = bybit_prepare_payload.prepare_payload(method=None, parameters=request_payload)
	
	signature = bybit_auth_hash.auth(payload=req_params, recv_window=5000, timestamp=timestamp, api_key=api_key, api_secret=api_secret)
	
	headers = {
		"Content-Type": "application/json",
		"X-BAPI-API-KEY": api_key,
		"X-BAPI-SIGN": signature,
		"X-BAPI-SIGN-TYPE": "2",
		"X-BAPI-TIMESTAMP": str(timestamp),
		"X-BAPI-RECV-WINDOW": str(5000),
	}
	
	# Convert the payload to JSON
	payload_json = json.dumps(request_payload)
	
	# Perform the POST request
	response = requests.post(url=endpoint, data=payload_json, headers=headers)
	
	return response.json()
