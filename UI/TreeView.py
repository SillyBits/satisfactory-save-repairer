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
	
	def __init__(self, parent, pane_func=None):
		super().__init__(parent=parent, size=(300,400), \
						style=wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS|wx.TR_SINGLE)
		self.__event = Event()
		self.__pane_func = pane_func
		if pane_func:
			self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onItemSelected)
		
	def __del__(self):
		if self.__pane_func:
			self.Unbind(wx.EVT_TREE_SEL_CHANGED)
		del self.__event

	def setup(self, savegame, callback):
		self.__savegame = savegame
		self.__callback = callback
		self.__count = 0
		self.__obj_map = {}
		
		self.__last_id = None
		self.__event.clear()
	
		# Count items avail in first pass, then add to tree as second pass
		self.__total = 1 + len(self.__savegame.Objects)		
		for obj in self.__savegame.Objects:
			childs = obj.Childs
			if childs:
				self.__total += self._count_recurs(childs)
		self.__total += 1 + len(self.__savegame.Collected)
		
		self.__cb_start()
		
		root = self._add(None, self.__savegame.Filename, None)
		
		label ="Objects [{}]".format(len(self.__savegame.Objects))
		self.__objects = self._add(root, label, None)
		
		# Early exit for faster debugging
		#self.__cb_end()
		#return

		for obj in self.__savegame.Objects:
			label = obj.Label
			itemid = self._add(self.__objects, label, obj)
			childs = obj.Childs
			if childs:
				self._add_recurs(itemid, childs)
		
		label = "Collected [{}]".format(len(self.__savegame.Collected))
		self.__collected = self._add(root, label, None)		
		for obj in self.__savegame.Collected:
			label = obj.Label
			itemid = self._add(self.__collected, label, obj)

		self.__cb_end()
		
	
	def process_event(self, event):
		itemid = None
		
		if event.which == Callback.Callback.START:
			self.DeleteAllItems()
			
		elif event.which == Callback.Callback.UPDATE:
			if not event.data.Parent:
				# First item is treated as root
				itemid = self.AddRoot(event.data.Label)#, image=-1, selImage=-1, data=event.data.Info)
			else:
				# Rest are 'just' childs
				itemid = self.AppendItem(event.data.Parent, event.data.Label, \
										image=-1, selImage=-1, data=event.data.Info)
			
		elif event.which == Callback.Callback.END:
			self.ScrollTo(self.RootItem)
			self.Expand(self.RootItem)

		# Signal we're ready
		self.__last_id = itemid
		self.__event.set()

	
	'''
	Private implementation
	'''

	def _count_recurs(self, childs):
		count = 0
		for name in childs:
			sub = childs[name]

			count += 1
			if isinstance(sub, (list,dict)):
				for obj in sub:
					count += 1
					childs = obj.Childs
					if childs:
						count += self._count_recurs(childs)
			else:
				childs = sub.Childs
				if childs:
					count += self._count_recurs(childs)

		return count

		
	def __cb_start(self):
		if self.__callback: self.__callback.start(self.__total)
		
	def __cb_update(self, pkg):
		if self.__callback: self.__callback.update(self.__count, pkg)
		
	def __cb_end(self):
		if self.__callback: self.__callback.end(True)


	def _add(self, parent, label, ref=None):
		#print("Trying to add: ",parent,'"'+label+'"',ref)
		self.__count += 1
		
		if ref:
			info = TreeView.NodeInfo(ref, None)# No error info yet
			pkg = TreeView.EventPackage(parent, label, info)
		else:
			pkg = TreeView.EventPackage(parent, label, None)

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


	def _add_recurs(self, parent, childs):
		for name in childs:
			sub = childs[name]

			if isinstance(sub, (list,dict)):
				label = "{} [{}]".format(name, len(sub))
				sub_parent = self._add(parent, label, None)
				for obj in sub:
					label = obj.Label #str(obj)
					itemid = self._add(sub_parent, label, obj)
					childs = obj.Childs
					if childs:
						self._add_recurs(itemid, childs)
			else:
				label = sub.Label
				itemid = self._add(parent, label, sub)
				childs = sub.Childs
				if childs:
					self._add_recurs(itemid, childs)


	def onItemSelected(self, event):
		assert self.__pane_func #!= None

		info = self.GetItemData(event.Item)
		prop = None
		if not info:
			if event.Item == self.RootItem:
				# Show header info
				prop = self.__savegame.Header
		elif info.Property:
			# Show info on property
			'''
			self.__pane_func(info.Property.Label+"\n\n"+str(info.Property))
			'''
			prop = info.Property
			
		'''
		For now, just list all keys and their values, if any avail.
		Next approach is to get UI elements based on type
		''' 
		s = ''
		if prop:
			for key in prop.Keys():
				s += "{}: {}\n".format(key, prop[key])
		self.__pane_func(s)
		
	
	class EventPackage:
		def __init__(self, parent, label, info):
			self.Parent = parent
			self.Label = label
			#self.style = ...
			self.Info = info 

	class NodeInfo:
		def __init__(self, sg_obj, err_obj):
			self.Property = sg_obj
			self.ErrorInfo = err_obj
			self.Id = None 



