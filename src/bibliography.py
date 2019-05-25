import glob
import sys
import json
import os
from logger import log_message

bibliography = {}
for f in glob.glob(os.environ['ADVMAKERPATH'] + "/database/bibliography.*.json"):
	try:
		with open(f,'r') as fin:
			lst = json.load(fin)
		bibliography.update(lst)
	except Exception as ex:
		log_message("Systems Error: Unable to load bibliographic database %s." % f)

def add_bib_databases():
	global bibliography
	for f in glob.glob("./bibliography.*.json"):
		try:
			with open(f,'r') as fin:
				lst = json.load(fin)
			bibliography.update(lst)
		except Exception as ex:
			log_message("Warning: Failed to load author bibliographic database %s." % f)
			log_message("    Try using https://jsonlint.com to check the format of your file.")

def get_citation(key):
	global bibliography
	if key in bibliography:
		bib = bibliography[key]
		if bib['site'] == 'DMsGuild' and bib['url'].find('?') == -1:
			bib['link'] = bib['url'] + '?affiliate_id=33042'
		elif bib['site'] == 'Amazon' and bib['url'].find('?') == -1:
			bib['link'] = bib['url'] + '?tag=dndadventure-20'
		else:
			bib['link'] = bib['url']
		return bib
	else:
		log_message('No such key as %s in bibliography.' % key)
		return bibliography['nosuch']

def get_library():
	global bibliography
	lst = []
	for key in bibliography:
		if key == 'nosuch': continue
		bib = bibliography[key]
		lst.append({'tag' : key,
			'title' : bib['title'],
			'author' : bib['author']})
	return lst
