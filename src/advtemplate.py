import os
from jinja2 import Environment, FileSystemLoader, Template

CURRENT_ENGINE = None

def template_filter(obj, template):
	if not CURRENT_ENGINE:
		raise Exception('No template engine registered')
	return CURRENT_ENGINE.Render(obj,template)

class TemplateEngine:
	def __init__(self, ext):
		self.template_env = Environment(loader=FileSystemLoader(os.environ['ADVMAKERPATH'] + '/advmaker_templates'))
		self.template_env.filters['usetemplate'] = template_filter
		self.extension = ext

	def register(self):
		global CURRENT_ENGINE
		CURRENT_ENGINE = self

	def Render(self, obj, template):
		tname = "%s.template.%s" % (template, self.extension)
		template = self.template_env.get_template(tname)
		return template.render(obj)
	


