zip AMinput.zip -r adventure.adv config.ini *.json fg/ pdf/ >tmp
curl --silent --output AMoutput.zip --data-binary "@AMinput.zip" http://app.dndal.club/advmaker/make
del AMinput.zip
del -rf finished/
unzip AMoutput.zip -o -d finished >tmp
del AMoutput.zip
more finished/logfile.txt
del tmp
