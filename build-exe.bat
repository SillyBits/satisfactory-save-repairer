@echo off

if exist .\build (
	echo Cleaning old .\build folder...
	rmdir /s /q .\build 
	rem > nul
)
if exist .\dist (
	echo Cleaning old .\dist folder...
	rmdir /s /q .\dist 
	rem > nul
)

rem pause
rem goto:eof

rem -F 							for a single executable (do NOT use this option, won't work due to resources folder)
rem -D 							for creating a whole folder infrastructure (needed with our resources folder!)
rem -n <name>					for naming the distribution
rem -w							for suppressing the console window
rem -i <file>					name of icon to include
rem --version-file <file>		include version info file

set pyi_options=-D -n SatisfactorySaveChecker -w --add-data .\Resources;Resources -i NoPack\Logo-128x128.ico --version-file NoPack\version.txt

pyinstaller %pyi_options% App.py
