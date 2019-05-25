import glob
import sys
import json
import os
from advutils import format_label
from copy import deepcopy
from logger import log_message

spell_db = {}
spells = {}

for f in glob.glob(os.environ['ADVMAKERPATH'] + "/database/spells.*.json"):
	try:
		with open(f,'r') as fin:
			lst = json.load(fin)
		spell_db.update(lst)
	except Exception as ex:
		log_message("Systems Error: Unable to load spell database.")

def add_spell_databases():
	global spells_db
	global spells
	for f in glob.glob("./spells.*.json"):
		try:
			with open(f,'r') as fin:
				lst = json.load(fin)
			spell_db.update(lst)
		except Exception as ex:
			log_message("Warning: Failed to load author spell database %s." % f)
			log_message("    Try using https://jsonlint.com to check the format of your file.")
		
def get_spell_index():
	global spells_db
	return sorted(spell_db.keys())

def get_spell(key):
	global spells_db
	global spells
	if not key in spells:
		if not key in spell_db:
			log_message("Warning: Spell %s not found." % key)
		 	spells[key] = deepcopy(spell_db['Nosuch'])
		 	spells[key]['name'] = 'Missing ' + key
		else:
			spells[key] = spell_db[key]
		spells[key]['label'] = format_label(spells[key]['name'])
		if not 'mechanism' in spells[key]: spells[key]['mechanism'] = None
		lvl = spells[key]['level']
		if lvl == 0:
			spells[key]['lvlline'] = "%s cantrip" % spells[key]['school']
		else:
			if lvl == 1:
				fx = 'st'
			elif lvl == 2:
				fx = 'nd'
			elif lvl == 3:
				fx = 'rd'
			else:
				fx = 'th'
			spells[key]['lvlline'] = "%d%s level %s" % (lvl, fx, spells[key]['school'])
	return spells[key]
		