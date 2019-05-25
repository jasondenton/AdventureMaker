import glob
import sys
import json
import os
from copy import deepcopy
from logger import log_message

items = {}
for f in glob.glob(os.environ['ADVMAKERPATH'] + "/database/items.*.json"):
	try:
		with open(f,'r') as fin:
			lst = json.load(fin)
		items.update(lst)
	except Exception as ex:
		log_message("System Error: Failure to load item database %s." % f)

def add_magicitem_databases():
	global items
	for f in glob.glob("./items.*.json"):
		try:
			with open(f,'r') as fin:
				lst = json.load(fin)
			items.update(lst)
		except Exception as ex:
			log_message("Warning: Failure to load author item database %s." % f)
			log_message("    Try using https://jsonlint.com to check the format of your file.")

def get_magicitem(key):
	global items
	if key in items:
		it = deepcopy(items[key])
		if 'need' not in it:
			it['need'] = []
		if 'attunement' not in it:
			it['attunement'] = False
		if 'rarity' not in it:
			it['rarity'] = 'Unique'
		if 'consumable' not in it:
			it['consumable'] = False
		if 'spell' not in it:
			it['spell'] = None
		return it
	else:
		log_message('Warning: No such item as %s.' % key)
		it = deepcopy(items['missing'])
		it['name'] = "Missing " + key
		return it
 
def get_item_list():
	global items
	itms = []
	for k in sorted(items.keys()):
		if k == 'default' : continue
		if k == 'missing' : continue
		nd = []
		if 'need' in items[k]: nd = items[k]['need']
		itms.append({
			'tag' : k,
			'needs' : nd,
			'name' : items[k]['name']})
	return itms



