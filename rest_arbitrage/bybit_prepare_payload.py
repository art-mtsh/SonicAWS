import json


def prepare_payload(method, parameters):
	def cast_values():
		string_params = [
			"qty",
			"price",
			"triggerPrice",
			"takeProfit",
			"stopLoss",
		]
		integer_params = ["positionIdx"]
		for key, value in parameters.items():
			if key in string_params:
				if type(value) != str:
					parameters[key] = str(value)
			elif key in integer_params:
				if type(value) != int:
					parameters[key] = int(value)
	
	if method == "GET":
		payload = "&".join(
			[
				str(k) + "=" + str(v)
				for k, v in sorted(parameters.items())
				if v is not None
			]
		)
		return payload
	else:
		cast_values()
		return json.dumps(parameters)
