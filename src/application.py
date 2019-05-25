#!/usr/bin/python
import os
from tempfile import mkdtemp, mkstemp
from shutil import rmtree
from datetime import datetime

from flask import Flask, jsonify, request

from advzip import AdventureFromZip, MonsterManualForSystem, MonsterCardForSystem
from monsters import get_monster_index
from spells import get_spell_index
from npc import get_npc_list
from magicitems import get_item_list
from bibliography import get_library
from sidebar import get_sidebar_list



app = Flask(__name__)

@app.route('/')
def rootpage():
	return os.environ['ADVMAKERPATH']

@app.route('/monsters')
def monster_list():
    return jsonify(get_monster_index())

@app.route('/spells')
def spell_list():
	return jsonify(get_spell_index())

@app.route('/npcs')
def npc_list():
	return jsonify(get_npc_list())

@app.route('/magicitems')
def item_list():
	return jsonify(get_item_list())

@app.route('/bibliography')
def bibliography():
	return jsonify(get_library())

@app.route('/sidebars')
def sidebars():
	return jsonify(get_sidebar_list())

@app.route('/make',methods=['POST'])
def make():
	workdir = mkdtemp(suffix='am', prefix='tmp')
	with open(workdir+'/input.zip','w') as fout:
		fout.write(request.stream.read())
	result = AdventureFromZip(workdir)
	data = open(workdir+'/output.zip','r')
	response = app.response_class(response=data.read(),status=200,mimetype='application/zip')
	data.close()
	#with open(os.environ['ADVMAKERPATH']+'/log/run.txt','a') as logout:
	#	logout.write(str(datetime.now())+'\t'+result+'\n')
#	rmtree(workdir,ignore_errors=True)
	return response

@app.route('/monstermanual')
def monstermanual():
	workdir = mkdtemp(suffix='mm', prefix='tmp')
	result = MonsterManualForSystem(workdir)
	data = open(result,'r')
	with open('/tmp/mm.pdf','w') as fout:
		fout.write(data.read())
	data.close()
	data = open(result,'r')
	response = app.response_class(response=data.read(),status=200,mimetype='application/pdf')
	data.close()
	#with open(os.environ['ADVMAKERPATH']+'/log/run.txt','a') as logout:
	#	logout.write(str(datetime.now())+'\t'+result+'\n')
	rmtree(workdir,ignore_errors=True)
	return response

@app.route('/shutdown')
def shutdown():
	request.environ.get('werkzeug.server.shutdown')()
	return 'Server shutting down...\n'
