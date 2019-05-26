"""
Language-related stuff

Own implementation as gettext and such is way too big for such a small project
"""

import sys
import os

import json

import wx


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
	def translate(source:str):
		if Lang.LANG != "en_US":
			if source in Lang.LANGTABLE:
				return Lang.LANGTABLE[source]
			print(u"Missing translation for: " + source)
		return source


import builtins
builtins.__dict__['_'] = Lang.translate
