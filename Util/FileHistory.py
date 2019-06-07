

from wx \
	import Menu, FileHistory, Config, EVT_MENU_RANGE

from wx.lib \
	import newevent


import AppConfig

from Util.Options \
	import Property


class FileHistoryHandler(FileHistory):
	"""
	Just to ease file history handling
	"""
	
	def __init__(self, menu, target, handler, persist=True, max_items=AppConfig.MAX_MRU):
		"""
		@param menu: Where to attach file history
		@param target: Target to use for event binding
		@param handler: Callback method to called on event
		@param persist: Whether or not to load from/save to config
		@param max_items: Number of menu items to support
		"""

		super().__init__(max_items)

		self.__menu = menu
		self.__target = target
		self.__handler = handler
		self.__persist = persist

		self.__menuitem = Menu()
		self.__menu.AppendSubMenu(self.__menuitem, _("Recently &used"))
		self.UseMenu(self.__menuitem)

		if self.__persist:
			self.__load()

		#self.AddFilesToMenu()

		EVT_MENU_RANGE.Bind(self.__target, 
							self.BaseId, self.BaseId + self.MaxFiles - 1, 
							self.__handler)


	def add(self, filename):
		self.AddFileToHistory(filename)

	def get(self, event):
		index = event.GetId() - self.BaseId
		return self.GetHistoryFile(index)

	def destroy(self):
		if self.__persist:
			self.__save()
		EVT_MENU_RANGE.Unbind(self.__target, 
							  self.BaseId, self.BaseId + self.MaxFiles - 1, 
							  self.__handler)



	'''
	Using our own load/save code as we've extended options to include type info
	'''

	def __load(self):
		cfg = Config.Get()

		for item in cfg.mru.items():
			if isinstance(item, Property):
				name = item.get()
				if name:
					self.AddFileToHistory(name)


	def __save(self):
		cfg = Config.Get()

		for obj in cfg.mru.items():
			obj.set("")

		for index in range(self.Count):
			filename = self.GetHistoryFile(index)
			cfg.mru.__setattr__("file{}".format(index+1), filename)



