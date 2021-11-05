import requests
import json
import datetime
import time
import traceback

from config import config
from coinflex import CoinFlex
  
cf = CoinFlex(config['rest_url'], config['rest_path'], config['api_key'], config['api_secret'])

# REST API method
filename = 'coinflex_data.json'

markets = ['BCH-USD']
flex_assets = ['flexUSD']

# load endpoints.json
with open('endpoints.json', 'r') as file:
  endpoints = json.load(file)

# load data
try:
	with open(filename, 'r') as file:
	  data = json.load(file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
	data = {}

# request accountinfo and add to data
print("requesting /v2/accountinfo...")
r = cf.request('/v2/accountinfo', {})
# print("accountinfo response", r)
# print("accountinfo response.content", r.content)
# print("accountinfo response.json", json.dumps(r.json(), indent=4))
data['accountinfo'] = r.json()


t_now = int(time.time() * 1000)

#print(f"data loaded from {filename}: ", json.dumps(data, indent=2))

for name in config['endpoints_to_sync'].split(","):
	endpoint = endpoints[name]
	print("endpoint: ", endpoint)
	limit = endpoint['limit']
	time_field_name = endpoint['time_field_name']

	# determine latest_t
	latest_t = config['t_account_start']
	if name not in data:
		data[name] = {
			'latest_t': None,
			'data': []
		}
	elif len(data[name]['data']) > 0:
		print("have data...")
		if data[name]['latest_t']:
			print("have latest_t in data")
			latest_t = data[name]['latest_t']
		elif time_field_name:
			print(f"using {time_field_name} for latest_t")
			latest_t = max(int(d[time_field_name]) for d in data[name]['data'])
		print(f"latest_t now {latest_t}")

	if latest_t > t_now:
		latest_t = t_now

	print(f"endpoint {name}: latest_t={latest_t}")

	if 'items' not in endpoint:
		items = ['<all>']
	else:
		items = endpoint['items']
	for item in items:
		path = endpoint['path'].format(name=name, item=item)
		current_start_t = latest_t
		current_period = endpoint['max_period']
		print(f"working on endpoint {name}, requesting {path}")
		received_data = None
		finished = False
		while not finished:
			try:
				params = {
					'limit': limit,
					'startTime': int(current_start_t), 
					'endTime': int(current_start_t + current_period) 
				}
				# if params['endTime'] > t_now:
				# 	params['endTime'] = t_now

				# fire request
				r = cf.request(path, params)

				#print("response", r)
				if r.status_code != 200:
					print(f"status_code {r.status_code}, content: {r.content}")
					if r.status_code == 429: # rate limit hit
						time.sleep(endpoint['rate_limit_sleep_s'])
				else:
					received_json = r.json()
					if "data" not in received_json:
						print("ERROR from api, response:")
						print(json.dumps(received_json, indent=2))
					else:
						received_data = received_json["data"]
						print(f"{name}: requested {path} with {params}...")
						#print("type(received_data): ", type(received_data))

						if received_data != None:
							print(f"   received {len(received_data)}/{limit} items")

							# append data to storage
							if len(received_data) > 0:
								data[name]['data'] += received_data

							# adjust time period parameters
							if len(received_data) == limit: # limit was hit exactly
								data[name]['latest_t'] = max(int(d[time_field_name]) for d in received_data) # this is problematic, there could be more non-delivered items with same timestamp
							elif len(received_data) >= 0: # received data below limit, so endTime can be next startTime
								data[name]['latest_t'] = params['endTime']
							current_start_t = data[name]['latest_t'] + 1
							print("   new current_start_t: ", datetime.datetime.fromtimestamp(current_start_t/1000))

							if current_start_t >= t_now:
								finished = True

						else:
							print("no data received (not even empty), probably error")
							print("response.json", json.dumps(r.json(), indent=4))

			except (KeyboardInterrupt, Exception) as ex:
				print("ABORT due to", ex)
				traceback.print_exc()
				finished = True

#print(json.dumps(data, indent=1))

# trades = []
# for market in markets:
# 	r = cf.request(f'/v2/trades/{market}').json()
# 	trades += r["data"]
# print(json.dumps(trades))

#{"pageNum":1,"pageSize":10,"searchParams":{"instruments":[],"statuses":[],"startDate":"2021-07-19 22:00:00","endDate":"2021-10-19 22:00:00"}}

# method = '/v2/account/withdraw/histories'
# params = {
# 	'startDate': "2021-07-19 22:00:00",
# 	"endDate":"2021-10-19 22:00:00"
# }
# resp = cf.request(method, params)
# print (resp)
# print(resp.content.decode())

with open("coinflex_data.json", "w") as outfile:
	outfile.write(json.dumps(data, indent=1))

