"""
Static configs for application
"""

from os import environ
DEBUG = True and "SSR_DEBUG" in environ
#DEBUG = False

#APP_NAME = "SatisfactorySaveRepairer"
#APP_TITLE = "Satisfactory Savegame Repairer"
APP_NAME = "SatisfactorySaveChecker"
APP_TITLE = "Satisfactory Savegame Checker"

CURR_VERSION = "v0.3-alpha"

SHOW_TREE = True

VALIDATE = False

MAX_MRU = 9
