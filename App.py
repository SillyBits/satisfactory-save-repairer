#!/usr/bin/env python3
'''
Handy GUI for dealing with corrupted Satisfactory saves.
'''

import sys
import os
import threading

import wx


from Savegame import Savegame
	 
from Util \
	import Options, Callback

from UI \
	import OptionsDlg, AboutDlg, TreeView


class Application(wx.App):
	def __init__(self):
		super().__init__(False)


class MainFrame(wx.Frame):

	currFile = None
	

	def __init__(self, parent=None):
		super().__init__(parent, title="Satisfactory savegame repair", size=(800,480))
		#self.pack(fill=BOTH, expand=Y)
		#self.master.title(self.get_title())
		#self.master.minsize(640,480)
		#self.columnconfigure(0, weight=1, minsize=400)
		#self.rowconfigure(0, weight=1, minsize=300)
		self.create_widgets()
		
		# Finally, update UI
		#self.update_extract_location()
		self.update_ui()
		#self.update_tree()

		self.Show()
		self.set_idle()


	'''
	UI generation
	'''

	def create_widgets(self):
		self.create_menubar(self)
		self.create_toolbars(self)
		self.create_content(self)
		self.create_statusbar(self)

	def create_menubar(self, parent):
		self.menuBar = wx.MenuBar()
		self.SetMenuBar(self.menuBar)

		def _add(menu, label, tooltip=None, func=None, id=wx.ID_ANY):
			item = menu.Append(id, label, tooltip)
			if func: self.Bind(wx.EVT_MENU, func, item)
			return item

		filemenu = wx.Menu()
		self.menuBar.Append(filemenu, "&File")
		_add(filemenu, "&Open...", "Opens a save game", self.onFileOpen)
		_add(filemenu, "&Save", "Saves changes", self.onFileSave)
		_add(filemenu, "Save &as...", "Saves changes into a different file", self.onFileSaveAs)
		_add(filemenu, "C&lose", "Closes save, will prompt if pending changes detected", self.onFileClose)
		filemenu.AppendSeparator()
		_add(filemenu, "E&xit", "Terminate program", self.onFileExit, wx.ID_EXIT)

		editmenu = wx.Menu()
		self.MenuBar.Append(editmenu, "E&dit")
		_add(editmenu, "&Options...", "OPens options dialog", self.onEditOptions)
		
		helpmenu = wx.Menu()
		self.menuBar.Append(helpmenu, "&Help")
		_add(helpmenu, "&About", "Information about this program", self.onHelpAbout, wx.ID_ABOUT)

	def create_toolbars(self, parent):
		pass

	def create_statusbar(self, parent):
		self.statusbar = self.CreateStatusBar(style=wx.STB_DEFAULT_STYLE)

	def create_content(self, parent):
		self.main_splitter = wx.SplitterWindow(parent=self, style=wx.SP_3D|wx.SP_NO_XP_THEME|wx.SP_LIVE_UPDATE)
		self.main_splitter.SetSashGravity(0.5)
		self.main_splitter.SetSashSize(5)
		self.treeview = TreeView.TreeView(self.main_splitter)
		self.infopane = wx.StaticText(parent=self.main_splitter, \
									label="Hello there! I'm a placeholder :D", size=(300,600))
		self.main_splitter.SplitVertically(self.treeview, self.infopane, 0)


	'''
	Updates UI
	'''

	def update_ui(self):
		self.SetTitle(self.get_title())
		# """
		# #TODO: Be more precise on menu item states
		# #	  e.g. archives not yet extracted will need this option to be avail
		# cab_avail = "normal" if _options.cabinet else "disabled"
		# self.menu_file.entryconfigure("Extract selected", state=cab_avail)
		# self.menu_file.entryconfigure("Extract all", state=cab_avail)
		# self.menu_file.entryconfigure("Close root", state=cab_avail)
		# #self.update_tree() # only called when _options.cabinet has changed!
		# # more to come, e.g. populating tree, ...
		# #...
		# """
		# self.set_statusbar()
		# Tk.update_idletasks(self)
		pass
	

	'''
	Menu handlers
	'''
		
	def onFileOpen(self, event):
		if 'LOCALAPPDATA' in os.environ:
			path = os.path.join(os.environ['LOCALAPPDATA'], "FactoryGame/Saved/SaveGames")
		elif 'APPDATA' in os.environ:
			path = os.path.join(os.environ['APPDATA'], "../Local/FactoryGame/Saved/SaveGames")
		else:
			path = "C:/"

		#new_file = os.path.join(path, "testfile.sav")
		new_file = ''
		dlg = wx.FileDialog(self, "Select savegame to load", new_file, "",\
							"Savegames (*.sav)|*.sav|All files (*.*)|*.*", wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			new_file = os.path.join(dlg.Directory, dlg.Filename)
			#wx.MessageBox("Filename is: "+new_file, "File open")
		
		if len(new_file) > 0 and os.path.isfile(new_file):
			self.currFile = Savegame.Savegame(new_file)
			self.update_ui()

			def _t():
				# First of all, load da save			
				callback = Callback.Callback(self, self.loader_callback)
				self.currFile.load(callback)
				del callback
				# Next up, check for errors
				#callback = Callback.Callback(self, self.checker_callback)
				#self.currFile.load(callback)
				#del callback
				# Finally, present some tree contents
				callback = Callback.Callback(self, self.builder_callback, 0)
				self.treeview.setup(self.currFile, callback)
				del callback
				
			#_t()
			t = threading.Thread(target=_t)
			t.start()
			
	def onFileSave(self, event):
		pass
			
	def onFileSaveAs(self, event):
		pass
			
	def onFileClose(self, event):
		pass
			
	def onFileExit(self, event):
		#self.app_ready()
		#self.__shutdown = True
		#while not self.__terminated:
		#	sleep(0.05)
		self.Close(True)
			

	def onEditOptions(self, event):
		#if OptionsDlg.OptionsDlg(self, _options).ShowModal() == wx.ID_OK:
		#	#TODO: Save changes
		#	self.update_ui()
		pass


	def onHelpAbout(self, event):
		AboutDlg.AboutDlg(self).ShowModal()


	'''
	Progress bar stuff
	'''

	def show_progressbar(self, maxval, cancelbtn=False):
		if cancelbtn:
			self.statusbar.SetFieldsCount(3, widths=(-1,-1,50))
			self.statusbar.SetStatusStyles((wx.SB_SUNKEN,wx.SB_NORMAL,wx.SB_NORMAL))
			rect = self.statusbar.GetFieldRect(2)
			self.cancelbtn = wx.Button(parent=self.statusbar, label="Cancel", pos=rect.Position, size=rect.Size)
			self.Bind(wx.EVT_BUTTON, self.onProgressCancel, self.cancelbtn)
			self.cancelbtn.Show()
		else:
			self.statusbar.SetFieldsCount(2, widths=(-1,-1))
			self.statusbar.SetStatusStyles((wx.SB_SUNKEN,wx.SB_NORMAL))

		rect = self.statusbar.GetFieldRect(1)
		self.progressbar = wx.Gauge(parent=self.statusbar, range=maxval, pos=rect.Position, size=rect.Size, style=wx.GA_HORIZONTAL)
		
	def update_progressbar(self, newpos):
		self.progressbar.SetValue(newpos)

	def hide_progressbar(self):
		self.progressbar.Hide()
		del self.progressbar
		self.progressbar = None
		self.statusbar.SetFieldsCount(1, widths=(-1,))
		self.statusbar.SetStatusStyles((wx.SB_SUNKEN,))
		self.set_idle()


	'''
	Status bar handling
	'''

	def update_statusbar(self, text=None, update=True):
		self.statusbar.SetStatusText(text or "Ready ...")

		
	'''
	Mouse cursor handling
	'''

	def set_busy(self, update=True):
		self._mouse("wait", update)

	def set_idle(self, update=True):
		self._mouse("")
		self.update_statusbar()

	def _mouse(self, cursor, update=True):
		#root.config(cursor=cursor)
		#if update:
		#	Tk.update(root)
		pass


	'''
	Helpers
	'''

	def get_title(self):
		#s = "Satisfactory Save Repairer"
		s = "Satisfactory Savegame Checker"
		if self.currFile:
			s += " - " + self.currFile.Filename
		return s


	'''
	Callbacks
	'''

	def loader_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar("Tilling earth ...")#"Loading file ...")
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar("Done loading")
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()

	def checker_callback(self, event):
		"""
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar("Loading file ...")
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar("Done loading")
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()
		"""
		pass

	def builder_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar("Growing banana tree ...")
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar("Done growing, enjoy")
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()

		# Done dealing with main frame, rest of duties is up to tree view itself
		self.treeview.process_event(event)
		
	

		

'''
Main
'''

#print(font.families())

_options = Options.Options("SatisfactorySaveRepairer.ini")

#root = tk.Tk()
#root.option_add('*tearOff', FALSE)
#
##TODO: Use _options to position to previously used position
#if _options.geometry.lower() == "zoomed":
#	root.wm_state("zoomed")
#else:
#	root.geometry(_options.geometry)
#
#app = Application(master=root)
#app.mainloop()
#
#TODO: Get geometry before window is being destroyed. But how?
#'''
#if root.wm_state() == "zoomed":
#	_options.geometry = "zoomed"
#else:
#	_options.geometry = root.geometry()
#'''

app = Application()

root = MainFrame()
root.Show()

app.MainLoop()

#_options.save()

sys.exit(0)
