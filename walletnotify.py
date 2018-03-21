#!/usr/local/bin/python3
import json
import subprocess
import sys
import requests

api_username = 'root'
api_password = 'root'

txid = sys.argv[1]
walletname = sys.argv[2]
currency = sys.argv[3]

wallet = '-rpcwallet=' + walletname
bitcoinCommand = 'gettransaction'

process = subprocess.Popen(['bitcoin-cli', wallet, bitcoinCommand, txid], stdout=subprocess.PIPE)
output, error = process.communicate()
transaction = json.loads(output)
for detail in transaction['details']:
	if detail['category'] == 'receive':
		account = detail['account']
		if not account or account == '':
			address = detail['address']
			bitcoinCommand2 = 'setaccount'
			process = subprocess.Popen(['bitcoin-cli', wallet, bitcoinCommand2, address, address], stdout=subprocess.PIPE)
			output, error = process.communicate()

userdata = {"currency" : currency, "txid" : txid}
resp = requests.post('http://127.0.0.1:8000/api/v1/wallet_notify/', auth=(api_username, api_password), data=userdata)
print(resp.json())
