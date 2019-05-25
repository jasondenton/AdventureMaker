from zipfile import ZipFile, ZIP_DEFLATED
from os import rename, chdir, getcwd, listdir
from shutil import copytree
import os.path
from copy import deepcopy
from advdoc import ParseAdventureDocument, DebugAdventureDocument
from latexengine import LaTeXOutputEngine
from fantasygrounds import FantasyGroundsOutputEngine
from subprocess import Popen, PIPE
from logger import *
from simpleconfig import load_configuration

from monsters import add_monster_databases
from npc import add_npc_databases
from sidebar import add_sidebar_databases
from magicitems import add_magicitem_databases
from bibliography import add_bib_databases
from spells import add_spell_databases

DEFAULT_CONFIG_FILE = {
	'output' : {
		'stage' : 'draft',
		'style' : None
	},
	'auth' : {
		'password' : None
	},
	'beta' : {}
}

#zip format
#top level, no directory
#adventure.txt
#*.json
#pdf/ + *.jpeg/*.jpg/*.png
#fg/ + *.jpeg/*.jpg/*.png

def add_author_databases():
	add_npc_databases()
	add_magicitem_databases()
	add_spell_databases()
	add_bib_databases()
	add_sidebar_databases()
	add_monster_databases()

def ZipFromList(zfile, contents):
	with ZipFile(zfile, 'w', ZIP_DEFLATED) as fout:
		for f in contents:
			fout.write(f)

files_latexed = 0
def Latex2PDF(infile, maxruns=15):
	global files_latexed
	files_latexed += 1
	found = 1
	runs = 0
	texfile = 'tmp_%d.tex' % files_latexed
	pdffile = 'tmp_%d.pdf' % files_latexed
	(basename,ext) = os.path.splitext(infile)
	rename(infile, texfile)
	while found != -1 and runs < maxruns:
		proc = Popen(['pdflatex', '-halt-on-error', '-interaction=nonstopmode', texfile],
			stderr=PIPE,stdin=None,stdout=PIPE)
		(out,err) = proc.communicate()
		found = out.find('Label(s) may have changed')
		if found != -1:
		 	found = out.find('rerunfilecheck')
		runs += 1
	if not os.path.exists(pdffile):
		efile = basename + '.err'
		with file(efile, 'w') as fout:
			fout.write(out)
			fout.write('\n\n------\n\n')
			fout.write(err)
		return efile
	ffile = basename + '.pdf'
	cmdline = ['gs', '-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/printer', '-dNOPAUSE', 
	'-dQUIET', '-dBATCH', '-sOutputFile=%s' % ffile, pdffile]
	proc = Popen(cmdline, stderr=PIPE,stdin=None,stdout=PIPE)
	(out,err) = proc.communicate()
	return ffile

EXPERT_MODE_FILES = [
	'dnd.sty',
	'small_logo.png'
]

def all_art_present(doc):
	have = os.listdir('.')
	missing = []
	for img in doc['artwork']:
		if img not in have:
			missing.append(img)
	if not missing: return True
	log_message("Error: Some required artwork was missing.")
	for m in missing:
		log_message("    Image file %s referenced but not present." % m)
	return False

#requires pwd=temp directory where input unpacked
def GenPDF(advtext, config):
	global EXPERT_MODE_FILES
	if not os.path.exists('pdf'):
		os.mkdir('pdf')
	doc = deepcopy(advtext)
	doc['intvars']['template'] = config['template']
	doc['intvars']['style'] = config['style']
	#try:
	with open('pdf/adventure.tex', 'w') as latexfile, open('pdf/itemcerts.tex', 'w') as itemfile, open('pdf/storycerts.tex', 'w') as storyfile:
		latex = LaTeXOutputEngine(latexfile, storyfile, itemfile)
		latex.format(doc)
	#except Exception as exp:
	#	log_message('Error: Problem producing intermediate source for pdf file.')
	#	return []
	files = []
	tmp = os.getcwd()
	os.chdir('pdf')
	texin = ['adventure.tex']
	if config['makecerts']:
		if doc['intvars']['has_story_awards']: texin.append('storycerts.tex')
		if doc['intvars']['has_itemcerts']: texin.append('itemcerts.tex')
	hasart = all_art_present(advtext)
	if not hasart:
		log_message("Warning: Adventure not generated because some images are missing from pdf directory.")
	if not config['makepdf']:
		log_message('No PDF files requested.')
	if hasart and config['makepdf']:
		for f in texin:
			res = Latex2PDF(f)
			rename(res, '../%s' % res)
			files.append(res)
	if config['sendtex']: 
		log_message('Notice: LaTeX sources provided.')
		EXPERT_MODE_FILES += texin
		for f in EXPERT_MODE_FILES:
			rename(f,'../'+f)
			files.append(f)
	os.chdir(tmp)
	return files

#requires pwd=temp directory where input unpacked
def GenFGMod(advtext, config):
	if not config['makefg']:
		log_message('Set the output stage in config.ini to "publish" to enable Fantasy Grounds mod file production.')
		return []
	if not os.path.exists('fg'):
		os.mkdir('fg')

	doc = deepcopy(advtext)
	try:
		with open('fg/db.xml', 'w') as fgdb, open('fg/definition.xml', 'w') as fgdef:
			fantg = FantasyGroundsOutputEngine(fgdb, fgdef)
			fantg.format(doc)		
	except Exception as exp:
		log_message('Error: Problem producing fantasy grounds module.')
		raise
	tmp = getcwd()
	chdir('fg')
	ZipFromList('../adventure.mod', listdir('.'))
	os.chdir(tmp)
	return ['adventure.mod']

def GetConfiguration():
	config = {
		'makepdf' : True,
		'sendtex' : False,
		'template' : 'adventure',
		'makefg' : False,
		'makecerts' : False,
		'style' : None
	}

	try:
		cf = load_configuration('config.ini',DEFAULT_CONFIG_FILE)
		print cf
		st = cf['output']['stage'].lower()

		if st == 'proof':
			config['template'] = 'proof'
		if st == 'publish':
			config['makefg'] = True
			config['makecerts'] = True
		if st == 'expert':
			config['makepdf'] = False
			config['sendtex'] = True
			config['makecerts'] = True
		if st == 'fgonly':
			config['makepdf'] = False
			config['makefg'] = True
		if st == 'pod':
			config['template'] = 'adventure_pod'
		if cf['output']['style']:
			config['style'] = cf['output']['style']
		return config
	except Exception as e:
		print e
		log_message("Error reading configuration file. Nothing done.\n")
		return None


def AdventureFromZip(tempdir): 
	workdir = tempdir + '/work'
	copytree(os.environ['ADVMAKERPATH']+'/assets',workdir)
	os.chdir(workdir)

	terminal = False
	try:
		with ZipFile(tempdir+'/input.zip', 'r') as zp:
			zp.extractall()
	except IOError as exp:
		log_message('Error: Problem unpacking input bundle. Check the inputs for your adventure and try again.')
		terminal = True

	if not terminal:
		config = GetConfiguration()
		if not config: terminal = True

	if not terminal:
		add_author_databases()
		try:
			with open('adventure.adv') as fin:
				raw = fin.readlines()
		except Exception as exp:
				log_message('Error: Problem reading adventure.adv. Is the file present?')
				terminal = True
		scrubbed = []
		lno = 1
		try:
			for line in raw:
				t = line.encode('ascii','replace')
				scrubbed.append(t.strip())
				lno += 1
		except Exception as exp:
				log_message('Error: Problem decoding text on line %d. Make sure you do not have any non-ascii characters in your document.' % lno)
				log_message('Usually, this error means you have copy and pasted text from Word, and used a "fancy" apostrophe, quote, or double quote.')
				log_message('You can fix this error by finding the offending symbol, deleting it, re-typing it in a plain text editor (like Sublime or Notepad).')
				terminal = True

	filesback = []
	doc = None
	if not terminal:
		if (os.getenv('ADVMAKERDEBUG') == 'ACTIVE'):
			print ("-- DEBUG CODE PATH --")
			doc = DebugAdventureDocument(scrubbed)
		else:
			doc = ParseAdventureDocument(scrubbed)
		if doc:
			filesback += GenFGMod(doc, config)
			filesback += GenPDF(doc, config)
		else:
			log_message('Problem with adventure.adv file. No files generated.')

	flush_log('logfile.txt')
	filesback.append('logfile.txt')
	ZipFromList(tempdir+'/output.zip', filesback)
	if doc:
		return doc['variables']['title'] + ' by ' + doc['variables']['author']
	else:
		return "Error"

def MonsterManualForSystem(tempdir):
	workdir = tempdir + '/work'
	copytree(os.environ['ADVMAKERPATH']+'/assets',workdir)
	os.chdir(workdir+'/pdf')

	latex = LaTeXOutputEngine(None, None, None)
	latex.create_monster_manual()
	fname = Latex2PDF('mm.tex')
	return '%s/pdf/%s' % (workdir,fname)

def MonsterCardForSystem(tempdir):
	workdir = tempdir + '/work'
	copytree(os.environ['ADVMAKERPATH']+'/assets',workdir)
	os.chdir(workdir+'/pdf')

	latex = LaTeXOutputEngine(None, None, None)
	latex.create_monster_card()
	fname = Latex2PDF('card.tex')
	return '%s/pdf/%s' % (workdir,fname)
