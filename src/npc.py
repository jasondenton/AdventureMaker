import glob
import sys
import json
import os
from monsters import get_monster, alias_monster
from advutils import format_label
from logger import log_message
from copy import deepcopy

npcs_db = {}
npcs = {}

for f in glob.glob(os.environ['ADVMAKERPATH'] + "/database/npcs.*.json"):
	try:
		with open(f,'r') as fin:
			lst = json.load(fin)
		npcs_db.update(lst)
	except Exception as ex:
		log_message("Systems Warning: Failed to load NPC database %s. Some NPCs will be unavailable." % f)

def add_npc_databases():
	global npcs_db
	for f in glob.glob("./npcs.*.json"):
		try:
			with open(f,'r') as fin:
				lst = json.load(fin)
			npcs_db.update(lst)
		except Exception as ex:
			log_message("Warning: Failed to load author NPC database %s." % f)
			log_message("    Try using https://jsonlint.com to check the format of your file.")

def get_npc_list():
	lst = []
	for tag in sorted(npcs_db.keys()):
		if tag == 'No Such Person': continue
		npc = get_npc(tag)
		if npc['sblock']: 
			npc['hasstats'] = True
		else:
			npc['hasstats'] = False
		del npc['sblock']
		del npc['label']
		npc['tag'] = tag
		lst.append(npc)
	return lst

def get_npc(key):
	global npcs_db
	global npcs
	if not key in npcs:
		if not key in npcs_db:
			log_message("NPC %s not found in database." % key)
			npcs[key] = deepcopy(npcs_db['No Such Person'])
			npcs[key]['name'] = key + ' not found'
		npcs[key] = npcs_db[key]
		npcs[key]['gender'] = npcs[key]['gender'].capitalize()
		npcs[key]['race'] = npcs[key]['race'].capitalize()
		npcs[key]['title'] = npcs[key]['title'].capitalize()
		if 'stats' not in npcs[key]: 
			npcs[key]['sblock'] = None
		else:
			if npcs[key]['stats'] != npcs[key]['name']:
				alias_monster(npcs[key]['stats'],npcs[key]['name'])
			npcs[key]['sblock'] = get_monster(npcs[key]['name'])
		npcs[key]['label'] = format_label(npcs[key]['name'])
	return npcs[key]
