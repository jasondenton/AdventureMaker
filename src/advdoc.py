from copy import deepcopy
from math import floor
import re

from pprint import PrettyPrinter
from patterns import PatternBehavior
from monsters import get_monster, alias_monster
from sidebar import get_sidebar
from bibliography import get_citation
from magicitems import get_magicitem
from spells import get_spell
from npc import get_npc
from advutils import *
from logger import *

class InlineTextProcesser(PatternBehavior):
    def citation(self, cite):
        if cite.strip() not in self.bibenteries:
            self.bibenteries.append(cite)
            self.bibliography.append(get_citation(cite))

    def cash(self, pieces):
        entry = pieces[0].strip() 
        entry = entry[0].upper() + entry[1:]
        try:
            self.cash.append([entry, float(pieces[2].strip())])
            self.totalcash += float(pieces[2])
        except Exception as exp:
            raise Exception("Expected a number at end of loot tag.")

    def rev_cash(self, pieces):
        entry = pieces[2].strip() 
        entry = entry[0].upper() + entry[1:]
        try:
            self.cash.append([entry, float(pieces[0].strip())])
            self.totalcash += float(pieces[0])
        except Exception as exp:
            raise Exception("Expected a number at start of gpfirst tag.")

    def noshowcash(self, pieces):
        entry = pieces[0].strip() 
        entry = entry[0].upper() + entry[1:]
        try:   
            self.cash.append([entry, float(pieces[1].strip())])
            #self.totalcash += format_cash(pieces[1])
            self.totalcash += float(pieces[1])
        except Exception as exp:
            raise Exception("Expected a number at end of noshowloot tag.")

    def npc_ref(self, name):
        name = name.strip()
        if name not in self.npcsenteries:
            self.npcsenteries.append(name)
            npc = get_npc(name)
            self.npcs.append(npc) 

    def quest_xp(self, pieces):
        tag = pieces[0].strip()
        xp = int(pieces[1].strip())
        self.quests.append([tag,xp])
        self.totalquestxp = self.totalquestxp + xp

    def imagehere(self,pieces):
        ifile = pieces.strip()
        self.artwork.append(ifile)

    def add_label(self,pieces):
        self.exlabels.append(pieces.strip())

    def chapref(self,pieces):
        self.chaprefs.append(pieces.strip())

    def stref(self,pieces):
        self.strefs.append(pieces.strip())

    def encref(self,pieces):
        self.encrefs.append(pieces.strip())

    def appref(self,pieces):
        self.apprefs.append(pieces.strip())

    def exref(self,pieces):
        self.exrefs.append(pieces.strip())
                
    def mundane(self, pieces):
        entry = pieces.strip()
        entry = entry[0].upper() + entry[1:]
        self.mundane.append(entry)

    def bold(self, pieces):
        self.bold_count += 1

    def italic(self, pieces):
        self.it_count += 1

    def lstmarker(self, pieces):
        self.list_count += 1

    def numlist(self, pieces):
        self.numlist_count += 1

    def add_table(self, pieces):
        if self.table_open:
            raise Exception("Error: Tables may not be nested.")
        self.table_open = True

    def end_table(self, pieces):
        if not self.table_open:
            raise Exception("Error: Attempt to close a table when no table open.\n    Starting a table requires alignment specs and a table name.")
        self.table_open = False
                   
    def __init__(self):
        PatternBehavior.__init__(self,[
            ['/b/', self.bold],
            ['/i/', self.italic],
            ['/l/', self.lstmarker],
            ['/nl/', self.numlist],
            ['/table ([clrCLR]+):([A-Za-z0-9\'\-\,\. \;:]*)+/', self.add_table],
            ['/table/', self.end_table],
            ['\[\[citation:\W*(\w*)\]\]', self.citation],
            ['\[\[imagehere:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.imagehere],
            ['\[\[label:([A-Za-z0-9\'\-\, \:\.]*)\]\]', self.add_label],
            ['\[\[encounter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.encref],
            ['\[\[storyaward:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.stref],
            ['\[\[chapter:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.chapref],
            ['\[\[appendix:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.appref],
            ['\[\[reference:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.exref],
            ['\[\[loot:([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*:\W?(\d*\.?\d*)\]\]', self.cash],
            ['\[\[gpfirst:\W?(\d*\.?\d*):([A-Za-z0-9\-\(\)\/\' ]+):([A-Za-z0-9\-\(\)\/\' ]+)*\]\]', self.rev_cash],
            ['\[\[noshowloot:\W*([A-Za-z0-9\-\(\)\/\' ]+):\W*(\d*\.?\d*)\]\]', self.noshowcash],
            ['\[\[NPC:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.npc_ref],
            ['\[\[xp:([A-Za-z0-9\'\-\,\. ]*):\W*(\d*)\]\]', self.quest_xp],
            ['\[\[mundane:([A-Za-z0-9\'\-\,\. \:]*)\]\]', self.mundane]
        ], False)
        self.bibenteries = []
        self.bibliography = []
        self.npcs = []
        self.npcsenteries = []
        self.cash = []
        self.quests = []
        self.totalcash = 0.0
        self.totalquestxp = 0
        self.artwork = []
        self.exlabel = []
        self.chaprefs = []
        self.strefs = []
        self.encrefs = []
        self.apprefs = []
        self.exlabels = []
        self.exrefs = []
        self.bold_count = 0
        self.it_count = 0
        self.table_open = False
        self.list_count = 0
        self.numlist_count = 0
        self.mundane = []

class SubDocument:
    def __init__(self, name):
        self.docline = []
        self.variables = {'name' : name.strip()}
        self.txttype = 0
        self.inpara = False
        self.inlist = False
        self.name = name

    def start_paragraph(self):
        self.docline.append({
            'category' : 'paragraph',
            'text' : ''
        })
        self.inpara = True
        self.inlist = False

    def endparagraph(self):
        self.inpara = False
        self.inlist = False

    def set_txttype(self,nxttype, header=None):
        if (nxttype == self.txttype): return
        if self.txttype > 0:
            self.docline.append({
                'category' : 'txttype_end',
                'txttype' : self.txttype
            })
        if nxttype > 0:
            self.docline.append({
                'category' : 'txttype_begin',
                'txttype' : nxttype,
                'header' : header
            })
        self.txttype = nxttype
        self.inpara = False
        self.inlist = False

    # callwith add_bulletpoint('my bullettext', 0/1)
    def add_bulletpoint(self, point, typ):
        self.set_txttype(0)
        if self.inlist == False:
            self.docline.append({
                'category' : 'bulletlist',
                'bullets' : [point],
                'btyp' : typ
            })
            self.inlist = True
            self.inpara = False
        else:
            self.docline[-1]['bullets'].append(point)

    def append_bullet(self, txt):
        self.docline[-1]['bullets'][-1] += ' ' + txt

    def add_line(self,line,typ):
        self.set_txttype(typ)
        if not self.inpara: self.start_paragraph()
        else: self.docline[-1]['text'] += ' '
        self.docline[-1]['text'] += line

    def add_header(self, txt, depth):
        self.set_txttype(0)
        self.endparagraph()
        self.docline.append({
            'category' : 'header',
            'depth' : depth,
            'text' : txt
        }) 

    def add_table(self, tab):
        self.set_txttype(0)
        self.endparagraph()
        self.docline.append({
            'category' : 'table',
            'table' : tab
        })

    def docvariable(self, key, value):
        self.variables[key] = value

    def label(self):
        return format_label(self.name)

    def close(self):
        self.set_txttype(0)
        self.endparagraph()

    def contents(self):
        self.close()
        for l in self.docline:
            if l['category'] == 'table':
                l['table'] = l['table'].contents()
        return {
            'variables' : self.variables,
            'text' : self.docline,
            'name' : self.name,
        }

    def special(self, pieces):
        print pieces
        raise Exception('Special processing line used out of context.')

ENCOUNTER_DIFFICULTY_LIST = ['Vweak', 'Weak', 'Normal', 'Strong', 'Vstrong']
MONSTER_ENTRY_PATTERN = re.compile(" ?(\d\d?)? ?(.*)")

def max_figures(flst, elst):
    nlst = deepcopy(flst)
    for fig in elst.keys():
        if fig in nlst:
            nlst[fig] = max(nlst[fig],elst[fig])
        else:
            nlst[fig] = elst[fig]
    return nlst

class Spellbook(SubDocument):
    def __init__(self, name):
        SubDocument.__init__(self,name)
        self.splst = [[],[],[],[],[],[],[],[],[]]

    def contents(self):
        cnt = SubDocument.contents(self)
        for lst in self.splst:
            lst.sort()
        cnt['spells'] = self.splst
        return cnt

    def add_spell(self, spname):
        sp = get_spell(spname);
        lvl = sp['level']
        lvl -= 1
        self.splst[lvl].append(sp['name'])

    def special(self, pieces):
        if pieces[0] != 'spells' :
            raise Exception("Invalid - line in spell book %s." % self.name)
        sps = pieces[1].split(",")
        for s in sps:
            self.add_spell(s.strip())

class Encounter(SubDocument):
#encounter_table = {difficulty : normal, totalxp : 0, roster: [{name : foo, number: 1, xp : 10}]}

    def contents(self):
        cnt = SubDocument.contents(self)
        if self.reorder:
            cnt['stat_blocks'] = sorted(self.stat_blocks, key=lambda sb: sb['blocklength'])
        else:
            cnt['stat_blocks'] = self.stat_blocks
        cnt['encounter_table'] = self.encounter_table
        cnt['sidebars'] = [get_sidebar(sb) for sb in self.sidebars]
        cnt['label'] = self.label()
        cnt['map'] = self.map
        cnt['evenstart'] = self.evenstart
        cnt['extra_critters'] = self.extra_critters
        return cnt

    def encounter_difficulty(self, difficulty, mlst):
        difficulty = difficulty.strip().capitalize()
        if difficulty not in ENCOUNTER_DIFFICULTY_LIST and difficulty != 'Noxp':
            raise Exception("Encounter difficulty must be one of %s." % ", ".join(ENCOUNTER_DIFFICULTY_LIST))

        totalxp = 0
        roster = []
        clist = mlst.split(",")
        diff_figs = {}
        sprevbar = None
        for crit in clist:
            critter = crit.strip()
            mo = MONSTER_ENTRY_PATTERN.match(critter).groups()
            num = int(mo[0]) if mo[0] else 1
            mname = mo[1]
            sblock = get_monster(mname)
            print_name = sblock['name'] #get normalize name
            xp = sblock['xp']
            totalxp += xp * num
            roster.append({'name' : print_name, 'number' : num, 'xp' : xp})
            diff_figs[print_name] = num
            if mname not in self.appearing:
                self.appearing.append(mname)
                self.stat_blocks.append(sblock)
            if 'sidebar' in sblock:
                sb = sblock['sidebar']
                if sb not in self.sidebars:
                    self.sidebars.append(sb) 
        if difficulty != 'Noxp':
            self.encounter_table.append({
                "difficulty" : difficulty,
                "totalxp" : totalxp,
                "roster" : roster
            })
        if difficulty == 'Noxp':
            self.extra_critters += roster
        self.figures = max_figures(self.figures, diff_figs)

    def special(self, pieces):
        if pieces[0] == 'map':
            self.map = pieces[1].strip()
        elif pieces[0] == 'order':
            tmp = []
            for k in pieces[1].split(','):
                split_block = False
                k = k.strip()
                if k[0] == '!':
                    k = k[1:]
                    split_block = True
                for st in self.stat_blocks:
                    if k == st['name']:
                        dup = deepcopy(st)
                        dup['split_block'] = split_block 
                        tmp.append(dup)
            self.stat_blocks = tmp
            self.reorder = False
        else:
            self.encounter_difficulty(pieces[0],pieces[1])

    def __init__(self, name):
        SubDocument.__init__(self, name)
        self.encounter_table = []
        self.appearing = []
        self.stat_blocks = []
        self.figures = {}
        self.sidebars = []
        self.reorder = True
        self.evenstart = True
        self.map = None
        self.extra_critters = []

class Chapter(SubDocument):      
    def contents(self):
        cnt = SubDocument.contents(self)
        enc_contents = []
        for en in self.encounters:
            enc_contents.append(en.contents())
        cnt['encounters'] = enc_contents
        cnt['label'] = self.label()
        return cnt

    def new_encounter(self, name):
        if len(self.encounters): self.encounters[-1].close()
        enc = Encounter(name)
        self.encounters.append(enc)
        return enc

    def __init__(self, name):
        SubDocument.__init__(self, name)
        self.encounters = []

class StoryAward(SubDocument):
    def __init__(self, name):
        SubDocument.__init__(self, name)

    def switch_part(self):
        self.close()
        self.dmtext = self.docline
        self.docline = []

    def special(self, pieces):
        self.switch_part()

    def contents(self):
        cnt = SubDocument.contents(self)
        cnt['text2'] = self.dmtext
        cnt['label'] = "story_" + self.label()
        return cnt

class MagicItem(SubDocument):

    def value_by_rarity(self,rarity):
        if rarity == 'Common':
            return 50
        elif rarity == 'Uncommon':
            return 500
        elif rarity == 'Rare':
            return 5000
        elif rarity == 'Very Rare':
            return 50000
        elif rarity == 'Legendary':
            return 150000
        elif rarity == 'Unique':
            return 500000

    def adjust_scroll(self,it):
        sp = it['spell']
        level = sp['level']
        addline = ''
        scrollentry = sp['name']
        if 'level' in self.variables and self.variables['level'] > sp['level']:
            level = int(self.variables['level'])
            addline = 'When used, this scroll casts @spell as a level %d spell. ' % level
            scrollentry += ' (at %d level)' % level
        if level < 3 : dc = 13
        elif level < 5 : dc = 15
        elif level < 7 : dc = 17
        elif level < 9 : dc = 18
        else : dc = 19
        tohit = dc - 8
        if level < 2 : it['rarity'] = 'Common'
        elif level < 4 : it['rarity'] = 'Uncommon'
        elif level < 6 : it['rarity'] = 'Rare'
        elif level < 9 : it['rarity'] = 'Very Rare'
        else : it['rarity'] = 'Legendary'
        if 'mechanism' in sp:
            if sp['mechanism'] == 'attack' or sp['mechanism'] == 'both' :
                addline += 'The attack bonus when you use this scroll is +%d.' % tohit
            if sp['mechanism'] == 'save' or sp['mechanism'] == 'both':
                addline += 'The save DC when you use this scroll is %d.' % dc 
            if addline != '':
                it['description'] += '!!'
                it['description'] += addline
        it['scrolltag'] = scrollentry
        return it

    def spawn_item(self):
        rarity = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary']
        key = self.variables['item'] if 'item' in self.variables else 'default'
        it = get_magicitem(key)
        if it['spell'] :
            self.variables['spell'] = it['spell']
        if 'spell' in self.variables:
            it['spell'] = get_spell(self.variables['spell'])
        if key == 'Spell Scroll' : it = self.adjust_scroll(it)
        for n in it['need']:
            if n not in self.variables: 
                raise Exception("Item %s needs variable %s set." % (key, n))
            rep = '@' + n
            it['name'] = it['name'].replace(rep,self.variables[n].capitalize())
            it['description'] = it['description'].replace(rep,self.variables[n].lower())
            it['category'] = it['category'].replace(rep,self.variables[n].capitalize())
            if 'fg_subtype' in it:
                it['fg_subtype'] = it['fg_subtype'].replace(rep,self.variables[n].capitalize())
        
        it['text2'] = deepcopy(self.docline)          
        dl = []
        if 'description' in it and it['description']:
            dl = self.docline
            self.docline = []
            self.add_line(it['description'],0)
            self.endparagraph()
            self.docline = self.docline + dl
        if it['rarity'] == 'byplus':
            it['rarity'] = rarity[int(self.variables['plus'])]
        elif it['rarity'] == 'rarebyplus':
            it['rarity'] = rarity[int(self.variables['plus'])+1]

        if 'called' in self.variables:
            it['name'] = self.variables['called']
        if 'available' not in self.variables: self.variables['available'] = 1
        if 'attuneby' not in it: it['attuneby'] = None
        it['available'] = int(self.variables['available'])
        it['castvalue'] = self.value_by_rarity(it['rarity'])
        return it

    def contents(self):
        it = self.spawn_item()
        cnt = SubDocument.contents(self)
        cnt.update(it)
        return cnt

    def special(self, pieces):
        self.variables[pieces[0]] = pieces[1].strip()

    def __init__(self, name):
        SubDocument.__init__(self, name)

class MainDocument(SubDocument):

    def __init__(self):
        SubDocument.__init__(self,'Main')
        self.chapters = []
        self.appendix = []
        self.storyawards = []
        self.magicitems = []
        self.monsters = []
        self.spellbooks = []
        self.variables = {
            'title' : 'Set the title variable',
            'code' : 'CCC-Unknown',
            'tier' : 1,
            'playtime' : 2
        }

    def contents(self):
        cnt = SubDocument.contents(self)
        cnt['chapters'] = [c.contents() for c in self.chapters]
        cnt['figures'] = self.module_figure_list()
        cnt['xpdata'] = self.xp_for_diffculty_table()
        cnt['storyawards'] = [s.contents() for s in self.storyawards]
        mtmp = [m.contents() for m in self.magicitems]
        cnt['magicitems'] = []
        cnt['consumables'] = []
        cnt['scrolls'] = []
        for m in mtmp:
            m['variables']['advtitle'] = self.variables['title']
            m['variables']['code'] = self.variables['code']
            if 'scrolltag' in m:
                cnt['scrolls'].append(m)
            elif m['consumable']:
                cnt['consumables'].append(m)
            else:
                cnt['magicitems'].append(m)
        if len(cnt['scrolls']) == 1: #treat 1 scroll as an ordinary consumable
            cnt['consumables'] += cnt['scrolls']
            cnt['scrolls'] = []
        cnt['extra_monsters'] = self.monsters
        cnt['appendix'] = self.appendix
        cnt['spellbooks'] = [s.contents() for s in self.spellbooks]
        return cnt

    def new_chapter(self, name):
        if len(self.chapters): self.chapters[-1].close()
        chp = Chapter(name)
        self.chapters.append(chp)
        return chp

    def new_storyaward(self,name):
        if len(self.storyawards): self.storyawards[-1].close()
        stawd = StoryAward(name)
        self.storyawards.append(stawd)
        return stawd

    def new_spellbook(self,name):
        if len(self.spellbooks): self.spellbooks[-1].close()
        book = Spellbook(name)
        self.spellbooks.append(book)
        return book

    def new_magicitem(self,name):
        if len(self.magicitems): self.magicitems[-1].close()
        mi = MagicItem(name)
        self.magicitems.append(mi)
        return mi  

    def module_figure_list(self):
        mod_figs = {}
        for chp in self.chapters:
            for enc in chp.encounters:
                mod_figs = max_figures(mod_figs, enc.figures)
        figs = []
        for f in sorted(mod_figs.keys()):
            figs.append([f,mod_figs[f]])
        return figs

    def add_monster(self, monster):
        self.monsters.append(get_monster(monster))

    def add_appendix_image(self, nm, image):
        self.appendix.append({
                'name' : nm.strip(),
                'image' : image.strip(),
                'label' : format_label(nm)
            })

    def xp_for_diffculty_table(self):
        has_diff = {}
        for diff in ENCOUNTER_DIFFICULTY_LIST:
            has_diff[diff] = False
        for chp in self.chapters:
            for enc in chp.encounters:
                for diff in enc.encounter_table:
                    has_diff[diff['difficulty']] = True
        #has_diff now tell what difficulties present in adventure
        cnt_diff = 1
        for key in ENCOUNTER_DIFFICULTY_LIST:
            if has_diff[key]: 
                has_diff[key] = cnt_diff
                cnt_diff += 1
        #has_diff now maps difficulty to row
        xp_for_encounter_by_difficult = []
        totalxp = ['Total XP'] + [0,0,0,0,0][:cnt_diff-1]
        for chp in self.chapters:
            for enc in chp.encounters:
                row = [enc.name] + [0,0,0,0,0][:cnt_diff-1]
                for d in enc.encounter_table:
                    row[has_diff[d['difficulty']]] = d['totalxp']
                    totalxp[has_diff[d['difficulty']]] += d['totalxp']
                #for cell in range(0,len(row)):
                #    row[cell] = str(row[cell])
                row = [str(x) for x in row]
                xp_for_encounter_by_difficult.append(row)
        has_difficulties = []
        for key in ENCOUNTER_DIFFICULTY_LIST:
            if has_diff[key]: has_difficulties.append(key)
        xp_party_size = []
        for diff in range(0,len(has_difficulties)):
            row = [has_difficulties[diff], '0', '0', '0', '0', '0']
            for idx in range(1,6):
                row[idx] = str(totalxp[diff+1] / (idx + 2))
            xp_party_size.append(row)
        totalxp = [str(x) for x in totalxp]
        #xp_for_encounter_by_difficult.append(totalxp)
        return {
            'difficulties' : has_difficulties,
            'by_encounter' : xp_for_encounter_by_difficult,
            'party_size' : xp_party_size,
            'cols_in_diff' : len(has_difficulties)+1,
            'totalxpbydiff' : totalxp
        }

class AdvTable:
    def __init__(self, headerline, name, w=False):
        self.table = []
        self.header = []
        self.alignment = []
        self.name = name if name else ''
        self.maxlen = -1
        self.longcol = -1
        self.wide = w
        parts = headerline.split("|")
        for p in parts:
            left = p[0] != ' '
            right = p[-1] != ' '
            center = left == right
            if center: align = 'center'
            elif left: align = 'left'
            else: align = 'right'
            self.alignment.append(align)
            self.header.append(p.strip())

    def add_line(self, line):
        parts = line.split("|")
        tab = []
        idx = 0
        for p in parts:
            tmp = p.strip()
            tab.append(tmp)
            l = len(tmp)
            if l > self.maxlen:
                self.maxlen = l
                self.longcol = idx
            idx += 1

        self.table.append(tab)
        if len(tab) != len(self.header):
            raise Exception("Table does not have the right number of columns.")

    def endparagraph(self):
        return

    def close(self):
        return

    def contents(self):
        return {
            'alignment' : self.alignment,
            'header' : self.header,
            'table' : self.table,
            'name' : self.name,
            'longestcol' : self.longcol,
            'wide' : self.wide
        }

class AdventureBuilder(PatternBehavior):
    def set_current_doc(self, doc):
        if isinstance(doc, Chapter):
            self.docstack = self.docstack[0:1] #pop everything but main doc
        elif isinstance(doc, Encounter):
            if not isinstance(self.docstack[1], Chapter):
                raise Exception('Cannot have an encounter outside of a chapter')
            self.docstack = self.docstack[0:2]
        self.docstack.append(doc)
        self.curdoc = doc

    def variable(self, pieces):
        self.curdoc.docvariable(pieces[0],pieces[1])

    def new_chapter(self, pieces):
        if not isinstance(self.curdoc, MainDocument) and not isinstance(self.curdoc, Chapter):
            raise Exception("Can not start a new chapter here.")
        chp = self.maindoc.new_chapter(pieces)
        self.set_current_doc(chp)
        self.toclines += 2

    def new_encounter(self, pieces):
        if self.in_encounter :
            raise Exception("Encounters may not be nested.")
        en = self.curdoc.new_encounter(pieces)
        self.set_current_doc(en)
        self.in_encounter = True
        self.total_encounters += 1
        self.toclines += 1

    def new_spellbook(self, pieces):
        book = self.maindoc.new_spellbook(pieces)
        self.set_current_doc(book)

    def appendix_image(self, pieces):
        p = pieces.split(":")
        self.maindoc.add_appendix_image(p[0], p[1])
        self.toclines += 2

    def endsubdoc(self, pieces):
        if isinstance(self.curdoc, Encounter):
            self.in_encounter = False
        self.curdoc.close()
        self.docstack.pop()
        self.curdoc = self.docstack[-1]

    def namedsidebar(self, pieces):
        self.curdoc.close()
        self.curdoc.set_txttype(0)
        self.curdoc.set_txttype(2, pieces.strip())

    def textline(self, pieces):
        nxttype = len(pieces[0]) if pieces[0] else 0
        txt = pieces[1]
        txt.strip()
        self.text_processer.match_and_process(txt)
        print(pieces)
        if self.curdoc.inlist:
            self.curdoc.append_bullet(txt)
        else:
            self.curdoc.add_line(txt, nxttype)

    def heading(self, pieces):
        lvl = len(pieces[0])
        if isinstance(self.curdoc,Encounter):
            if lvl < 3: 
                log_message("Use only *** headers in encounters.")
                lvl = 3 #only subsections in encounters
        self.curdoc.add_header(pieces[1],lvl)
        if lvl <= 2:
            self.toclines += 1

    def noop(self,pieces):
        return

    def endparagraph(self, pieces):
        self.curdoc.endparagraph()
        if isinstance(self.curdoc,AdvTable):
            self.endsubdoc(pieces)

    def check_references(self, cnt):
        labels = {
            'appendix' : [format_label('Adventure Summary')] + [format_label(a['name']) for a in cnt['appendix']],
            'chapter' : [],
            'storyawards' : [format_label(s['name']) for s in cnt['storyawards']],
            'encounter' : [],
            'general' : [format_label(l) for l in self.text_processer.exlabels]
        }
        for chp in cnt['chapters']:
            labels['chapter'].append(format_label(chp['name']))
            for enc in chp['encounters']:
                labels['encounter'].append(format_label(enc['name']))

        for r in self.text_processer.apprefs:
            l = format_label(r)
            if l not in labels['appendix']:
                log_message("Warning: Reference to unknown appendix %s." % r)
        for r in self.text_processer.chaprefs:
            l = format_label(r)
            if l not in labels['chapter']:
                log_message("Warning: Reference to unknown chapter %s." % r)
        for r in self.text_processer.strefs:
            l = format_label(r)
            if l not in labels['storyawards']:
                log_message("Warning: Reference to unknown story award %s." % r)
        for r in self.text_processer.encrefs:
            l = format_label(r)
            if l not in labels['encounter']:
                log_message("Warning: Reference to unknown encounter %s." % r)            
        for r in self.text_processer.exrefs:
            l = format_label(r)
            if l not in labels['general']:
                log_message("Warning: Reference to unknown label %s." % r)

    def check_markup(self):
        valid = True
        if self.text_processer.bold_count % 2 == 1: 
            log_message("Unterminiated bold markup (/b/).")
            valid = False
        if self.text_processer.it_count % 2 == 1:
            log_message("Unterminiated italic markup (/i/).")
            valid = False
        if self.text_processer.numlist_count % 2 == 1:
            log_message("Unterminated numeric list markup (/nl/).")
            valid = False
        if self.text_processer.list_count % 2 == 1: 
            log_message("Unterminated list markuped (/l/).")
            valid = False
        if self.text_processer.table_open:
            log_message("Unterminated table (missing /table).")
            valid = False
        return valid

    def validate_document(self, cnt):
        self.check_references(cnt)
        return self.check_markup()


    def contents(self):
        tiers = [0,'1-4','5-10','11-16','17-20']
        optlvl = [0,'2nd', '7th', '13th', '18th']
        dmxphour = [0, 75, 325, 800, 1675]

        cnt = self.maindoc.contents()
        variables = cnt['variables']
        cnt['bibliography'] = self.text_processer.bibliography
        cnt['cash'] = self.text_processer.cash
        cnt['totalcash'] = format_cash(self.text_processer.totalcash)
        cnt['npcs'] = sorted(self.text_processer.npcs,key=lambda npc: npc['name'])
        cnt['quests'] = self.text_processer.quests
        cnt['mundane'] = self.text_processer.mundane
        cnt['spellbook'] = [get_spell(sp) for sp in self.spellbook]
        cash = float(self.text_processer.totalcash)
        cnt['totalquestxp'] = self.text_processer.totalquestxp
        cnt['cashsplit'] = ["{0:0.2f}".format(cash / float(s)) for s in range(3,8)]
        cnt['splices'] = {}
        for k in self.splices:
            cnt['splices'][k] = self.splices[k].contents()
        certitems = False
        tmp = cnt['magicitems']+cnt['consumables']+cnt['scrolls']
        for it in tmp:
            if not (it['variables'].get('nocert',False)):
                certitems = True
                break
        cnt['artwork'] = [a['image'] for a in cnt['appendix']]
        cnt['artwork'] += self.text_processer.artwork
        if 'coverimage' in variables: cnt['artwork'].append(variables['coverimage'])
        for chp in cnt['chapters']:
            for enc in chp['encounters']:
                if enc['map']: cnt['artwork'].append(enc['map'])
        for it in cnt['magicitems']:
            if 'image' in it['variables']:
                cnt['artwork'].append(it['variables']['image'])
        for it in cnt['consumables']:
            if 'image' in it['variables']:
                cnt['artwork'].append(it['variables']['image'])
        try:
            if 'tier' not in variables: raise Exception('no tier')
            ti = int(variables['tier'])
            if ti < 1 or ti > 4: raise Exception('out of bounds')
        except Exception:
            raise Exception('The tier variable must be a number from 1-4.')
        try:
            if 'playtime' not in variables: raise Exception('no playtime')
            ptime = int(variables['playtime'])
            tblocks = int(floor(ptime/2))
        except Exception:
            raise Exception('The playtime variable must be set and must be an integer.')
        renown = 1
        if ptime >= 8: renown = 2
        if cnt['xpdata']['difficulties']:
            if not 'minxp' in cnt['variables']:
                minxp = int(cnt['xpdata']['party_size'][0][4]) + (cnt['totalquestxp'] // 2)
                minxp = (minxp // 50) * 50
                cnt['variables']['minxp'] = minxp
            if not 'maxxp' in cnt['variables']:
                mdif = len(cnt['xpdata']['party_size']) - 1
                maxxp = int(cnt['xpdata']['party_size'][mdif][2]) + cnt['totalquestxp']
                maxxp = ((maxxp // 50) + 1) * 50
                cnt['variables']['maxxp'] = maxxp

        if len(cnt['bibliography']) > 0: self.toclines += 2
        if len(cnt['npcs']) > 0: self.toclines += 2
        longtoc = self.toclines > 55

        cnt['intvars'] = {
            'encounters' : self.total_encounters,
            'has_story_awards': self.has_story_awards,
            'has_itemcerts': certitems,
            'tierlevels' : tiers[ti],
            'optlevels' : optlvl[ti],
            'dmgold' : int(floor(dmxphour[ti] * int(variables['playtime']) / 2)),
            'dmxp' : dmxphour[ti] * int(variables['playtime']),
            'downtime' : 5 * tblocks,
            'renown' : renown,
            'longtoc' : longtoc,
        }
        return cnt

    def add_monster(self, pieces):
        self.maindoc.add_monster(pieces)

    def named_monster(self, pieces): #monster is an individual
        alias_monster(pieces[1].strip(), pieces[0].strip(), True)

    def skin_monster(self, pieces): #monster is just reskinned
        alias_monster(pieces[1].strip(), pieces[0].strip(), False)

    def add_bullet(self, pieces):
        numlist = False
        if pieces[0][0] == '#': numlist = True
        self.text_processer.match_and_process(pieces[1])
        self.curdoc.add_bulletpoint(pieces[1], numlist)

    def special(self, pieces):
        self.curdoc.special(pieces)

    def new_storyaward(self,pieces):
        st = self.maindoc.new_storyaward(pieces)
        self.set_current_doc(st)
        self.has_story_awards = True

    def splice(self,pieces):
        sp = SubDocument(pieces)
        self.set_current_doc(sp)
        self.splices[pieces] = sp

    def magic_item(self,pieces):
        mi = self.maindoc.new_magicitem(pieces)
        self.set_current_doc(mi)

    def switch_part(self, tmp):
        if isinstance(self.curdoc, StoryAward):
            self.curdoc.switch_part()
        else:
            raise Exception('Found a !playertext command when not in a story award block.')

    def table_name(self,pieces):
        self.table_name = pieces

    def wide_table_name(self,pieces):
        self.table_name = pieces
        self.table_wide = True

    def spell_reference(self, pieces):
        self.spellbook.append(pieces)

    def table(self,pieces):
        if isinstance(self.curdoc, AdvTable):
            self.curdoc.add_line(pieces)
        else:
            table = AdvTable(pieces, self.table_name, self.table_wide)
            self.curdoc.add_table(table)
            self.set_current_doc(table)
        self.table_name = None
        self.table_wide = False

    def __init__(self):
        PatternBehavior.__init__(self,[
            ['^@(\w+) (.+)$', self.variable],
            ['^\* (.+)$', self.new_chapter],
            ['^(\*\*+) (.+)$', self.heading],
            ['^- (\w+):(.+)?$', self.special],
            ['^\|\|\|\| (.*)$', self.wide_table_name],
            ['^\|\|\| (.*)$', self.table_name],
            ['^\|(.*)\|$', self.table],
            ['^!encounter (.*)', self.new_encounter],
            ['^!storyaward (.*)', self.new_storyaward],
            ['^!magicitem (.*)', self.magic_item],
            ['^!spellbook (.*)', self.new_spellbook],
            ['^!end', self.endsubdoc],
            ['^!monster (.*)$', self.add_monster],
            ['^!namedmonster ([A-Za-z0-9\-\(\)\' ]+)/(.*)$', self.named_monster],
            ['^!skinmonster ([A-Za-z0-9\-\(\)\' ]+)/(.*)$', self.skin_monster],
            ['^!appendix_image (.*)$',self.appendix_image],
            ['^!spellreference (.*)$',self.spell_reference],            
            ['^!splice (.*)$',self.splice],
            ['^!table (.*)$', self.table_name],
            ['^//.*', self.noop],
            ['^$', self.endparagraph],
            ['^>>#(.+)$', self.namedsidebar],
            ['^-(.) (.*)$', self.add_bullet],
            ['^(>*)?(.+)$', self.textline]
        ])
        self.maindoc = MainDocument()
        self.curdoc = self.maindoc
        self.docstack = [self.maindoc]
        self.text_processer = InlineTextProcesser()
        self.splices = {}
        self.table_name = None
        self.table_wide = False
        self.total_encounters = 0
        self.has_story_awards = False
        self.toclines = 2
        self.spellbook = []
        self.in_encounter = False

def ParseAdventureDocument(doc):
    builder = AdventureBuilder()
    pdoc = None  
    try:
        builder.match_and_process(doc)
        pdoc = builder.contents()
        #fout = open('/Users/jdenton/tmp/advdoc','w')
        #pp = PrettyPrinter(indent=2, stream=fout)
        #pp.pprint(pdoc)
        #fout.close()
        if builder.validate_document(pdoc): return pdoc
    except Exception as exp:
        log_message("Error: line %d: %s" % (builder.lineno,str(exp)))
    return False

def DebugAdventureDocument(doc):
    builder = AdventureBuilder()
    pdoc = None  
    builder.match_and_process(doc)
    pdoc = builder.contents()
    fout = open('/tmp/advdoc','w')
    pp = PrettyPrinter(indent=2, stream=fout)
    pp.pprint(pdoc)
    fout.close()
    if builder.validate_document(pdoc): return pdoc
    return False

