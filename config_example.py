config = {
	# coinflex production api server
	# 'rest_url': 'https://v2api.coinflex.com',
	# 'rest_path': 'v2api.coinflex.com',

	# opnx production api server
	'rest_url': 'https://api.opnx.com',
	'rest_path': 'api.opnx.com',

	# local data filename
	'data_filename': 'opnx_data.json',

	# create an api key on coinflex.com or opnx.com and put it here
	'api_key': "<your api key>",
	'api_secret': "<your api secret>",

	# list the assets (for mint, redeem, earned)
	'assets': [
		"FLEX"
	],

	# list markets you used (for trades)
	'markets': [
		"FLEX-USDT",
		"rvUSD-USDT"
	],

	# data will be pulled starting from this timestamp
	't_account_start': int(1680300000 * 1000), # 2023/04/01 Europe/Berlin (output of "date -d 2023-04-01 +%s")

	# list of endpoints to sync (look at endpoints.json for which ones are available)
	'endpoints_to_sync': 'mint,redeem,earned,trades,withdrawals,deposits,wallet'
}

