"""
Option handling, wrapping :class:`wx.FileConfig` to allow for hierarchical access like
``cfg.deep_analysis.enabled = False``

@author: SillyBits
@copyright: (c)2019 SillyBits
@contact: https://github.com/SillyBits
@license: GPL
@version: 1.0
"""


from os \
	import path

from wx \
	import Config, ConfigBase, FileConfig, CONFIG_USE_LOCAL_FILE


class Options(FileConfig):
	"""
	@param appname: Name of application, used to define name of .ini to process
	@param apppath: Path where .ini should be stored
	"""

	def __init__(self, appname:str, apppath:str):
		inifile = path.join(apppath, appname + ".ini")
		super().__init__(appname, style=CONFIG_USE_LOCAL_FILE, localFilename=inifile)
		Config.Set(self)

		self.__root = Container("/")

		self.__setup()


	'''
	Private implementation
	'''

	def __setup(self):
		num = self.GetNumberOfEntries(True)
		if num < 5:
			# Create initial config
			self.version = "v0.3-alpha"
			self.deep_analysis.enabled = False
			self.deep_analysis.asked = False
			self.incident_report.enabled = False
			self.incident_report.asked = False
			self.Flush()
			return
		# Upgrade existing
		#TODO:


	def __getattr__(self, name:str):
		if name.startswith("_"):
			try:
				return FileConfig.__getattribute__(self, name)
			except:
				pass
		return self.__root.get(name, None)

	def __setattr__(self, name:str, value):
		if name.startswith("_"):
			try:
				return FileConfig.__setattr__(self, name, value)
			except:
				pass
		return self.__root.set(name, value)


class Container:

	def __init__(self, path:str):
		self.__path = path
		self.__load()


	def get(self, name:str, default):
		if not name in self.__dict__:
			return self.__create(name, default)
		obj = object.__getattribute__(self, name)
		if isinstance(obj, Property):
			obj = obj.get()
		return obj

	def set(self, name:str, value):
		if not name in self.__dict__:
			return self.__create(name, value)
		obj = object.__getattribute__(self, name)
		if isinstance(obj, Property):
			obj = obj.set(value)
		return obj


	'''
	Private implementation
	'''

	def __str__(self):
		s = self.__class__.__qualname__ + " @ " + self.__path
		return s

	def __load(self):
		#vvvvv DEBUG
		## We must copy ourself, no .copy() avail, sadfully
		#prev_dict = [ key for key in self.__dict__.keys() ]
		#^^^^^ DEBUG

		last_path = Config.Get().GetPath()
		Config.Get().SetPath(self.__path)

		more, name, index = Config.Get().GetFirstEntry()
		while more:
			if SEPARATOR in name:
				path = self.__path + name
				name,t = name.split(SEPARATOR)
				t = t[0].lower()
			else:
				# Note: We should run into this only with very old configs!
				# Convert wx.Config type mapping to our types
				# (ends up in string always as FileConfig has no real types)
				t = Config.Get().GetEntryType(name)
				if t in WX_MAPPING:
					t = WX_MAPPING[t]
				else:
					t = STRING
				path = self.__path + name + SEPARATOR + t

			prop = TYPE_MAPPING[t](path)
			self.__dict__[name] = prop

			more, name, index = Config.Get().GetNextEntry(index)

		# Not sure what happens if we do change path while enumerating,
		# so we will do this in 2 phases: Gather first, create last
		groups = []
		more, name, index = Config.Get().GetFirstGroup()
		while more:
			groups.append(name)
			more, name, index = Config.Get().GetNextGroup(index)

		for name in groups:
			container = Container(self.__path + name + "/")
			self.__dict__[name] = container

		Config.Get().SetPath(last_path)

		#vvvvv DEBUG
		#print("members for path {}:".format(self.__path))
		#for n in self.__dict__:
		#	if n not in prev_dict:
		#		print("-",n,":",self.__dict__[n])
		#^^^^^ DEBUG


	def __create(self, name:str, value):
		if "/" in name or value is None:
			new_group = name.split("/", maxsplit=1)[0]
			container = Container(self.__path + new_group + "/")
			self.__dict__[new_group] = container
			if name == new_group:
				# We're done
				return container
			# More keys waiting
			remain = name[len(new_group)+1:]
			return container.__create(remain, value)

		if isinstance(value, float):
			t = FLOAT
		elif isinstance(value, bool):
			t = BOOL
		elif isinstance(value, int):
			t = INT
		else:
			t = STRING

		path = self.__path + name + SEPARATOR + t
		prop = TYPE_MAPPING[t](path, value)
		self.__dict__[name] = prop
		return prop.set(value)


	def __getattr__(self, name:str):
		if name.startswith("_"):
			try:
				return object.__getattribute__(self, name)
			except:
				pass
		return self.get(name, None)

	def __setattr__(self, name:str, value):
		if name.startswith("_"):
			try:
				return object.__setattr__(self, name, value)
			except:
				pass
		return self.set(name, value)


class Property:
	def __init__(self, path:str, default=None):
		self.path = path
		self.default = default


	def get(self):			pass
	def set(self, value):	pass


	'''
	Private implementation
	'''

	def __str__(self):
		s = self.__class__.__qualname__ + " @ " + self.path
		if self.default is not None:
			s += " (default='{}')".format(self.default)
		return s

	def __lt__(self, other): return self.get() <  other
	def __le__(self, other): return self.get() <= other
	def __eq__(self, other): return self.get() == other
	def __ne__(self, other): return self.get() != other
	def __gt__(self, other): return self.get() >  other
	def __ge__(self, other): return self.get() >= other
	#def __bool__(self):      return self.get() == True


class FloatProperty(Property):
	def get(self):			return Config.Get().ReadFloat (self.path, self.default or 0.0)
	def set(self, value):	return Config.Get().WriteFloat(self.path, value)
	def __float__(self):    return self.get()

class BoolProperty(Property):
	def get(self):			return Config.Get().ReadBool (self.path, self.default or False)
	def set(self, value):	return Config.Get().WriteBool(self.path, value)
	def __bool__(self):     return self.get()

class IntProperty(Property):
	def get(self):			return Config.Get().ReadInt (self.path, self.default or 0)
	def set(self, value):	return Config.Get().WriteInt(self.path, value)
	def __int__(self):      return self.get()

class StringProperty(Property):
	def get(self):			return Config.Get().Read (self.path, self.default or "")
	def set(self, value):	return Config.Get().Write(self.path, value)
	def __str__(self):      return self.get()


SEPARATOR = "." # Using ":" has negative side effect of being escaped -> version\:s=...

FLOAT   = "f"
BOOL    = "b"
INT     = "i"
STRING  = "s"

WX_MAPPING = {
	ConfigBase.EntryType.Type_Float  : FLOAT,
	ConfigBase.EntryType.Type_Boolean: BOOL,
	ConfigBase.EntryType.Type_Integer: INT,
	ConfigBase.EntryType.Type_String : STRING,
}

TYPE_MAPPING = {
	FLOAT : FloatProperty,
	BOOL  : BoolProperty,
	INT   : IntProperty,
	STRING: StringProperty,
}


