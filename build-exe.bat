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

rem -F 								for a single executable (do NOT use this option, won't work due to resources folder)
rem -D 								for creating a whole folder infrastructure (needed with our resources folder!)
rem -n <name>						for naming the distribution
rem -w								for suppressing the console window
rem -i <file>						name of icon to include
rem --version-file <file>			include version info file
rem --add-data <folder>;<destname>	for adding extra data, e.g. resources
rem --exclude-module <name>			to force exclusion of module given (Dangerous: Will crash if missing one gets accessed)

rem set PYTHONOPTIMIZE=1

set pyi_options=-D -n SatisfactorySaveChecker -w --add-data .\Resources;Resources -i NoPack\Logo-128x128.ico --version-file NoPack\version.txt

REM set EE=--exclude-module
REM set pyi_excludes=%EE% bz2 %EE% lzma %EE% socket %EE% ssl %EE% select %EE% calendar
REM rem So far, seems to work still
REM 
REM set pyi_excludes=%pyi_excludes% %EE% xml %EE% email %EE% socketserver %EE% tty %EE% unittest %EE% socket 
REM rem Wow, still able to start
REM 
REM set pyi_excludes=%pyi_excludes% %EE% gzip %EE% tarfile %EE% zipfile %EE% zipimport 
REM rem Impressive, no startup error so far
REM 
REM set pyi_excludes=%pyi_excludes% %EE% ftplib %EE% http %EE% java %EE% netrc %EE% termios %EE% urllib
REM rem Ok, some failure
REM rem %EE% shutil == Required
REM rem Works again
REM 
REM set pyi_excludes=%pyi_excludes% %EE% difflib %EE% doctest %EE% gettext %EE% argparse %EE% getopt
REM rem Really, still working? Cool
REM 
REM rem This needs a change to Reporter.py first!!!
REM rem set pyi_excludes=%pyi_excludes% %EE% hashlib %EE% _md5 %EE% _sha512 %EE% _sha256
REM 
REM 
REM rem %EE% xml.sax %EE% six %EE% ast %EE% selectors %EE% abc 
REM rem set pyi_ex_codecs=%EE% _codecs_cn %EE% _codecs_hk %EE% _codecs_jp %EE% _codecs_kr %EE% _codecs_tw
REM rem %EE% base64 %EE% re

pyinstaller %pyi_options% %pyi_excludes% %pyi_ex_hashes% App.py
