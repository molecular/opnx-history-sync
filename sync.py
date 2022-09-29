import requests
import json
import datetime
import time
import traceback
import sys

from config import config
from coinflex import CoinFlex

class History:
	def __init__(self):
		self.cf = CoinFlex(config['rest_url'], config['rest_path'], config['api_key'], config['api_secret'])
		self.data = {}
		
		# load endpoints.json
		with open('endpoints.json', 'r') as file:
			self.endpoints = json.load(file)

	def loadFromFile(self, filename):
		try:
			with open(filename, 'r') as file:
			  self.data = json.load(file)
				#print(f"data loaded from {filename}: ", json.dumps(self.data, indent=2))
		except (FileNotFoundError, json.decoder.JSONDecodeError):
			print(f"data file '{filename}' not found or not valid JSON data, starting from empty data")

	def dumpToFile(self, filename):	
		with open(filename, "w") as outfile:
			outfile.write(json.dumps(self.data, indent=1))

	# sync "accountinfo" endpoint to self.data['accountinfo']

	def sync_accountinfo(self):
		# request accountinfo and add to data
		print("requesting /v2/accountinfo...")
		r = self.cf.request('/v2/accountinfo', {})
		# print("accountinfo response", r)
		# print("accountinfo response.content", r.content)
		# print("accountinfo response.json", json.dumps(r.json(), indent=4))
		self.data['accountinfo'] = r.json()

	# sync data from enpoints given by enpoint_names to self.data 

	def sync_endpoints(self, endpoint_names):
		t_now = int(time.time() * 1000)

		for name in endpoint_names:
			endpoint = self.endpoints[name]

			self.sync_endpoint(endpoint, t_now)

	# sync data from given enpoints self.data 

	def sync_endpoint(self, endpoint, t_now):

		print(f"\n*** syncing endpoint {endpoint} ***\n")
		name = endpoint['name']
		time_field_name = endpoint['time_field_name']

		# determine latest_t
		if name not in self.data:
			self.data[name] = {
				'latest_t': None,
				'data': []
			}
		if 'latest_t' in self.data[name] and self.data[name]['latest_t']:
			latest_t = self.data[name]['latest_t']
			print(f"{name}: using latest_t {latest_t} from data")
		elif len(self.data[name]['data']) > 0 and time_field_name:
			print(f"{name}: using {time_field_name} for latest_t")
			latest_t = max(int(d[time_field_name]) for d in self.data[name]['data'])
		else:
			latest_t = config['t_account_start']

		if latest_t > t_now:
			latest_t = t_now

		if 'items_config_var' not in endpoint:
			items = ['<all>']
		else:
			items = config[endpoint['items_config_var']]
		print(f"--- endpoint '{name}': syncing items {items} ---")
		for item in items:
			self.sync_endpoint_item(endpoint, item, t_now, latest_t)

	# sync data specified by 'item' from given endpoint to self.data

	def sync_endpoint_item(self, endpoint, item, t_now, latest_t):
		name = endpoint['name']
		limit = endpoint['limit']
		path = endpoint['path'].format(name=name, item=item)
		time_field_name = endpoint['time_field_name']

		current_start_t = latest_t
		current_period = endpoint['max_period']
		print(f"\n--- syncing {name}, item {item}: latest_t = {latest_t} = {datetime.datetime.fromtimestamp(latest_t/1000)} ---\n")

		received_data = None
		finished = False
		while not finished:
			try:
				params = {
					'limit': limit,
					'startTime': int(current_start_t), 
					'endTime': int(current_start_t + current_period) 
				}
				if "params" in endpoint:
					params_to_add = endpoint['params']
					for key in params_to_add.keys():
						params[key] = params_to_add[key].format(name=name, item=item)
				if params['endTime'] > t_now:
				 	params['endTime'] = t_now

				# fire request
				print(f"requesting path {path} with params {params}")
				r = self.cf.request(path, params)

				#print("response", r)
				if r.status_code != 200:
					print(f"status_code {r.status_code}, content: {r.content}")
					if r.status_code == 429: # rate limit hit
						print(f"   rate limit encountered, sleeping {endpoint['rate_limit_sleep_s']} seconds...")
						time.sleep(endpoint['rate_limit_sleep_s'])
					else:
						raise Exception(f"HTTP Status Code {r.status_code}, aborting (will store data)")
				else:
					received_json = r.json()
					# temporary hack to get around behaviour introduced 4/15 2022 that api throws error 20001 when there is no data
					if "success" in received_json and "code" in received_json and "message" in received_json:
						print('looks like error response')
						if received_json["success"] == False and received_json["code"] == "20001" and received_json["message"] == "result not found, please check your parameters":
							print('special hack to ignore error code 20001')
							received_json["data"] = []

					if "data" not in received_json:
						print("ERROR from api, response:")
						print(json.dumps(received_json, indent=2))
					else:
						# pick out received_data
						received_data = received_json["data"]
						if endpoint["is_wallet_history"]:
							received_data = []
							for d in received_json["data"]:
								for item in d["walletHistory"]:
									item["accountId"] = d["accountId"]
									item["accountName"] = d["name"]
									received_data.append(item)
						print(f"   requested {path} with {params}...")
						#print("received_data: ", received_data)

						# work around issue A6 removing redeem operations still in progess. This can be removed when A6 is fixed by coinflex
						# NOTE: this introduces danger of missing a redeem that is still in progress in case startTime/endTime filter is on requestedAt. 
						#       In case filter is on redeemetAt it should be fine
						if name == 'redeem':
							received_data = [d for d in received_data if d["redeemedAt"] != d["requestedAt"]]

						if received_data == None:
							print("no data received (not even empty), probably error")
							print("response.json", json.dumps(r.json(), indent=4))
						else:
							print(f"   received {len(received_data)}/{limit} items")

							# adjust time interval parameters

							if len(received_data) == limit: # limit was hit exactly
								# try again with shorter period (exponential backoff)
								current_period /= 2
								print(f"limit hit, reducing current_period to {current_period} and trying again")	
								if current_period < 1:							
									sys.exit(f"current_period reduced to <1. Too many trades at that timestamp")	
								#sys.exit(f"limit hit, due to issue A5 we have to abort, consider reducing max_period in endpoints.json for endpoint named '{name}'")
								

								'''
								# latest_t is taken from received_data
								self.data[name]['latest_t'] = max(int(d[time_field_name]) for d in received_data) 
								print(f"self.data[name]['latest_t'] = {self.data[name]['latest_t']}")

								# store all items except the ones with latest timestamp
								# there could be more non-delivered items with that timestamp,... 
								for d in received_data:
									if True or int(d[time_field_name]) != self.data[name]['latest_t']:
										print(f"storing {d}")
										self.data[name]['data'].append(d) 
									else:
										print(f"skipping storage of {d}")

								# so we need to include that timestamp as startTime in next request
								current_start_t = self.data[name]['latest_t']
								'''
							elif len(received_data) >= 0: 
								current_period *= 2
								if current_period > endpoint['max_period']:
									current_period = endpoint['max_period']

								# latest_t is set to endTime of request
								# is this problematic due to possible clock difference local vs. server (TODO)?
								self.data[name]['latest_t'] = params['endTime']

								# append data to storage
								self.data[name]['data'] += received_data

								# next request can used endTime + 1 as startTime
								current_start_t = self.data[name]['latest_t'] + 1

							#print("   new current_start_t: ", datetime.datetime.fromtimestamp(current_start_t/1000))

							if current_start_t >= t_now:
								finished = True


			except (KeyboardInterrupt, Exception) as ex:
				print("ABORT due to", ex)
				traceback.print_exc()
				finished = True


# instantiate history, load data from file, sync and dump back to same file

history = History()
history.loadFromFile(config['coinflex_data_filename'])
#history.sync_accountinfo()
history.sync_endpoints(config['endpoints_to_sync'].split(","))
history.dumpToFile(config['coinflex_data_filename'])
