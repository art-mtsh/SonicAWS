import hmac
import hashlib
from websocket_trading import keys


# Bybit API Key and Secret
api_key = keys.BYBIT_API
api_secret = keys.BYBIT_SECRET


def auth(payload, recv_window, timestamp):
	if api_key is None or api_secret is None:
		raise PermissionError("Authenticated endpoints require keys.")
	
	param_str = str(timestamp) + api_key + str(recv_window) + payload
	hash = hmac.new(
		bytes(api_secret, "utf-8"),
		param_str.encode("utf-8"),
		hashlib.sha256,
	)
	return hash.hexdigest()
