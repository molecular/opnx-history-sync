import requests
import hmac
import base64
import hashlib
import datetime
from urllib.parse import urlencode

class CoinFlex():

	def __init__(self, rest_url, rest_path, api_key, api_secret):
		self.rest_url = rest_url
		self.rest_path = rest_path
		self.api_key = api_key
		self.api_secret = api_secret
		self.nonce = 1

	def request(self, method, params):
		ts = datetime.datetime.utcnow().isoformat()
		# Not required for /v2/accountinfo
		body = urlencode(params)

		if body:
		    path = method + '?' + body
		else:
		    path = method

		msg_string = '{}\n{}\n{}\n{}\n{}\n{}'.format(ts, self.nonce, 'GET', self.rest_path, method, body)
		sig = base64.b64encode(hmac.new(self.api_secret.encode('utf-8'), msg_string.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')

		header = {'Content-Type': 'application/json', 'AccessKey': self.api_key,
		          'Timestamp': ts, 'Signature': sig, 'Nonce': str(self.nonce)}

		#print(f"msg_string: {msg_string}")
		#print(f"sig: {sig}")

		resp = requests.get(self.rest_url + path, headers=header)

		self.nonce += 1

		#return resp.content.decode()
		return resp
