import hmac
import hashlib


def auth(payload, recv_window, timestamp, api_key, api_secret):
	if api_key is None or api_secret is None:
		raise PermissionError("Authenticated endpoints require keys.")
	
	param_str = str(timestamp) + api_key + str(recv_window) + payload
	hash = hmac.new(
		bytes(api_secret, "utf-8"),
		param_str.encode("utf-8"),
		hashlib.sha256,
	)
	return hash.hexdigest()
