from logger import log_message
from datavisit import DataVisitor

def format_label(tag):
	lb = tag.strip()
	lb = lb.lower().replace(" ","_")
	lb = lb.replace("'","").replace('"','').replace(".","")
	return lb

def format_cash(value):
	try:
		v = float(value)
		gp = int(v)
		if float(gp) != v:
			sp = int((value - gp) * 10)
		else: sp = 0
	except:
		log_message("Expected a number for cash, instead got %s." % value)
		return " **ERROR** "
	txt = ''
	if gp > 0:
		txt = "%d gp" % gp
	if sp > 0:
		if len(txt) > 0:
			txt += ", "
		txt += "%d sp" % sp
	return txt

class StringProcessor(DataVisitor):
    def __init__(self, processor):
        DataVisitor.__init__(self)
        self.processor = processor

    def visit_string(self, value):
        return self.processor.process(value)