#!/usr/bin/env python3
'''
Handy GUI for dealing with corrupted Satisfactory saves.
'''

import sys
import os
import threading
from time import sleep
from datetime import datetime

import wx

from Savegame \
	import Savegame, Validator
	 
from Util \
	import Options, Callback, Lang

from UI \
	import OptionsDlg, AboutDlg, TreeView, DetailsPanel


class Application(wx.App):
	def __init__(self):
		self.__path = os.path.dirname(sys.argv[0])

		# For distribution only!
		# -> Create log file, and rename existing one as backup
		logpath = os.path.join(self.__path, "logs")
		if not os.path.isdir(logpath):
			os.mkdir(logpath)
		self.__logfile = os.path.join(logpath, "SatisfactorySaveChecker.log")
		if os.path.isfile(self.__logfile):
			mtime = datetime.fromtimestamp(os.path.getmtime(self.__logfile))
			backup = "SatisfactorySaveChecker-" + mtime.strftime("%Y%m%d-%H%M%S") + ".log"
			os.rename(self.__logfile, os.path.join(logpath, backup))
		super().__init__(True, filename=self.__logfile, useBestVisual=True)
		# For development only!
		# -> Let IDE show messages in its output pane
		#super().__init__(False, useBestVisual=True)

		# Do additional groundwork
		Lang.Lang.load(None, os.path.join(self.Path, "Resources"))
		
		wx.FileSystem.AddHandler(wx.MemoryFSHandler())

		wx.Image.AddHandler(wx.PNGHandler())

	@property
	def Path(self): 
		return self.__path


def Log(text:str, add_ts:bool=True, add_newline:bool=True):
	if add_ts:
		text = "[{}] ".format(datetime.now()) + text
	if add_newline:
		text += "\n"
	print(text, end='')



class MainFrame(wx.Frame):

	currFile = None
	

	def __init__(self, parent=None):
		Log("Starting up...")
		super().__init__(parent, title="", size=(800,480))
		self.Bind(wx.EVT_CLOSE, self.onClose)

		file = os.path.join(wx.App.Get().Path, "Resources/Logo-128x128.png")
		self.Icon = wx.Icon(file)
		
		self.create_ui()
		
		# Finally, update UI
		self.update_ui()
		#self.update_tree()

		self.Show()
		self.Center()
		self.set_idle()


	'''
	UI generation
	'''

	def create_ui(self):
		self.create_menubar(self)
		self.create_toolbars(self)
		self.create_content(self)
		self.create_statusbar(self)

	def create_menubar(self, parent):
		self.menuBar = wx.MenuBar()
		self.SetMenuBar(self.menuBar)

		def _add(menu, label, tooltip=None, func=None, menuid=wx.ID_ANY):
			item = menu.Append(menuid, label, tooltip)
			if func: 
				self.Bind(wx.EVT_MENU, func, item)
			return item

		filemenu = wx.Menu()
		self.menuBar.Append(filemenu, _("&File"))
		self.menu_file_open = _add(filemenu, _("&Open...\tCtrl+O"), _("Opens a save game"), self.onFileOpen)
		#self.menu_file_save = _add(filemenu, _("&Save\tCtrl+S"), _("Saves changes"), self.onFileSave)
		#self.menu_file_save_as = _add(filemenu, _("Save &as..."), _("Saves changes into a different file"), self.onFileSaveAs)
		self.menu_file_close = _add(filemenu, _("C&lose\tCtrl+W"), _("Closes save"), self.onFileClose)
		filemenu.AppendSeparator()
		_add(filemenu, _("E&xit"), _("Terminate program"), self.onFileExit, wx.ID_EXIT)

		#editmenu = wx.Menu()
		#self.MenuBar.Append(editmenu, _("E&dit"))
		#_add(editmenu, _("&Options..."), _("Opens options dialog"), self.onEditOptions)
		
		helpmenu = wx.Menu()
		self.menuBar.Append(helpmenu, _("&Help"))
		_add(helpmenu, _("&About..."), _("Information about this program"), self.onHelpAbout, wx.ID_ABOUT)

	def create_toolbars(self, parent):
		#TODO: Add 'Next' + 'Prev' error buttons to navigate in tree
		pass

	def create_statusbar(self, parent):
		self.statusbar = self.CreateStatusBar(style=wx.STB_DEFAULT_STYLE)

	def create_content(self, parent):
		'''
		self.main_splitter = wx.SplitterWindow(parent=self, style=wx.SP_3D|wx.SP_NO_XP_THEME|wx.SP_LIVE_UPDATE)
		self.main_splitter.SetSashGravity(0.5)
		self.main_splitter.SetSashSize(5)
		#self.infopane = wx.StaticText(parent=self.main_splitter, \
		#							label="Hello there! I'm a placeholder :D", size=(300,600))
		self.infopanel = DetailsPanel.DetailsPanel(self.main_splitter)
		self.treeview = TreeView.TreeView(self.main_splitter, self.infopanel)
		self.main_splitter.SplitVertically(self.treeview, self.infopanel, 0)
		'''
		self.infopanel = DetailsPanel.DetailsPanel(self)
		self.infopanel.SetSize(size=self.ClientSize)



	'''
	Updates UI
	'''

	def update_ui(self):
		self.SetTitle(self.get_title())
		
		# Be more precise on menu item states
		has_save = (self.currFile != None)
		#has_changes = False
		self.menu_file_open.Enable(True)
		#self.menu_file_save.Enable(has_save & has_changes)  		
		#self.menu_file_save_as.Enable(has_save & has_changes)  		
		self.menu_file_close.Enable(has_save)
		
		if not has_save:
			self.update_panel("")
	
	def update_panel(self, text, append=False):
		self.infopanel.update(text, append)

			


	'''
	Menu handlers
	'''
		
	def onFileOpen(self, event):
		self.onFileClose(None)

		if 'LOCALAPPDATA' in os.environ:
			path = os.path.join(os.environ['LOCALAPPDATA'], "FactoryGame/Saved/SaveGames")
		elif 'APPDATA' in os.environ:
			path = os.path.join(os.environ['APPDATA'], "../Local/FactoryGame/Saved/SaveGames")
		else:
			path = "C:/"

		#new_file = os.path.join(path, "testfile.sav")
		new_file = ''
		dlg = wx.FileDialog(self, _("Select savegame to load"), path, "",\
							_("Savegames") + " (*.sav)|*.sav|" + _("All files") + " (*.*)|*.*",\
							wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			new_file = os.path.join(dlg.Directory, dlg.Filename)
			#wx.MessageBox("Filename is: "+new_file, "File open")
		
		if len(new_file) > 0 and os.path.isfile(new_file):
			self.currFile = Savegame.Savegame(new_file)
			self.update_ui()

			#TODO:
			#- Close current file (prompting for unsaved changes if any)
			#- Delete tree before starting
			#- Disable UI until done
			
			def _t():
				Log("Loading file: " + new_file)
				# First of all, load da save			
				l_callback = Callback.Callback(self, self.loader_callback)
				self.currFile.load(l_callback)
				sleep(0.0001)
				del l_callback
				sleep(0.0001)
				# Next up, check for errors
				v_callback = Callback.Callback(self, self.checker_callback, 0)
				validator = Validator.Validator(self.currFile)
				validator.validate(v_callback)
				sleep(0.0001)
				del validator
				del v_callback
				sleep(0.0001)
				'''
				# Finally, present some tree contents
				b_callback = Callback.Callback(self, self.builder_callback, 0)
				self.treeview.setup(self.currFile, b_callback)
				sleep(0.0001)
				del b_callback
				'''
				r_callback = Callback.Callback(self, self.result_callback, 0)
				self.show_results(r_callback)
				sleep(0.0001)
				del r_callback
				sleep(0.0001)				
				# Before exiting, send an update request
				#self.update_ui()
				Log("Finished loading")

			# Do the hard work in a background thread
			t = threading.Thread(target=_t)
			t.start()
			
	#def onFileSave(self, event):
	#	pass
			
	#def onFileSaveAs(self, event):
	#	pass
			
	def onFileClose(self, event):
		#self.treeview.DeleteAllItems()
		self.update_panel("")
		#TODO: Check change state before closing
		self.currFile = None
		self.update_ui()
			
	def onFileExit(self, event):
		#self.app_ready()
		#self.__shutdown = True
		#while not self.__terminated:
		#	sleep(0.05)
		self.onFileClose(None)
		self.Close(True)
		
		
	def onClose(self, event):
		Log("Shutting down...")
		event.Skip()
			

	#def onEditOptions(self, event):
	#	#if OptionsDlg.OptionsDlg(self, _options).ShowModal() == wx.ID_OK:
	#	#	#TODO: Save changes
	#	#	self.update_ui()
	#	pass


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
			self.cancelbtn = wx.Button(parent=self.statusbar, label=_("Cancel"), \
									pos=rect.Position, size=rect.Size)
			self.Bind(wx.EVT_BUTTON, self.onProgressCancel, self.cancelbtn)
			self.cancelbtn.Show()
		else:
			self.statusbar.SetFieldsCount(2, widths=(-1,-1))
			self.statusbar.SetStatusStyles((wx.SB_SUNKEN,wx.SB_NORMAL))

		rect = self.statusbar.GetFieldRect(1)
		self.progressbar = wx.Gauge(parent=self.statusbar, range=maxval, \
								pos=rect.Position, size=rect.Size, style=wx.GA_HORIZONTAL)
		
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
		self.statusbar.SetStatusText(text or _("Ready ..."))

		
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
		s = _("Satisfactory Savegame Checker")
		if self.currFile:
			s += " - " + self.currFile.Filename
		return s


	'''
	Callbacks
	'''

	def loader_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar(_("Loading file ..."))
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar(_("Done loading"))
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()

	def checker_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar(_("Checking objects ..."))
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar(_("Done checking"))
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()

	'''
	def builder_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar(_("Populating tree ..."))
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar(_("Done populating"))
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()

		# Done dealing with main frame, rest of duties is up to tree view itself
		self.treeview.process_event(event)
	'''	
	# Instead of building tree structure, we're generating an ASCII-based report
	def result_callback(self, event):
		if event.which == Callback.Callback.START:
			self.set_busy()
			self.update_statusbar(_("Generating report ..."))
			self.show_progressbar(event.maxval)
			
		elif event.which == Callback.Callback.UPDATE:
			if event.data:
				self.infopanel.update(event.data, True)
			self.update_progressbar(event.val)
			
		elif event.which == Callback.Callback.END:
			self.update_statusbar(_("Done generating"))
			self.hide_progressbar()
			self.set_idle()
			self.update_ui()
	
	def __cb_results_start(self, total):
		if self.__results_callback: 
			self.__results_callback.start(total)
		
	def __cb_results_update(self, text):
		if self.__results_callback: 
			self.__results_callback.update(self.__results_count, text)
		
	def __cb_results_end(self):
		if self.__results_callback: 
			self.__results_callback.end(True)
	
	def show_results(self, callback):
		self.__results_callback = callback
		self.__results_count = 0
		self.__indent = 0
		self.__error_count = 0
		
		total = self.currFile.TotalElements		
		self.__cb_results_start(total)
		
		for obj in self.currFile.Objects:
			self.__show_results(obj)
		
		for obj in self.currFile.Collected:
			self.__show_results(obj)

		if not self.__error_count:
			self.__cb_results_update(_("No errors found"))
		else:
			self.__cb_results_update("\n\n"+_("A total of {} errors found!").format(self.__error_count))
		self.__cb_results_end()

	def __show_results(self, obj):
		self.__results_count += 1
		if obj.HasErrors:
			self.__error_count += 1
			s = str(obj) + "\n"
			for e in obj.Errors:
				s += ("\t"*self.__indent) + e + "\n"  
			self.__cb_results_update(s)
			childs = obj.Childs
			if childs:
				self.__show_results_recurs(childs)
				
	def __show_results_recurs(self, childs):
		self.__indent += 1
		for name in childs:
			sub = childs[name]

			if isinstance(sub, (list,dict)):
				for obj in sub:
					self.__show_results(obj)
			else:
				self.__show_results(sub)
		
		self.__indent -= 1

'''
Main
'''

#print(font.families())

#_options = Options.Options("SatisfactorySaveChecker.ini")

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
