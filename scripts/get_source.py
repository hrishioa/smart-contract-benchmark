import numpy as np
import json
from tqdm import tqdm
import glob
import re
import subprocess
import os
import mmap
from HTMLParser import HTMLParser
from multiprocessing import Pool


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get_contract_code(cadd):
	print "Getting source for %s" % cadd
	sourcepattern = r"style='max-height: 250px; margin-top: 5px;'>([\s\S]+?)<\/pre>"
	namepattern = r"<td>Contract Name:[\n.]<\/td>[\n.]<td>[.\n]([\s\S]+?)[\n.]<\/td>"
	bytecodepattern = r"verifiedbytecode2'>([\da-f]+?)<\/div>"
	abipattern = r"style='max-height: 200px; margin-top: 5px;'>(\[[\s\S]+?)<\/pre>"
	command = "wget -S -O - 'https://etherscan.io/address/%s#code'" % cadd
	DEVNULL = open(os.devnull, 'wb')
	wget = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=DEVNULL)
	outp = wget.stdout.read()
	outp = HTMLParser().unescape(outp)
	return (re.findall(namepattern, outp), re.findall(sourcepattern, outp), re.findall(bytecodepattern, outp), re.findall(abipattern, outp))

def check_hello(contract_code):
	greeter_str = "606060405260405161032c38038061032c833981016040528080518201919060200150505b5b33600060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908302179055505b8060016000509080519060200190828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a057805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518260005055916020019190600101906100b2565b5b5090506100fc91906100de565b808211156100f857600081815060009055506001016100de565b5090565b50505b5061021e8061010e6000396000f360606040526000357c01000000000000000000000000000000000000000000000000000000009004806341c0e1b514610044578063cfae32171461005357610042565b005b61005160048050506100ce565b005b6100606004805050610162565b60405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600302600f01f150905090810190601f1680156100c05780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b600060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141561015f57600060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b5b565b602060405190810160405280600081526020015060016000508054600181600116156101000203166002900480601f01602080910402602001604051908101604052809291908181526020018280546001816001161561010002031660029004801561020f5780601f106101e45761010080835404028352916020019161020f565b820191906000526020600020905b8154815290600101906020018083116101f257829003601f168201915b5050505050905061021b565b9056"
	return (len(contract_code) <= len(greeter_str))

def get_most_ether(max, outfname):
	get_contract_source_json(max, outfname, "https://etherscan.io/accounts/c/%d")	

def get_most_tx(max, outfname):
	get_contract_source_json(max, outfname, "https://etherscan.io/accounts/c/%d?sort=txcount&order=desc&")

def get_contract_source_json(max, outfname, template):
	contract_pattern = r">(0x[\da-f]+)<\/a>[\s\S]+?td>(\d[\s\S]+?Ether)<\/td>[\s\S]+?<td>([\d]+?)<\/td>"
	pagination_re = r"Page <b>([\d]+?)<\/b> of <b>([\d]+)<\/b><\/span>"

	max_pages = int(run_re_link(pagination_re, template % 1)[0][1])

	source_json = {}
	try:
		source_json = json.loads(open(outfname).read())
	except:
		pass

	print "Getting contract source"

	for page in tqdm(xrange(1, max_pages+1)):
		if(len(source_json) >= max): break

		contracts = run_re_link(contract_pattern, template % page)
		for contract_d in contracts:
			source = get_contract_code(contract_d[0])
			if(len(source[1]) == 0): continue
			print "Got source for %d contracts." % (len(source_json) + 1)
			# print "len(source) = %d, len(source[0]) = %d, len(source[1]) = %d" % (len(source), len(source[0]), len(source[1]))
			contract = {}
			contract['source'] = source[1][0]
			if(len(source[0]) > 0): contract['name'] = source[0][0]
			if(len(source[2]) > 0): contract['bytecode'] = source[2][0]
			if(len(source[3]) > 0): contract['abi'] = source[3][0]			
			contract['balance'] = contract_d[1]
			contract['address'] = contract_d[0]
			contract['transactions'] = contract_d[2]
			source_json[contract['address']] = contract
		with open(outfname, 'w') as of:
			of.write(json.dumps(source_json, indent=1))

	print "Writing..."

	with open(outfname, 'w') as of:
		of.write(json.dumps(source_json, indent=1))

	print "Done."

def get_average_roi(contract_add, contract_txs):
	# Format for tx_stats:
	# list of investors - along with a list of transaction values 
	#			(negative for deposits and positive for withdrawals from the contract)
	tx_stats = {}

	for txhash, tx in contract_txs.iteritems():
		if tx['sender'] == contract_add:
			if tx['recipient'] not in tx_stats:
				tx_stats[tx['recipient']] = []
			tx_stats[tx['recipient']].append(tx['price'])
		elif tx['recipient'] == contract_add:
			if tx['sender'] not in tx_stats:
				tx_stats[tx['sender']] = []
			tx_stats[tx['sender']].append(0-tx['price'])

	# sanitize - remove investors with fewer than 5 transactions
	# for others, get cumulative sum, fit to line and return gradient
	new_tx_stats = {}

	for tx, tval in (tx_stats.iteritems()):
		# print tx
		if len(tx_stats[tx]) < 5:
			# del tx_stats[tx]
			continue
		new_tx_stats[tx] = np.cumsum(tx_stats[tx])
		g = np.polyfit(np.arange(0, len(new_tx_stats[tx])),new_tx_stats[tx],1)
		new_tx_stats[tx] = g[0]

	return (np.mean(new_tx_stats.values()) if len(new_tx_stats) > 0 else 0)

def get_interesting_source(contracts):
	ctuples = []

	for contract in contracts:
		ctuples.append((len(contracts[contract][0]),contract))

	ctuples = sorted(ctuples, reverse=True)

	source_lim = 50 # arbitrary number, increase this if you have no life

	contract_source = {}

	t = tqdm(total=source_lim)
	source_found = 0

	names = []

	for c in tqdm(ctuples):
		try:
			name, source = get_contract_code(c[1])
			if(len(source) == 0):
				continue
			if len(name) != 0 and name[0] in names: continue
			if len(name) == 0:
				name = [c]
			# print name[0]
			names.append(name[0])
			contract_source[c[1]] = {}
			contract_source[c[1]]['source'] = source[0]
			contract_source[c[1]]['name'] = name[0]
			contract_source[c[1]]['len'] = c[0]
			source_found += 1
			t.update(source_found)
			print "Source found: "+str(source_found)
			if source_found > source_lim: break
		except KeyboardInterrupt:
			break

	return contract_source

def run_re_file(re_str, fn):
	size = os.stat(fn).st_size
	with open(fn, 'r') as tf:
		data = mmap.mmap(tf.fileno(), size, access=mmap.ACCESS_READ)
		return re.findall(re_str, data)

def run_re_link(re_str, link):
	tmpfile = "tmp.html"

	subprocess.call(["wget", "-O", "%s" % tmpfile, "%s" % link], stdout=open(os.devnull, 'wb'))

	res = run_re_file(re_str, tmpfile)

	os.system("rm %s" % tmpfile)

	return res

def main():
	contracts = {}
	print "Loading contract code..."
	contract_code_files = glob.glob('../contracts/contract_data/contract*.json')
	for cfile in tqdm(contract_code_files):
		contracts.update(json.loads(open(cfile).read()))

	cfiles = glob.glob('tx_data_2/*.json')

	cstats = {}

	# print "Processing contracts..."
	# for cfile in tqdm(cfiles):
	# 	cjson = json.loads(open(cfile).read())
	# # for cadd in contracts:
	# # 	cjson = json.loads(open('tx_data_2/'+cadd+'.json').read())
	# 	cadd = re.search(r"(0x[\s\S]+?)\.json", cfile).groups(0)[0]
	# 	try:
	# 		cstats[cadd] = {}
	# 		cstats[cadd]['hello_world'] = check_hello(contracts[cadd][0]+contracts[cadd][1])
	# 		cstats[cadd]['roi'] = get_average_roi(cadd, cjson)
	# 	except:
	# 		raise
	# 		print "Error in contract %s" % cadd
	# 		continue

	# print "Saving results..."
	# with open('results.json','w') as ofile:
	# 	ofile.write(json.dumps(cstats, indent=1))

	print "Getting source (this might be a long wait..)"
	source = get_interesting_source(contracts)

	with open('source.json', 'w') as of:
		of.write(json.dumps(source, indent=1))

	os.system('mkdir -p source')
	for s in source:
		with open('source/'+source[s]['name']+'_'+s+'.sol', 'w') as of:
			of.write('// Name: %s\n// Address: %s\n// Length: %d\n' % (source[s]['name'], s, source[s]['len']))
			of.write(source[s]['source'])

	print "Saved source."

	print "Completed."

# main()


# # Testing
# name_str = "0x651a7c4345210ed026cfd3b7ed851bfa497e5c74"
# j = json.loads(open('tx_data_2/'+name_str+'.json').read())
# f = get_tx_stats(name_str, j)