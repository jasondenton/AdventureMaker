from patterns import PatternSubstitutions
from advtemplate import TemplateEngine
from StringIO import StringIO
from bibliography import get_citation
from npc import get_npc
from advutils import *
from datavisit import DataVisitor

class LaTeXTextProcessor(PatternSubstitutions):
	def __init__(self):
		PatternSubstitutions.__init__(self,[
			['##', '\\\\\\\\\n'], #force line break
			['!!', '\n\n'], #end paragraph
			['&', r'\&'],
			['#', r'\#'],
			#['_', r'\_'], #does latex need this?
			['%', r'\%'],
			['"', self.double_quote],
			['/b/', self.bold],
			['/i/', self.italic],
			['/l/', self.lstmarker],
			['/nl/', self.numlist],
			['/table ([clrCLR]+):([A-Za-z0-9\'\-\,\. \;]*)/', self.add_table],
			['/row/', self.table_row],
			['/col/', self.table_col],
			['/table/', self.end_table],
			['/inch/', '\\inches'],
			['--', '\\item '],
			['/noindent/', '\\\\noindent '],
			['\[\[imagehere:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.imagehere],
			['\[\[citation:\W*(\w*)\]\]', self.citation],
			['\[\[encounter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.encounter_ref],
			['\[\[storyaward:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.story_ref],
			['\[\[chapter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.chapter_ref],
			['\[\[reference:([A-Za-z0-9\'\-\,\. \;:]*)\]\]', self.add_reference],
			['\[\[appendix:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.appendix_ref],
			['\[\[label:([A-Za-z0-9\'\-\, \:\.]*)\]\]', self.add_label],
			['\[\[NPC:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.npc_ref],
			['\[\[xp:([A-Za-z0-9\'\-\,\. ]*):\W*(\d*)\]\]', self.quest_xp],
			['\[\[magicitemref:([A-Za-z0-9\- ]+)\]\]', self.magicitem_ref],
			['\[\[loot:([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*:\W*(\d*\.?\d*)\]\]', self.cash],
			['\[\[gpfirst:\W?(\d*\.?\d*):([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*\]\]', self.rev_cash],
			['\[\[noshowloot:([A-Za-z0-9\-\(\)\/\' ]+):\W*(\d*\.?\d*)\]\]', self.noop],
			['\[\[url:(.*)\]\]', self.url],
			['\[\[mundane:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.mundane],
		])
		self.dquote = 1
		self.bolding = 1
		self.italicing = 1
		self.lst = 1
		self.doc = None

	def add_table(self, matchobj):
		align = ''
		spec = matchobj.groups()[0].strip()
		for a in spec:
			if a == 'L':
				align += '>{\\raggedright\\arraybackslash}X'
			elif a == 'R':
				align += '>{\\raggedleft\\arraybackslash}X'
			elif a == 'X':
				align += 'X'
			else: align += a 
		return "\n\\begin{dndtable}{%s}{%s}\n" % (matchobj.groups()[1].strip(),align)

	def end_table(self,matchobj):
		return "\\\\ \n\\end{dndtable}\n"

	def table_col(self,matchobj):
		return " & "

	def table_row(self,matchobj):
		return "\\\\ \n"

	def echo(self, matchobj):
		return matchobj.string()

	def noop(self, matchobj):
		return ''

	def imagehere(self, matchobj):
		img = matchobj.groups()[0].strip()
		return '\\includegraphics[width=\\columnwidth]{%s}' % img

	def double_quote(self, matchobj):
		self.dquote = (self.dquote + 1) % 2
		return ['``', "''"][self.dquote]

	def bold(self, matchobj):
		self.bolding = (self.bolding + 1) % 2
		return ['\\textbf{', "}"][self.bolding]

	def lstmarker(self,matchobj):
		self.lst = (self.lst + 1) % 2
		return ['\\begin{dnditemize}\n','\\end{dnditemize}\n'][self.lst]

	def numlist(self,matchobj):
		self.lst = (self.lst + 1) % 2
		return ['\\begin{dndenumerate}\n','\\end{dndenumerate}\n'][self.lst]

	def italic(self, matchobj):
		self.italicing = (self.italicing + 1) % 2
		return ['\\textit{', "}"][self.italicing]

	def citation(self, matchobj):
		b = get_citation(matchobj.groups()[0].strip())
		if not b.get('link',False): return b['title']
		return "\\textit{\\href{%s}{%s}}" % (b['link'], b['title'])

	def url(self, matchobj):
		uri = matchobj.groups()[0].strip()
		return "\\url{%s}" % uri

	def encounter_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[enc_%s]{%s}" % (lb, name)

	def magicitem_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[magicitem_%s]{%s}" % (lb, name)

	def chapter_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[chapter_%s]{%s}" % (lb, name)	

	def appendix_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[appendix_%s]{%s}" % (lb, name)

	def quest_xp(self, matchobj):
		return ''

	def story_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[story_%s]{%s}" % (lb, name)

	def add_label(self, matchobj):
		lb = format_label(matchobj.groups()[0].strip())		
		return "\\label{lb_%s} " % lb

	def add_reference(self, matchobj):	
		name = matchobj.groups()[0].strip()
		lb = format_label(name)
		return "\\hyperref[lb_%s]{%s}" % (lb, name)

	def cash(self, matchobj):
		pieces = matchobj.groups()
		return "%s %s %s" % (pieces[0],pieces[1],format_cash(pieces[2]))

	def rev_cash(self, matchobj):
		pieces = matchobj.groups()
		return "%s %s %s" % (format_cash(pieces[0]),pieces[1],pieces[2])

	def npc_ref(self, matchobj):
		name = matchobj.groups()[0].strip()
		npc = get_npc(name)
		return "\\hyperref[npc_%s]{%s}" % (npc['label'], npc['name'])

	def mundane(self, matchobj):
		return matchobj.groups()[0].strip()

class LaTeXTemplateEngine(TemplateEngine):
	def __init__(self):
		TemplateEngine.__init__(self, 'tex')
		self.template_env.block_start_string = '/$'
		self.template_env.block_end_string = '$/'
		self.template_env.variable_start_string = '/@'
		self.template_env.variable_end_string = '@/'
		self.template_env.trim_blocks = True
		self.template_env.lstrip_blocks = True

class LaTeXTextFormatter(StringIO):
	def __init__(self):
		StringIO.__init__(self)

	def paragraph(self,txt):
		self.write(txt['text'])
		self.write("\n\n")

	def heading(self,node, notoc):
		txt = node['text']
		star = '*' if notoc else ''
		if node['depth'] == 2:
			hd = '\n\\section%s{%s}' % (star,txt)
		elif node['depth'] == 3:
			hd = '\n\\subsection%s{%s}' % (star,txt)
		elif node['depth'] == 4:
			hd = '\n\\subsubsection%s{%s}' % (star,txt)
		self.write(hd)
		self.write('\n\n')

	def start_txttype(self, node):
		if node['txttype'] == 1:
			tp = '\n\\begin{boxtext}\n'
		elif node['txttype'] == 2:
			tp = '\n\\begin{sidebar}'
			if node['header']:
				tp += '[title=\\large\\textbf{%s}]' % node['header']
			self.write('\n\\indent')
		self.write(tp)
		self.write('\n')

	def end_txttype(self,node):
		if node['txttype'] == 1:
			tp = '\\end{boxtext}'
		elif node['txttype'] == 2:
			tp = '\\end{sidebar}'
		self.write(tp)
		self.write('\n')

	def format_table(self, node):
		table = node['table']
		align = ''
		for i in range(0,len(table['alignment'])):
			if i == table['longestcol']:
				if table['alignment'][i][0] == 'l':
					align += '>{\\raggedright\\arraybackslash}X'
				elif table['alignment'][i][0] == 'r':
					align += '>{\\raggedleft\\arraybackslash}X'
				else:
					align += 'X'
			else:
				align += table['alignment'][i][0]
		if table['wide']:
			self.write("\\begin{widedndtable}{%s}{%s}\n" % (table['name'],align))
		else:
			self.write("\\begin{dndtable}{%s}{%s}\n" % (table['name'],align))
		self.write(" & ".join(['\\multicolumn{1}{c}{\\textbf{%s}}' % h for h in table['header']]))
		self.write("\\\\ \n")
		cidx = 0
		for l in table['table']:
			self.write(" & ".join(l))
			self.write("\\\\ \n")
		if table['wide']:
			self.write("\\end{widedndtable}\n")
		else:
			self.write("\\end{dndtable}\n")

	def format_list(self, node):
		typ = ['dnditemize', 'dndenumerate'][node['btyp']]
		self.write("\\begin{%s}\n" % typ)
		for p in node['bullets']:
			self.write("\\item %s\n" % p)
		self.write("\\end{%s}\n\n" % typ)

	def format(self, nodes, notoc = False):
		for node in nodes:
			cat = node['category']
			if cat == 'paragraph':
				self.paragraph(node)
			elif cat == 'header':
				self.heading(node,notoc)
			elif cat == 'txttype_begin':
				self.start_txttype(node)
			elif cat == 'txttype_end':
				self.end_txttype(node)
			elif cat == 'table': 
				self.format_table(node)
			elif cat == 'bulletlist':
				self.format_list(node)
			elif cat == 'spellhere':
				self.format_spell(node)
		txt = self.getvalue()
		self.truncate(0)
		return txt

class LaTeXCleaner(DataVisitor):
	def __init__(self,formatter):
		self.formatter = formatter
		self.notoc = False
		self.skiplist = []
		self.translate = {
			'text' : 'body',
			'text2' : 'body2'}

	def visit_dict(self, value):
		d = {}
		for k in value.keys():
			if k in self.skiplist:
				d[k] = value[k]
				continue
			if k in self.translate:
				d[self.translate[k]] = self.formatter.format(value[k], self.notoc)
			else: d[k] = self.run(value[k])
		return d		

class LaTeXOutputEngine:
	def __init__(self, fout, story, item):
		self.fout = fout
		self.engine = LaTeXTemplateEngine()
		self.formatter = LaTeXTextFormatter()
		self.processor = LaTeXTextProcessor()
		self.engine.register()
		self.stout = story
		self.itemout = item

	def format(self, input):
		sp = StringProcessor(self.processor)
		doc = sp.run(input)
		cleaner = LaTeXCleaner(self.formatter)
		cleaner.skiplist = ['splices']
		doc = cleaner.run(doc)
		cleaner.notoc = True
		doc['splices'] = cleaner.run(doc['splices'])

		self.fout.write(self.engine.Render(doc, doc['intvars']['template']))

		if doc['intvars']['has_story_awards']:
			self.stout.write(self.engine.Render(doc,'storycert'))

		if doc['intvars']['has_itemcerts']:
			self.itemout.write(self.engine.Render(doc,'itemcerts'))

	def create_monster_manual(self):
		from monsters import get_monster_manual
		mm = get_monster_manual()
		context = {'monsters' : [self.clean_statblock(m) for m in mm]}
		txt = self.engine.Render(context,"monster_manual")
		with open('mm.tex','w') as fout:
			fout.write(txt)
