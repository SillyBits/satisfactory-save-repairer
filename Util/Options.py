"""
Option handling
"""


import os

import wx


"""
TODO:
- Add some upgrading functionality in case format changes dramatically
  (so its a good idea to store at least some version info)
-
"""


class Options(wx.FileConfig):
	'''
	Wrapping wx.FileConfig with easy accessors
	'''

	def __init__(self, appname:str, apppath:str):
		inifile = os.path.join(apppath, appname + ".ini")
		super().__init__(appname, style=wx.CONFIG_USE_LOCAL_FILE, localFilename=inifile)
		wx.Config.Set(self)

		self.__mapping = {
			wx.ConfigBase.EntryType.Type_Float:   [ self.ReadFloat, self.WriteFloat ],
			wx.ConfigBase.EntryType.Type_Boolean: [ self.ReadBool , self.WriteBool  ],
			wx.ConfigBase.EntryType.Type_Integer: [ self.ReadInt  , self.WriteInt   ],
			wx.ConfigBase.EntryType.Type_String:  [ self.Read     , self.Write      ],
		}
		self.__names = {}

		if self.NumberOfEntries < 4:
			self.__setup()
		else:
			self.__load()


	'''
	Private implementation
	'''

	def __setup(self):
		#TODO: Also check if this instance needs an upgrade to a newer version
		self.__create("deep_analysis", False)
		self.__create("deep_analysis_asked", False)
		self.__create("incident_report", False)
		self.__create("incident_report_asked", False)


	def __load(self):
		more, name, index = self.GetFirstEntry()
		while more:
			self.__names[name] = self.GetEntryType(name)
			more, name, index = self.GetNextEntry(index)

	def __create(self, name, value):
		if isinstance(value, float):
			t = wx.ConfigBase.EntryType.Type_Float
		elif isinstance(value, bool):
			t = wx.ConfigBase.EntryType.Type_Boolean
		elif isinstance(value, int):
			t = wx.ConfigBase.EntryType.Type_Integer
		else:
			t = wx.ConfigBase.EntryType.Type_String

		self.__names[name] = t

		op = self.__mapping[t][Options.WRITE]
		op(name, value)


	def __getattr__(self, name):
		if name.startswith("_"):
			return super().__getattr__(name)
		if not name in self.__names:
			self.__create(name, "")
		t = self.__names[name]
		op = self.__mapping[t][Options.READ]
		return op(name)

	def __setattr__(self, name, value):
		if name.startswith("_"):
			super().__setattr__(name, value)
		else:
			if not name in self.__names:
				# Create new entries on-the-fly
				self.__create(name, value)
			else:
				t = self.__names[name]
				op = self.__mapping[t][Options.WRITE]
				op(name, value)


	READ = 0
	WRITE = 1



