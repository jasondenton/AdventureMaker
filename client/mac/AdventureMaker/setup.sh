#!/bin/bash
STPATH=$HOME/Library/Application\ Support/Sublime\ Text\ 3/Packages
mkdir -p "$STPATH/AdventureMaker"
if [ ! -d "$STPATH/User" ]; then
	mkdir -p "$STPATH/User"
fi

cp AdvMaker.sublime-build "$STPATH/User"
cp advmaker.sh "$STPATH/AdventureMaker"
echo "Be sure to restart Sublime Text"
