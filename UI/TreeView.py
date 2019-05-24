"""
The mother of all, the tree
"""

from threading import Event 
from time import sleep

import wx

from Savegame \
	import Property
from Util \
	import Callback


class TreeView(wx.TreeCtrl):
	
	def __init__(self, parent):
		super().__init__(parent=parent, size=(300,400), \
						style=wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS|wx.TR_SINGLE)
		self.__event = Event()
		
	def __del__(self):
		del self.__event

	def setup(self, savegame, callback):
		self.__savegame = savegame
		self.__callback = callback
		
		#TODO: Count items avail in first pass, then add to tree as second pass
		#self.__total = len(self.__savegame.Objects) + len(self.__savegame.Collected)
		#self.__total *= 1000
		self.__total = 1 + len(self.__savegame.Objects)		
		for obj in self.__savegame.Objects:
			childs = obj.Childs
			if childs:
				self.__total += self._count_recurs(childs)
		self.__total += 1 + len(self.__savegame.Collected)
		
		self.__count = 0
		self.__packages = []
		self.__last_id = None
		
		self.__event.clear()
		
		self.__cb_start()
		
		root = self._add(None, self.__savegame.Filename, None)

		label ="Objects [{}]".format(len(self.__savegame.Objects))
		self.__objects = self._add(root, label, None)		
		for obj in self.__savegame.Objects:
			label = obj.Label #str(obj)
			itemid = self._add(self.__objects, label, obj)
			childs = obj.Childs
			if childs:
				self._add_recurs(itemid, childs)
		
		label = "Collected [{}]".format(len(self.__savegame.Collected))
		self.__collected = self._add(root, label, None)		
		for obj in self.__savegame.Collected:
			label = obj.Label #str(obj)
			self._add(self.__collected, label, obj)

		self.__cb_end()
		
		for pkg in self.__packages:
			del pkg
		self.__packages = None
		
	
	def process_event(self, event):
		if event.which == Callback.Callback.START:
			self.DeleteAllItems()
			
		elif event.which == Callback.Callback.UPDATE:
			if not event.data.Parent:
				# First item is treated as root
				#print("Trying to create root: ",'"'+event.data.Label+'"')
				#event.data.Info.Id 
				self.__last_id = self.AddRoot(event.data.Label)#, image=-1, selImage=-1, data=event.data.Info)
			else:
				# Rest are 'just' childs
				#print("Trying to create child: ",event.data.Parent,'"'+event.data.Label+'"')
				#event.data.Info.Id
				self.__last_id = self.AppendItem(event.data.Parent, event.data.Label, \
											image=-1, selImage=-1, data=event.data.Info)
			
		elif event.which == Callback.Callback.END:
			self.ScrollTo(self.RootItem)
			self.Expand(self.RootItem)

		# Signal we're ready
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
		
		info = TreeView.NodeInfo(ref, None)# No error info yet
		pkg = TreeView.EventPackage(parent, label, info)
		self.__packages.append(pkg)

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

		itemid = self.__last_id
		
		#self.__event.clear()
		
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



