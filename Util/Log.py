"""
Basic logging
"""

import os
from datetime \
	import datetime



LOG_DEBUG = 0
LOG_INFO  = 1
LOG_ERROR = 2

	
__logpath = None
__logfile = None

__log_min_severity = -1
__log_severity = [ "DEBUG", "INFO", "ERROR" ]	

def InitLog(self, appname, apppath, min_severity=LOG_INFO):
	__log_min_severity = min_severity

	__logpath = os.path.join(apppath, "logs")
	
	if not os.path.isdir(__logpath):
		os.mkdir(__logpath)
		
	__logfile = os.path.join(__logpath, appname + ".log")

	if os.path.isfile(__logfile):
		mtime = datetime.fromtimestamp(os.path.getmtime(__logfile))
		backupfile = appname + "-" + mtime.strftime("%Y%m%d-%H%M%S") + ".log"
		os.rename(__logfile, os.path.join(__logpath, backupfile))

	return __logfile


def Log(text:str, add_ts:bool=True, add_newline:bool=True, severity=LOG_INFO):
	if severity < __log_min_severity:
		return

	s = ""
	if add_ts:
		s = "[{}]".format(datetime.now())
	s += "[" + __log_severity[severity] + "] "

	s += text
	if add_newline:
		s += "\n"
		
	print(s, end='')

