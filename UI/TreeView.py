"""
The mother of all, the tree
"""

from threading import Event 


import wx


from UI \
	import ProgressDlg


class TreeView(wx.TreeCtrl):

	TYPE_RAW = 0
	TYPE_BY_CLASSNAME = 1
	FLAG_DEFECTIVES_ONLY = 0x80
	
	def __init__(self, parent, pane=None, visualize=TYPE_RAW):
		super().__init__(parent=parent, size=(300,400), \
						style=wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS|wx.TR_SINGLE)
		self.__event = Event()
		self.__pane = pane
		self.__type = visualize
		if pane:
			self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onItemSelected)
		self.__error_color = wx.Colour(255,0,0)
		self.__progress = TreeView.Progress(self)
		self.__curr_sel = None


	def setup(self, savegame, callback):
		self.__savegame = savegame
		self.__count = 0
		self.__obj_map = {}

		self.__last_id = None
		self.__event.clear()

		if self.__type == TreeView.TYPE_RAW:
			total = 3 + len(self.__savegame.Objects) + len(self.__savegame.Collected)
			if self.__savegame.Missing:
				total += 1		
			self.__cb_start(total, _("Building tree..."))
	
			root = self.__add(None, self.__savegame.Filename, None)
	
			label = "Objects [{}]".format(len(self.__savegame.Objects))
			self.__objects = self.__add(root, label, None)
	
			label = "Collected [{}]".format(len(self.__savegame.Collected))
			self.__collected = self.__add(root, label, None)		
	
			for obj in self.__savegame.Objects:
				label = str(obj)
				self.__add(self.__objects, label, obj)
	
			for obj in self.__savegame.Collected:
				label = str(obj)
				self.__add(self.__collected, label, obj)
	
			if self.__savegame.Missing:
				label = "Missing"
				self.__add(self.root, label, self.__savegame.Missing)
	
			self.__cb_end()


		elif self.__type == TreeView.TYPE_BY_CLASSNAME:
			self.__classes = {}

			# The static number is a rough estimate on number of extra nodes
			total = 150 + len(self.__savegame.Objects) + len(self.__savegame.Collected)
			#if self.__savegame.Missing:
			#	total += 1		
			self.__cb_start(total, _("Building tree..."))
	
			root = self.__add(None, self.__savegame.Filename, None)

			for obj in self.__savegame.Objects:
				self.__add_class_recurs(root, "/", obj)

			#for obj in self.__savegame.Collected:
			#	self.__add_class_recurs(root, "/", obj)
	
			#if self.__savegame.Missing:
			#	label = "Missing"
			#	self.__add(self.root, label, self.__savegame.Missing)

			self.__cb_end()


	@property
	def Type(self):
		return self.__type

	@property
	def Classes(self):
		return self.__classes


	'''
	Private implementation
	'''

	def __cb_start(self, total, status=None, info=None):
		self.__progress.start(maxval=total, status=status, info=info)

	def __cb_update(self, pkg, status=None, info=None):
		self.__progress.update(val=self.__count, status=status, info=info, data=pkg)

	def __cb_end(self):
		self.__progress.end(state=True)

	def signal(self, itemid):
		self.__last_id = itemid
		self.__event.set()


	def __add(self, parent, label, ref=None):
		self.__count += 1

		if ref:
			# Might add more info in future, so keep this as wrapper
			info = TreeView.NodeInfo(ref)
		else:
			info = None
			
		pkg = TreeView.EventPackage(parent, label, info)
		self.__cb_update(pkg, None, label)

		if not ref:
			while not self.__last_id:
				self.__event.wait(0.000001)
			return self.__last_id

	def __add_class_recurs(self, parent_item, parent_class, prop):
		remain = prop.ClassName[len(parent_class):]
		if "/" in remain:
			classname = remain.split("/", 1)[0]
			fullname = parent_class + classname + "/"
			#if not fullname in self.__classes:
			#	class_item = self.__add(parent_item, classname)
			#	self.__classes[fullname] = class_item
			#else:
			#	class_item = self.__classes[fullname]
			class_item = self.__add_or_get_class(parent_item, fullname, classname)
			return self.__add_class_recurs(class_item, fullname, prop)

		if "." in remain:
			classnames = remain.split(".")
			if len(classnames) == 2:
				if classnames[0] + "_C" == classnames[1]:
					# Ignore [1]
					#return self.__add(parent_item, classnames[0], prop)
					fullname = parent_class + classnames[0] + "."
					classname = classnames[0]
					class_item = self.__add_or_get_class(parent_item, fullname, classnames[0])
				else:
					# Add both?
					fullname = parent_class + classnames[0] + "."
					class_item = self.__add_or_get_class(parent_item, fullname, classnames[0])
					
					fullname += classnames[1]
					class_item = self.__add_or_get_class(class_item, fullname, classnames[1])

				label = ".".join(prop.PathName.split(".")[1:])
				return self.__add(class_item, label, prop)
				
			print("__add_class_recurs: What to do with\n-> {}?".format(prop.ClassName))
		"""
			fullname = parent_class + classname + "."
			if not fullname in self.__classes:
				class_item = self.__add(parent_item, classname)
				self.__classes[fullname] = class_item
			else:
				class_item = self.__classes[fullname]
			return self.__add_class_recurs(class_item, fullname, prop)

		"" "
		if prop.ClassName.startswith("/Script/") and remain:
			fullname = prop.ClassName
			if not fullname in self.__classes:
				class_item = self.__add(parent_item, remain)
				self.__classes[fullname] = class_item
			else:
				class_item = self.__classes[fullname]
			parent_item = class_item
		"""

		# At the end of our path, now add property
		#return self.__add(parent_item, remain, prop)
		#label = prop.PathName.split(".")[1:]
		label = ".".join(prop.PathName.split(".")[1:])
		return self.__add(parent_item, label, prop)

	def __add_or_get_class(self, parent_item, fullname, classname):
		if not fullname in self.__classes:
			class_item = self.__add(parent_item, classname)
			self.__classes[fullname] = class_item
		else:
			class_item = self.__classes[fullname]
		return class_item


	def onItemSelected(self, event):
		assert self.__pane #!= None

		if self.__curr_sel == event.Item:
			return
		self.__curr_sel = event.Item

		info = self.GetItemData(event.Item)
		prop = None
		if not info:
			if event.Item == self.RootItem:
				# Show header info
				prop = self.__savegame.Header
		elif info.Property:
			# Show info on property
			prop = info.Property

		self.__pane.show_property(prop)


	class EventPackage:
		def __init__(self, parent, label, info):
			self.Parent = parent
			self.Label = label
			#self.style = ...
			self.Info = info 

	class NodeInfo:
		def __init__(self, sg_obj):
			self.Property = sg_obj


	class Progress(ProgressDlg.ProgressDlg):
		def __init__(self, control):
			self.__control = control
			super().__init__(parent=wx.App.Get().GetTopWindow(), 
							caption=_("Object tree"), 
							counts_format=_("{:,d} / {:,d} objects"))

		def onStart(self, maxval, status, info):
			ProgressDlg.ProgressDlg.onStart(self, maxval, status, info)
			self.__control.DeleteAllItems()
			self.__control.Enable(False)

		def onUpdate(self, val, status, info, data=None):
			ProgressDlg.ProgressDlg.onUpdate(self, val, status, info)
			if not data.Parent:
				# First item is treated as root
				itemid = self.__control.AddRoot(data.Label)
				self.__control.signal(itemid)
			else:
				# Rest are 'just' childs
				itemid = self.__control.AppendItem(data.Parent, data.Label, \
										image=-1, selImage=-1, data=data.Info)
				if not data.Info:
					self.__control.signal(itemid)

		def onEnd(self, state, status, info):
			if self.__control.Type == TreeView.TYPE_BY_CLASSNAME:
				# Update counts on those groups
				for itemid in self.__control.Classes.values():
					label = "{} [{}]".format(self.__control.GetItemText(itemid),
											self.__control.GetChildrenCount(itemid, False))
					self.__control.SetItemText(itemid, label)

			ProgressDlg.ProgressDlg.onEnd(self, state, status, info)
			self.__control.Enable(True)
			self.__control.ScrollTo(self.__control.RootItem)
			self.__control.Expand(self.__control.RootItem)



