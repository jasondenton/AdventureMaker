LOG = []

def flush_log(filename):
	with open(filename, 'w') as logfile:
		for l in LOG:
			logfile.write("%s\n" % l)

def log_message(msg):
	LOG.append(msg)