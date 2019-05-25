@echo off
set STPATH="C:%HOMEPATH%\AppData\Roaming\Sublime Text 3\Packages"
set AMPATH=%STPATH%\AdventureMaker"
mkdir %STPATH%\User
mkdir %AMPATH%

copy curl.exe %AMPATH%

copy zip.exe %AMPATH%
copy unzip.exe %AMPATH%

copy advmaker.bat %AMPATH%
copy AdvMaker.sublime-build %STPATH%\User

echo "Be sure to restart Sublime Text."