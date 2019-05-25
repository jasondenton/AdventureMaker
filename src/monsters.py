import glob
import math
import json
import sys
import os
from copy import deepcopy
from logger import log_message
from datavisit import DataVisitor

class MonsterRenamer(DataVisitor):
	def __init__(self, oldname, newname, old_u, new_u):
		self.oldname = oldname
		self.newname = newname
		self.old_unique = old_u
		self.new_unique = new_u

	def visit_string(self, value):
		s = value
		n = self.newname

		olds = [self.oldname]
		tmp = self.oldname.split(" ")
		if len(tmp) > 1:
			olds.append(tmp[0])

		if not self.old_unique and not self.new_unique:
			for o in olds:
				s = s.replace('The ' + o.lower(), 'The ' + n.lower())
				s = s.replace('the ' + o.lower(), 'the ' + n.lower())
				s = s.replace(o,n)

		if not self.old_unique and self.new_unique:
			for o in olds:
				s = s.replace('The ' + o.lower(), n)
				s = s.replace('the ' + o.lower(), n)
				s = s.replace(o,n)

		if self.old_unique and self.new_unique:
			for o in olds:
				s = s.replace(o,n)

		if self.old_unique and not self.new_unique:
			for o in olds:
				s = s.replace(o, 'The ' + n.lowercase())
				s = s.replace('. t', '. T')
		return s

total_monsters_used = 0
monster_db = {}
monster_manual = {}

STATS = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
MODS_FOR_SKILLS = {
	'acrobatics' : 'dexterity',
	'animal handling' : 'wisdom',
	'arcana' : 'intelligence',
	'athletics' : 'strength',
	'deception' : 'charisma',
	'history' : 'intelligence',
	'insight' : 'wisdom',
	'intimidation' : 'charisma',
	'investigation' : 'intelligence',
	'medicine' : 'wisdom',
	'nature' : 'intelligence',
	'perception' : 'wisdom',
	'performance' : 'charisma',
	'persuasion' : 'charisma',
	'religion' : 'intelligence',
	'sleight of hand' : 'dexterity',
	'stealth' : 'dexterity',
	'survival' : 'wisdom'
}

def xp_for_cr(cr):
	XP_FOR_LEVEL = [10,200,450,700,1100,1800,2300,2900,3900,5000,5900,7200,8400,10000,
	11500,13000, 15000,18000,20000,22000,25000,33000,41000,50000,62000,75000,90000,105000,120000,
	135000,155000];
	if cr == '0': return 10
	if cr == '1/8': return 25
	if cr == '1/4': return 50
	if cr == '1/2': return 100
	return XP_FOR_LEVEL[int(cr)]

def proficiency_for_cr(cr):
	if cr == '1/8' or cr == '1/4' or cr == '1/2': return 2
	cr = int(cr)
	if cr < 5: return 2
	if cr < 9: return 3
	if cr < 13: return 4
	if cr < 17: return 5
	if cr < 21: return 6
	if cr < 25: return 7
	if cr < 29: return 8
	return 9

def modifiers_for_stats(block):
	mod = {}
	for st in STATS:
		mod[st] = int(math.floor(block[st] / 2) - 5)
	return mod

def set_saves(block):
	sv = []
	p = block['proficiency']
	if 'strength' in block['saves']:
		bonus = p + block['modifier']['strength']
		sv.append('Str +%d' % bonus)
	if 'dexterity' in block['saves']:
		bonus = p + block['modifier']['dexterity']
		sv.append('Dex +%d' % bonus)
	if 'constitution' in block['saves']:
		bonus = p + block['modifier']['constitution']
		sv.append('Con +%d' % bonus)
	if 'intelligence' in block['saves']:
		bonus = p + block['modifier']['intelligence']
		sv.append('Int +%d' % bonus)
	if 'wisdom' in block['saves']:
		bonus = p + block['modifier']['wisdom']
		sv.append('Wis +%d' % bonus)
	if 'charisma' in block['saves']:
		bonus = p + block['modifier']['charisma']
		sv.append('Cha +%d' % bonus)
	block['saves'] = ', '.join(sv)
	return block

def set_skills(block):
	sklst = []	
	p = block['proficiency']
	pp = 10 + block['modifier']['wisdom']
	if 'perception' in block['skills']: pp += p
	if 'perception' in block['expertise']: pp += p
	block['passive_perception'] = pp
	for sk in block['skills']:
		bonus = block['modifier'][MODS_FOR_SKILLS[sk]] + p
		if 'expertise' in block and sk in block['expertise']: bonus += p
		sklst.append("%s +%d" % (sk.capitalize(), bonus))
	sklst.sort()
	block['skills'] = ', '.join(sklst)
	return block

def sizeof_monster(block):
	jstr = json.dumps(block)
	return len(jstr)

def monster_from_db(mname):
	global monster_db
	entry = deepcopy(monster_db[mname])
	if 'basedon' in entry:
		base = deepcopy(monster_from_db(entry['basedon']))
		base.update(entry)
		entry = base
		del entry['basedon']
	return entry

def denormalize_monster(mname):
	global total_monsters_used
	global monster_manual
	block = monster_from_db(mname)
	block['proficiency'] = proficiency_for_cr(block['challenge_rating'])
	xp = xp_for_cr(block['challenge_rating'])
	block['xp'] = xp
	block['modifier'] = modifiers_for_stats(block)
	block = set_skills(block)
	block = set_saves(block)
	ptperdie = (block['hit_dice_size'] + 1) / 2.0
	block['hit_points'] = int(block['hit_dice_num'] * ptperdie)
	htdbonus = block['modifier']['constitution'] * block['hit_dice_num']
	block['hit_points'] += htdbonus
	block['hit_dice_bonus'] = "%+d" % htdbonus
	block['blocklength'] = sizeof_monster(block)
	total_monsters_used += 1
	block['muid'] = total_monsters_used
	if 'large_block' in block and block['large_block']:
		block['split_block'] = True
	if block.get('legendary_actions', False):
		if not 'legendaries' in block:
			block['legendaries'] = 3
		if block.get('unique', False):
			block['legtitle'] = block['name']
		else:
			block['legtitle'] = 'The ' + block['name'].lower()
	monster_manual[mname] = block

def get_monster(mname):
	global monster_manual
	global monster_db
	if mname in monster_manual:
		return monster_manual[mname]
	elif mname in monster_db:
		denormalize_monster(mname)
		return monster_manual[mname]
	log_message("Warning: Missing Monster %s." % mname)
	alias_monster("Missing Monster", mname, False)
	return monster_manual[mname]

def alias_monster(mname, alias, uniq=True):
	global monster_manual
	if alias in monster_manual: return
	if mname not in monster_manual:
		denormalize_monster(mname)
	dup = deepcopy(monster_manual[mname])
	oldname = dup['name']
	renamer = MonsterRenamer(oldname, alias, dup.get('unique',False), uniq)
	block = renamer.run(dup)
	block['name'] = alias
	block['unique'] = uniq
	if uniq:
		block['legtitle'] = alias
	else:
		block['legtitle'] = 'The + ' + alias.lower()
	monster_manual[alias] = block

def proper_monster_name(tag):
	m = get_monster(tag)
	return m['name']

def add_monster_databases():
	global monster_db
	files = glob.glob("./monsterdb.*.json")
	for f in files:
			try:
				with open(f,'r') as fin:
					mlst = json.load(fin)
				monster_db.update(mlst)
			except:
				log_message("Warning: Failed to load author monster database %s." % f)
				log_message("    Try using https://jsonlint.com to check the format of your file.")

def get_monster_manual():
	add_monster_databases()
	idx = get_monster_index()
	manual = [get_monster(m) for m in idx]
	return manual

def get_monster_index():
	global monsters_db
	return sorted(monster_db.keys())

files = glob.glob(os.environ['ADVMAKERPATH'] + "/database/monsterdb.*.json")
for f in files:
		try:
			with open(f,'r') as fin:
				mlst = json.load(fin)
			monster_db.update(mlst)
		except:
			log_message("Systems Warning: Failed to load monster database %s. Some monsters will be unavailable." % f)