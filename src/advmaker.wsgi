import os
import sys
APATH = '/var/www/AdventureMaker'
sys.path.insert(0, APATH +'/src')
os.environ['ADVMAKERPATH'] = APATH
os.environ['PATH'] = os.environ['PATH'] + ':/usr/local/texlive/2017/bin/x86_64-linux'
from application import app as application