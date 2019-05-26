"""
The mother of all, the tree
"""

from threading import Event 

import wx

#from Savegame \
#	import Property
from Util \
	import Callback


class TreeView(wx.TreeCtrl):
	
	def __init__(self, parent, pane=None):
		super().__init__(parent=parent, size=(300,400), \
						style=wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS|wx.TR_SINGLE)
		self.__event = Event()
		self.__pane = pane
		if pane:
			self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onItemSelected)
		self.__error_color = wx.Colour(255,0,0)

	def setup(self, savegame, callback):
		self.__savegame = savegame
		self.__callback = callback
		self.__count = 0
		self.__depth = 0 #TODO: Check for those in add_recurs
		self.__max_depth = 4
		self.__obj_map = {}
		
		self.__last_id = None
		self.__event.clear()
	
		total = self.__savegame.TotalElements		
		self.__cb_start(total)
		
		root = self.__add(None, self.__savegame.Filename, None)
		
		label = "Objects [{}]".format(len(self.__savegame.Objects))
		self.__objects = self.__add(root, label, None)
		
		# Early exit for faster debugging
		#self.__cb_end()
		#return

		for obj in self.__savegame.Objects:
			label = str(obj)#obj.Label
			itemid = self.__add(self.__objects, label, obj)
			childs = obj.Childs
			if childs:
				self.__add_recurs(itemid, childs)
		
		label = "Collected [{}]".format(len(self.__savegame.Collected))
		self.__collected = self.__add(root, label, None)		
		for obj in self.__savegame.Collected:
			label = str(obj)#obj.Label
			itemid = self.__add(self.__collected, label, obj)

		self.__cb_end()
		
	
	def process_event(self, event):
		itemid = None
		
		if event.which == Callback.Callback.START:
			self.DeleteAllItems()
			self.Enable(False)
			
		elif event.which == Callback.Callback.UPDATE:
			if not event.data.Parent:
				# First item is treated as root
				itemid = self.AddRoot(event.data.Label)#, image=-1, selImage=-1, data=event.data.Info)
			else:
				# Rest are 'just' childs
				itemid = self.AppendItem(event.data.Parent, event.data.Label, \
										image=-1, selImage=-1, data=event.data.Info)

				if event.data.Info and event.data.Info.Property.Errors:
					# Propagate error state up the tree
					hier = itemid
					while hier:
						if self.IsBold(hier):
							break # Propagated already
						self.SetItemBold(hier)
						self.SetItemTextColour(hier, self.__error_color)
						hier = self.GetItemParent(hier) 

		elif event.which == Callback.Callback.END:
			self.Enable(True)
			self.ScrollTo(self.RootItem)
			self.Expand(self.RootItem)

		# Signal we're ready
		self.__last_id = itemid
		self.__event.set()

	
	'''
	Private implementation
	'''

	def __cb_start(self, total):
		if self.__callback: self.__callback.start(total)
		
	def __cb_update(self, pkg):
		if self.__callback: self.__callback.update(self.__count, pkg)
		
	def __cb_end(self):
		if self.__callback: self.__callback.end(True)


	def __add(self, parent, label, ref=None):
		#print("Trying to add: ",parent,'"'+label+'"',ref)
		self.__count += 1
		
		if ref:
			info = TreeView.NodeInfo(ref)# Might add more info in future, so keep this as wrapper
		else:
			info = None
		
		pkg = TreeView.EventPackage(parent, label, info)

		'''		
		self.__event.clear()
		self.__cb_update(pkg)
		# Wait until callback signals that id is avail
		self.__event.wait(100)
		'''
		# Somewhat odd above doesn't work ... but ugly hack below does, so what -.-
		self.__event.clear()
		self.__last_id = None
		self.__cb_update(pkg)
		while not self.__last_id:
			self.__event.wait()

		del pkg
		
		itemid = self.__last_id
		if ref:
			# Link savegame object and item id to be able to find it later on 
			self.__obj_map[ref] = itemid
		
		return itemid


	def __add_recurs(self, parent, childs):
		for name in childs:
			sub = childs[name]

			if isinstance(sub, (list,dict)):
				label = "{} [{}]".format(name, len(sub))
				sub_parent = self.__add(parent, label, None)
				for obj in sub:
					label = str(obj)#obj.Label
					itemid = self.__add(sub_parent, label, obj)
					childs = obj.Childs
					if childs:
						self.__add_recurs(itemid, childs)
			else:
				label = str(sub)#sub.Label
				itemid = self.__add(parent, label, sub)
				childs = sub.Childs
				if childs:
					self.__add_recurs(itemid, childs)


	def onItemSelected(self, event):
		assert self.__pane #!= None

		info = self.GetItemData(event.Item)
		prop = None
		if not info:
			if event.Item == self.RootItem:
				# Show header info
				prop = self.__savegame.Header
		elif info.Property:
			# Show info on property
			'''
			self.__pane(info.Property.Label+"\n\n"+str(info.Property))
			'''
			prop = info.Property
			
		'''
		For now, just list all keys and their values, if any avail.
		Next approach is to get UI elements based on type
		'''
		""" 
		s = ''
		if info and info.Property.Errors:
			s = "Found errors in object:\n"
			for error in info.Property.Errors:
				s += "- " + error + "\n"
			s += "\n\n"
		if prop:
			for key in prop.Keys:
				s += "{}: {}\n".format(key, prop[key])
		self.__pane.update(s)
		"""
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



