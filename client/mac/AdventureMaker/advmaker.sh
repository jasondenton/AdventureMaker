#!/bin/bash
zip AMinput.zip -r adventure.adv config.ini *.json fg/ pdf/ >/dev/null
curl --silent --output AMoutput.zip --data-binary "@AMinput.zip" http://app.greatpanic.com/advmaker/make
if [ $? -ne 0 ]
then
        echo "Something went really wrong. Your document is probably broken in a way the error checking failed to catch."
        exit
fi

rm AMinput.zip
rm -rf finished/
unzip AMoutput.zip -d finished >/dev/null 
if [ $? -ne 0 ] 
then
        echo "Error unpacking the results. Something probably went wrong on the server." 
        echo "This might explain it:" 
        cat AMoutput.zip 
fi
rm AMoutput.zip
cat finished/logfile.txt
if [ -e "finished/adventure.pdf" ]; then
        open finished/adventure.pdf
fi