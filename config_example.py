config = {
	# coinflex production api server
	'rest_url': 'https://v2api.coinflex.com',
	'rest_path': 'v2api.coinflex.com',

	# local data filename
	'coinflex_data_filename': 'coinflex_data.json',

	# create an api key on coinflex.com and put it here
	'api_key': "<your api key>",
	'api_secret': "<your api secret>",

	# data will be pulled starting from this timestamp
	't_account_start': int(1609455600 * 1000), # 2021/01/01 Europe/Berlin (output of "date -d 2021-01-01 +%s")

	# list of endpoints to sync (look at endpoints.json for which ones are available)
	'endpoints_to_sync': 'mint,redeem,earned,trades,withdrawals,deposits'
}

