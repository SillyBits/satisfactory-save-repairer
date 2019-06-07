"""
Language-related stuff

Own implementation as gettext and such is way too big for such a small project
"""

import sys
import os

import json

import wx

from Util \
	import Log


"""
TODO:
Even if this .json format is ok now now, find some other format which is easy to maintain
and also allows for pseudo-groups and comments to assist with translating stuff.
"""
 
class Lang:

	LANG = None	
	LANGTABLE = {}
	
	@staticmethod
	def load(lang:str, folder:str):
		if lang is None:
			syslang = wx.Locale.GetSystemLanguage()
			if syslang == wx.LANGUAGE_GERMAN:
				lang = "de_DE"
			else:
				lang = "en_US"
		Lang.LANG = lang

		if lang != "en_US":
			Lang.LANGTABLE = {}
			filename = os.path.join(folder, lang, "lang.dat")
			with open(filename, "rt", encoding="UTF-8") as file:
				content = json.load(file)
				Lang.LANGTABLE = content

	@staticmethod
	def translate(*source):
		if Lang.LANG == "en_US":
			return ''.join(source)

		trans = ""
		for entry in source:
			if entry in ("\n","\t"):
				trans += entry
			elif entry in Lang.LANGTABLE:
				trans += Lang.LANGTABLE[entry]
			else:
				Log.Log(u"Missing translation for: " + entry,
					severity=Log.LOG_ERROR)
		return trans




import builtins
builtins.__dict__['_'] = Lang.translate
