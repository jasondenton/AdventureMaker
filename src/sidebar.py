import glob
import sys
import json
import os
from logger import log_message
from copy import deepcopy

sidebars = {}
for f in glob.glob(os.environ['ADVMAKERPATH'] + "/database/sidebars.*.json"):
	try:
		with open(f,'r') as fin:
			lst = json.load(fin)
		sidebars.update(lst)
	except Exception as ex:
		log_message("System Error: Error loading standard sidebars from file %s" % f)

def add_sidebar_databases():
	global sidebars
	for f in glob.glob("./sidebars.*.json"):
		try:
			with open(f,'r') as fin:
				lst = json.load(fin)
			sidebars.update(lst)
		except Exception as ex:
			log_message("Warning: Unable to load author sidebar file %s" % f)
			log_message("    Try using https://jsonlint.com to check the format of your file.")

def get_sidebar(key):
	global sidebars
	if key in sidebars:
		return sidebars[key]
	else:
		log_message("Warning: Sidebar %s not found." % key)
		tmp = deepcopy(sidebars['Missing Sidebar'])
		tmp['title'] = key
		return tmp

def get_sidebar_list():
	lst = []
	for k in sorted(sidebars.keys()):
		if k == 'Missing Sidebar': continue
		lst.append(k)
	return lst

