from ConfigParser import SafeConfigParser
from copy import deepcopy

def fix_input(value):
	if value.lower() in ['f', 'false', 'no', 'n']:
		return False
	if value.lower() in ['true', 't', 'yes', 'y']:
		return True
	try:
		return int(value)
	except Exception as exp: noop = None
	try: return float(value)
	except Exception as exp: noop = None
	return value

def load_configuration(filename, defaults={}):
	settings = deepcopy(defaults)
	cp = SafeConfigParser()
	cp.read(filename)
	for sec in cp.sections():
		items = cp.items(sec)
		for item in items:
			settings[sec][item[0]] = fix_input(item[1])
	print settings
	return settings
