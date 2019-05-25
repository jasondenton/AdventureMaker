from patterns import PatternSubstitutions
from advtemplate import TemplateEngine
from advutils import format_label, format_cash
from bibliography import get_citation
from logger import log_message
from advutils import StringProcessor
from datavisit import DataVisitor

FG_PAGE_COUNT = 0
PAGE_INDEX = {}
IMAGES = []

class FantasyGroundsMarkupProcessor(PatternSubstitutions):
	def __init__(self):
		PatternSubstitutions.__init__(self,[
			['##', '</p><p>'], #force line break
			['!!', '</p><p>'], #end paragraph
			['&', r'&amp;'],
			['"', '&quot;'],
			['/inch/', '&#34;'],
			['/b/', self.bold],
			['/i/', self.italic],
			['/l/', self.add_list],
			['/nl/', self.numlist],
			['/table ([clrCLR]+):([A-Za-z0-9\'\-\,\. \;:]*)+/', self.add_table],
			['/row/', self.table_row],
			['/col/', self.table_col],
			['/table/', self.end_table],
			['--', self.bullet],
			['/noindent/', self.noop],
			['\[\[citation:\W*(\w*)\]\]', self.citation],	
			['\[\[NPC:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.echo],
			['\[\[xp:([A-Za-z0-9\'\-\,\. ]*)*:\W*(\d*)\]\]', self.noop],
			['\[\[magicitemref:([A-Za-z0-9\- ]+)\]\]', self.echo],
			['\[\[loot:([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*:\W*(\d*)\]\]', self.cash],
			['\[\[gpfirst:\W?(\d*\.?\d*):([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*\]\]', self.rev_cash],
			['\[\[noshowloot:([A-Za-z0-9\-\(\)\/\' ]+):\W*(\d*)\]\]', self.noop],
			['\[\[url:(.*)\]\]', self.echo],
			['\[\[mundane:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.mundane]
		])
		self.dquote = 1
		self.bolding = 1
		self.italicing = 1
		self.list = 1
		self.item = False

	def cash(self, matchobj):
		pieces = matchobj.groups()
		return "%s %s %s" % (pieces[0],pieces[1],format_cash(pieces[2]))

	def rev_cash(self, matchobj):
		pieces = matchobj.groups()
		return "%s %s %s" % (format_cash(pieces[0]),pieces[1],pieces[2])

	def mundane(self, matchobj):
		print matchobj.groups[0]
		return matchobj.groups()[0].strip()

	def add_table(self, matchobj):
		return "<b>%s</b><table>\n<tr>\n<td>" % matchobj.groups()[1].strip()

	def end_table(self, matchobj):
		return "</td></tr>\n</table>"

	def table_row(self, matchobj):
		return "</td></tr>\n"

	def table_col(self, matchobj):
		return "</td>\n"

	def add_list(self,matchobj):
		self.list = (self.list + 1) % 2
		if self.list: self.item = False
		return ['<ul>','</li></ul>'][self.list]

	def numlist(self,matchobj):
		self.list = (self.list + 1) % 2
		if self.list: self.item = False
		return ['<ol>','</li></ol>'][self.list]

	def bullet(self,matchobj):
		if self.item:
			return '</li><li> '
		else :
			self.item = True
			return '<li>'

	def citation(self, matchobj):
		b = get_citation(matchobj.groups()[0].strip())
		return b['title']

	def label(self, matchobj):
		tag = matchobj.groups()[0].strip()
		self.page.add_tag(tag)
		return ''

	def appendix(self, matchobj):
		tag = matchobj.groups()[0].strip()
		#self.page.add_symbolic_link('Appendix: ' + tag)
		return tag

	def storyaward(self, matchobj):
		tag = matchobj.groups()[0].strip()
		#self.page.add_symbolic_link('Story Award: ' + tag)
		return tag

	def noop(self, *args):
		return None

	def bold(self, matchobj):
		self.bolding = (self.bolding + 1 ) % 2
		return ['<b>', '</b>'][self.bolding]

	def italic(self, matchobj):
		self.italicing = (self.italicing + 1 ) % 2
		return ['<i>', '</i>'][self.italicing]

	def echo(self, matchobj):
		return matchobj.groups()[0].strip()

	def loot(self, matchobj):
		g = matchobj.groups()
		return "{0} {1} {2} ".format(g[0].strip(),g[1].strip(),format_cash(g[2].strip()))


class FantasyGroundsTextProcessor(PatternSubstitutions):
	def __init__(self):
		PatternSubstitutions.__init__(self,[
			['\[\[chapter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.reference],
			['\[\[imagehere:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.imagehere],
			['\[\[encounter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.encounter],
			['\[\[reference:([A-Za-z0-9\'\-\,\. \;:]*)\]\]', self.reference],
			['\[\[storyaward:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.storyaward],
			['\[\[label:([A-Za-z0-9\'\-\, \:\.]*)\]\]', self.label],
			['\[\[appendix:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.appendix]
		])
		self.page = None 

	def imagehere(self, matchobj):
		img = matchobj.groups()[0].strip()
		self.page.add_image(img)

	def label(self, matchobj):
		tag = matchobj.groups()[0].strip()
		self.page.add_tag(tag)
		return ''

	def appendix(self, matchobj):
		tag = matchobj.groups()[0].strip()
		#self.page.add_symbolic_link('Appendix: ' + tag)
		return tag

	def storyaward(self, matchobj):
		tag = matchobj.groups()[0].strip()
		#self.page.add_symbolic_link('Story Award: ' + tag)
		return tag

	def encounter(self, matchobj):
		tag = matchobj.groups()[0].strip()
		self.page.add_symbolic_link('Encounter: ' + tag)
		return tag

	def reference(self, matchobj):
		tag = matchobj.groups()[0].strip()
		self.page.add_symbolic_link(tag)
		return tag

class FantasyGroundsMonsterLib:
	def __init__(self, doc, processor):
		self.processor = processor
		self.total_monsters = 0
		self.monsters = []
		self.monsteridx = {}
		for chp in doc['chapters']:
			for enc in chp['encounters']:
				for s in enc['stat_blocks']:
					self.add_monster(s)
		for n in doc['npcs']:
			blk = n.get('sblock',None)
			if blk: self.add_monster(blk)
		for m in doc['extra_monsters']:
			self.add_monster(m)


	def add_monster(self,block):
		n = block['name']
		if n in self.monsteridx: return
		self.total_monsters += 1
		block['token'] = n[0]
		block['mid'] = self.total_monsters
		self.monsteridx[n] = block['mid']
		self.monsters.append(block)

	def get_monster_id(self, n):
		if not n in self.monsteridx:
			log_message("Error: missing monster %s when building fantasy grounds module." % n)
			return 0
		return self.monsteridx[n]

	def content(self):
		return self.monsters

class FantasyGroundsPage:
	def __init__(self, name):
		global FG_PAGE_COUNT
		global PAGE_INDEX
		FG_PAGE_COUNT += 1
		PAGE_INDEX[name[6:]] = FG_PAGE_COUNT
		self.pageid = FG_PAGE_COUNT
		self.name = name.strip()
		self.text = ''
		self.ptype = 0
		self.nextpage = None
		self.prevpage = None
		self.links = []
		self.prelinks = []
		self.tbd = []
		self.tags = []
		self.ongoing = False

	def content(self):
		refs = []
		for tag in self.tbd:
			if not tag in self.tags:
				if not tag in PAGE_INDEX: 
					log_message("Error: Reference to unknown fantasy grounds page: %s." % tag)
				self.tags.append(tag)
				refs.append({'text':tag,'id': PAGE_INDEX[tag]})

		return {
			'name' : self.name,
			'id' : self.pageid,
			'text' : self.text,
			'next' : self.nextpage,
			'prev' : self.prevpage,
			'links' : self.links,
			'prelinks' : self.prelinks,
			'references' : refs
		}

	def add_image(self, img):
		global IMAGES
		idx = len(IMAGES) + 1
		nm = 'Image %d' % idx
		IMAGES.append({'name':nm, 'filename':img, 'id' : idx, 'needgrid' : False})
		self.add_link(nm, 'image', idx)

	def end_page(self):
		if self.ongoing:
			self.text += "</frame>"

	def add_symbolic_link(self, tag):
		self.tbd.append(tag)

	def add_tag(self,tag):
		global PAGE_INDEX
		PAGE_INDEX[tag] = self.pageid
		self.tags.append(tag)

	def toggle_frame(self):
		self.ptype = self.ptype ^ 1
		if self.ongoing:
			self.text += "</frame>"
		self.ongoing = False

	def add_paragraph(self, para):
		if self.ptype == 0:
			self.text += "<p>%s</p>" % para.strip()
		elif self.ongoing:
			self.text += "&#13;&#13;"
			self.text += para.strip()
		else:
			self.ongoing = True
			self.text += "<frame>%s" % para.strip()

	def add_header(self, h):
		self.text = self.text + "<h>{0}</h>\n".format(h)

	def next(self, pageid):
		self.nextpage = pageid

	def prev(self, pageid):
		self.prevpage = pageid


	def add_link(self, text, typ, pid, pre=False, prepend=False):
		if typ == 'image':
			rtype = 'image'
			typ = 'imagewindow'
		else:
			rtype = typ
		entry = {
			'text' : text,
			'type' : typ,
			'recordtype' : rtype,
			'id' : pid 
		}

		if pre:
			tl = self.prelinks
		else:
			tl = self.links

		if prepend:
			tl.insert(0,entry)
		else:
			tl.append(entry)

	def add_table(self, table):
		self.text += "<table>\n<tr>"
		for h in table['header']:
			self.text += "<td><b>%s</b></td>\n" % h
		self.text += "</tr>"
		for row in table['table']:
			self.text += "<tr>\n"
			for col in row:
				self.text += "<td>%s</td>" % col
			self.text += "</tr>"
		self.text += "</table>\n"

class FantasyGroundsTreasurePage(FantasyGroundsPage):
	def __init__(self, itm):
		FantasyGroundsPage.__init__(self, itm['name'])


class FantasyGroundsTemplateEngine(TemplateEngine):
	def __init__(self):
		TemplateEngine.__init__(self, 'xml')
		self.template_env.trim_blocks = True
		self.template_env.lstrip_blocks = True

class MonsterFix(DataVisitor):
	def visit_string(self,value):
		value = value.replace('<i>','')
		value = value.replace('</i>','')
		return value.replace('</p><p>','\\n')

class FantasyGroundsOutputEngine:
	def __init__(self, dbstream, descstream):
		self.engine = FantasyGroundsTemplateEngine()
		self.engine.register()
		self.processor = FantasyGroundsTextProcessor()
		self.markup = FantasyGroundsMarkupProcessor()
		self.pages = []
		self.pstack = []
		self.chapter = None
		self.battles = []
		self.total_battles = 0
		self.in_section = False
		self.treasure = []
		self.founditems = []
		self.story_pages = []
		self.app_pages = []
		self.storyaward_pages = []
		self.dbstream = dbstream
		self.descstream = descstream
		self.chapter_count = 0
		self.section_count = 0
		self.sidebar_count = 0
		self.enc_count = 0

	def appendix_pages(self,doc):
		global IMAGES
		summary = self.new_page('9100. Appendix A: Adventure Summary')
		summary.add_tag('Appendix A: Adventure Summary')
		self.app_pages.append(summary)
		txt = self.engine.Render(doc, 'summarypage')
		summary.text += txt
		final_splices = ['noteable_items', 'advleague_rewards']
		kys = doc['splices'].keys()
		slist = [k for k in kys if k in final_splices]
		for splice in slist:
			for node in doc['splices'][splice]['text']:
				self.txt2page(node)
		self.finish_page()	
		npc = self.new_page('9200. Appendix B: Important NPCs')
		npc.add_tag('Appendix B: Important NPCs')
		for n in doc['npcs']:
			npc.text += "<h>{0}</h><p><i>{1} {2}, {3}.</i></p>".format(n['name'],n['race'],n['gender'],n['title'])
			self.txt2page(
					{
					'category' : 'paragraph',
					'text' : n['description']
					}) 
			sb = n.get('sblock',None)
			if sb: npc.add_link(sb['name'], 'npc', get_monster_id(sb['name']))
		self.finish_page()
		self.app_pages.append(npc)
		for a in doc['appendix']:
			i = len(IMAGES) + 1
			IMAGES.append({'name':a['name'], 'filename':a['image'], 'id' : i})
		staw_counter = 9110
		for staw in doc['storyawards']:
			sp = self.new_page(str(staw_counter) + '. Story Award: ' + staw['name'])
			for node in staw['text2']:
				self.txt2page(node)
			sp.toggle_frame()
			for node in staw['text']:
				self.txt2page(node)
			summary.add_link('Story Award: ' + staw['name'], 'encounter', sp.pageid)
			self.finish_page()
			self.storyaward_pages.append(sp)
			staw_counter += 10

	def add_section(self, node):
		self.section_count += 1
		if self.in_section: self.finish_page()
		self.in_section = True
		prefix = 1000 + self.chapter_count * 100 + self.section_count 
		pg = self.new_page(str(prefix) + '. ' + node['text'])
		self.chapter.add_link(node['text'], 'encounter', pg.pageid)
		self.pstack[-1].prev(self.prevpage.pageid)
		self.prevpage.next(self.pstack[-1].pageid)
		self.prevpage = self.pstack[-1]

	def add_magicitem(self, item):
		pg = FantasyGroundsTreasurePage(item)
		self.pstack.append(pg)
		self.processor.page = pg
		for node in item['text']:
			self.txt2page(node)
		prev = self.pstack.pop()
		self.processor.page = prev
		ct = pg.content()

		uip = FantasyGroundsTreasurePage(item)
		self.pstack.append(uip)
		self.processor.page = uip
		for node in item['text2']:
			self.txt2page(node)
		prev = self.pstack.pop()
		self.processor.page = prev
		ui = uip.content()

		if 'fg_type' not in item:
			item['fg_type'] = item['category']
		item['body'] = ct['text']
		item['body2'] = ui['text']
		item['cashgoods'] = False
		item['tid'] = len(self.founditems) + 1
		self.founditems.append(item)

	def add_spellbook(self, book):
		pg = FantasyGroundsTreasurePage(book)
		self.pstack.append(pg)
		self.processor.page = pg
		for node in book['text']:
			self.txt2page(node)
		prev = self.pstack.pop()
		self.processor.page = prev
		ct = pg.content()
		ct['text'] += self.engine.Render(book, 'spellbook')
		self.founditems.append({
			'body' : ct['text'],
			'body2' : ct['text'],
			'name' : book['name'],
			'type' : 'Spellbook',
			'rarity' : 'Unique',
			'value' : 'Not For Sale',
			'variables' : {},
			'tid' : len(self.founditems) + 1
		})

	def add_mundane_items(self, doc):
		txt = self.engine.Render(doc, 'mundane')
		self.founditems.append({
			'desc' : txt,
			'name' : 'Mundane Items',
			'type' : 'Mundane Items',
			'rarity' : 'Common',
			'value' : 'Not For Sale',
			'variables' : {},
			'tid' : len(self.founditems) + 1
		})

	def add_scrolls(self, doc):
		txt = self.engine.Render(doc, 'scrolls')
		self.treasure.append({
			'desc' : txt,
			'name' : 'Spell Scrolls',
			'type' : 'Scrolls',
			'rarity' : 'Varies',
			'value' : 'Not For Sale',
			'tid' : len(self.founditems) + 1
		})


	def add_loot(self, loot):
		desc = loot[0].strip()
		gp = loot[1]
		tid = len(self.treasure) + 1
		self.treasure.append({
			'desc' : desc,
			'name' : desc,
			'type' : 'Treasure',
			'rarity' : 'Common',
			'value' : gp,
			'tid' : len(self.treasure) + 1
		})

	def format_list(self, node):
		typ = ['ul', 'ol'][node['btyp']]
		txt = "<%s>\n" % typ
		for p in node['bullets']:
			txt += "<li>%s</li>\n" % p
		txt = "</%s>\n" % typ
		self.pstack[-1].add_paragraph(txt)

	def txt2page(self, node):
		if node['category'] == 'paragraph':
			txt = self.processor.process(node['text'])
			self.pstack[-1].add_paragraph(txt)
		elif node['category'] == 'txttype_begin' and node['txttype'] == 1:
			self.pstack[-1].toggle_frame()
		elif node['category'] == 'txttype_end' and node['txttype'] == 1:
			self.pstack[-1].toggle_frame()
		elif node['category'] == 'txttype_begin' and node['txttype'] == 2:
			self.sidebar_count += 1
			prefix = 1000 + self.chapter_count * 100 + 60 + self.sidebar_count
			self.new_page(str(prefix) + '. Sidebar: ' + node['header'])
			self.chapter.add_link('Sidebar: ' + node['header'], 'encounter', self.pstack[-1].pageid)
		elif node['category'] == 'txttype_end' and node['txttype'] == 2:
			self.finish_page()
		elif node['category'] == 'header' and node['depth'] == 2:
			self.add_section(node)
		elif node['category'] == 'header' and node['depth'] == 3:
			self.pstack[-1].add_header(node['text'])
		elif node['category'] == 'table':
			self.pstack[-1].add_table(node['table'])
		elif node['category'] == 'bulletlist':
			self.format_list(node)

	def encounter(self, enc):
		global IMAGES
		self.enc_count += 1
		prefix = 1000 + self.chapter_count * 100 + 80 + self.enc_count 
		ename = str(prefix) + '. Encounter: ' + enc['name']
		page = self.new_page(ename)
		page.add_tag(ename)
		for node in enc['text']:
			self.txt2page(node)
		for diff in enc['encounter_table']:
			self.total_battles += 1
			battle = {
				'id' : self.total_battles,
				'xp' : diff['totalxp'],
				'cr' : 0,
				'name' : enc['name'] + ' - ' + diff['difficulty'] + ' Version',
				'npcs' : []
			}
			page.add_link(battle['name'], 'battle', battle['id'],pre=True)
			for critter in diff['roster']:
				battle['npcs'].append({
					'count' : critter['number'],
					'name' : critter['name'],
					'token' : critter['name'][0],
					'id' : self.monsterlib.get_monster_id(critter['name'])
				})
			for critter in enc['extra_critters']:
				battle['npcs'].append({
					'count' : critter['number'],
					'name' : critter['name'],
					'token' : critter['name'][0],
					'id' : self.monsterlib.get_monster_id(critter['name'])
				})
								
			self.battles.append(battle)
		for sb in enc['sidebars']:
			page.add_header(sb['title'])
			page.add_paragraph(sb['body'])
		if enc['map']:
			i = len(IMAGES) + 1
			IMAGES.append({'name':'Map: ' + enc['name'], 'filename':enc['map'], 'id' : i, 'needgrid' : True})
			page.add_link('Battle Map', 'image', i, True)
		self.chapter.add_link(ename,'encounter',page.pageid)
		self.finish_page()

	def new_page(self, name):
		page = FantasyGroundsPage(name)
		self.pstack.append(page)
		self.processor.page = page
		return page

	def finish_page(self):
		page = self.pstack.pop()
		page.end_page()
		if len(self.pstack):
			self.processor.page = self.pstack[-1]
		else:
			self.processor.page = None
		self.pages.append(page)

	def fglabel(self, doc):
		txt = format_label(doc['variables']['code'])
		txt += format_label(doc['variables']['title'])
		doc['variables']['fglabel'] = txt 

	def format(self, input):
		global IMAGES
		sp = StringProcessor(self.markup)
		doc = sp.run(input)
		mf = MonsterFix()

		self.fglabel(doc)
		self.monsterlib = FantasyGroundsMonsterLib(doc, self.processor)
		self.cover = self.new_page('0000. ' + doc['variables']['title'])
		self.story_pages.append(self.cover)

		for node in doc['text']:
			self.txt2page(node)
		self.finish_page()

		if doc['variables']['coverimage']:
			IMAGES.append({'name':'Cover Art', 'filename':doc['variables']['coverimage'], 'id' : 1, 'needgrid' : False})

		self.prevpage = self.cover
		for chp in doc['chapters']:
			self.chapter_count += 1
			self.in_section = False
			prefix = 1000 + self.chapter_count * 100
			self.chapter = self.new_page(str(prefix) + '. ' + chp['name'])
			self.chapter.add_tag(chp['name'])
			self.story_pages.append(self.chapter)
			self.prevpage.next(self.chapter.pageid)
			self.chapter.prev(self.prevpage.pageid)
			self.prevpage = self.chapter
			self.cover.add_link(chp['name'],'encounter',self.chapter.pageid)
			for node in chp['text']:
				self.txt2page(node)
			for enc in chp['encounters']:
				self.encounter(enc)
			if self.in_section: self.finish_page()
			self.finish_page()
			self.section_count = 0
			self.sidebar_count = 0
			self.enc_count = 0
		self.appendix_pages(doc)
		for loot in doc['cash']:
			self.add_loot(loot)
		for itm in doc['magicitems']:
			self.add_magicitem(itm)
		for itm in doc['consumables']:
			self.add_magicitem(itm)
		for itm in doc['scrolls']:
			self.add_magicitem(itm)
		for bk in doc['spellbooks']:
			self.add_spellbook(bk)
		if 'scrolls' in doc and doc['scrolls']: self.add_scrolls(doc)
		if 'mundane' in doc and doc['mundane']: self.add_mundane_items(doc)

		initial_splices = ['preliminaries', 'credits']
		kys = doc['splices'].keys()
		slist = [k for k in kys if k in initial_splices]
		for splice in slist:
			pname = splice.capitalize()
			self.new_page(pname)
			for node in doc['splices'][splice]['text']:
				self.txt2page(node)
			self.cover.add_link(pname,'encounter',self.pstack[-1].pageid,prepend=True)
			self.finish_page()

		pcontent = [p.content() for p in self.pages]
		story = [{'name' : p.name, 'id' : p.pageid} for p in self.story_pages]
		app_tmp = [{'name' : p.name, 'id' : p.pageid} for p in self.app_pages]
		st_tmp = [{'name' : p.name, 'id' : p.pageid} for p in self.storyaward_pages]
		self.fgdata = {
			'variables' : doc['variables'],
			'pages' : sorted(pcontent, key=lambda p: p['id']),
			'monsters' : mf.run(self.monsterlib.content()),
			'battles' : self.battles,
			'treasure' : self.treasure,
			'founditems' : self.founditems,
			'images' : IMAGES,
			'quests' : doc['quests'],
			'story_pages' : sorted(story, key=lambda p: p['id']),
			'storyaward_pages' : sorted(st_tmp, key=lambda p: p['id']),
			'app_pages' : sorted(app_tmp, key=lambda p: p['id'])
		}

		adventure = self.engine.Render(self.fgdata, 'db')
		self.dbstream.write(adventure)
		self.dbstream.close()

		adventure = self.engine.Render(self.fgdata, 'definition')
		self.descstream.write(adventure)
		self.descstream.close()
