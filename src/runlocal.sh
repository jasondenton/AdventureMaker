#!/bin/bash
export FLASK_APP="application.py"
export ADVMAKERPATH="`pwd`/.."
export ADVMAKERDEBUG="ACTIVE"
flask run
