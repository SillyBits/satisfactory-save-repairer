#!/usr/bin/env python3
'''
Handy GUI for dealing with corrupted Satisfactory saves.
'''

import sys
import os
import threading
from time import sleep

import wx

from wx.lib \
    import newevent


import AppConfig

from Savegame \
	import Savegame, Property, Validator

from Util \
	import Options, Callback, Lang, Log

from UI \
	import OptionsDlg, AboutDlg, ChangelogDlg, TreeView, DetailsPanel, ProgressDlg


class Application(wx.App):

	def __init__(self):
		self.__path = os.path.dirname(sys.argv[0])

		if 'SSR_DEBUG' in os.environ:
			# For development only!
			# -> Let IDE show messages in its output pane
			#super().__init__(False, useBestVisual=True)
			self.__logfile = None
		else:
			# For distribution only!
			# -> Create log file, and rename existing one as backup
			self.__logfile = Log.InitLog(AppConfig.APP_NAME, self.__path)
		super().__init__(self.__logfile != None, filename=self.__logfile, useBestVisual=True)

		self.AppName = AppConfig.APP_NAME

		# Below should be dealt with in OnInit?

		Options.Options(AppConfig.APP_NAME, self.__path)

		Lang.Lang.load(None, os.path.join(self.__path, "Resources"))

		wx.FileSystem.AddHandler(wx.MemoryFSHandler())

		wx.Image.AddHandler(wx.PNGHandler())


	#def OnInit(self, *args, **kwargs):
	#	return wx.App.OnInit(self, *args, **kwargs)
	
	#def OnExit(self, *args, **kwargs):
	#	# Should clean up stuff like config
	#	wx.Config.Set(None)
	#	return wx.App.OnExit(self, *args, **kwargs)		

	
	@property
	def Path(self): 
		return self.__path


class MainFrame(wx.Frame):

	currFile = None


	def __init__(self, parent=None):
		Log.Log("Starting up...")

		cfg = wx.Config.Get()
		if cfg.window.pos_x >= 0:
			pos = wx.Point(int(cfg.window.pos_x), int(cfg.window.pos_y))
		else:
			pos = wx.DefaultPosition
		if cfg.window.size_x > 0:
			size = wx.Size(cfg.window.size_x, cfg.window.size_y)
		else:
			size = wx.Size(800,480)

		super().__init__(parent, title="", pos=pos, size=size)

		self.__update_event_class, self.__update_event = newevent.NewEvent()
		self.Bind(self.__update_event, self.onUpdateUI)

		self.Bind(wx.EVT_CLOSE, self.onClose)

		file = os.path.join(wx.App.Get().Path, "Resources/Logo-128x128.png")
		self.Icon = wx.Icon(file)
		
		self.create_ui()
		
		# Finally, update UI
		self.update_ui()
		#self.update_tree()

		self.Show()
		if pos == wx.DefaultPosition:
			self.Center()
		self.set_idle()

		wx.App.Get().SetTopWindow(self)
		
		self.__check_first_time_options()


	'''
	UI generation
	'''

	def create_ui(self):
		self.__wait = None
		self.__disabler = None

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

		editmenu = wx.Menu()
		self.MenuBar.Append(editmenu, _("E&dit"))
		_add(editmenu, _("&Options..."), _("Opens options dialog"), self.onEditOptions)
		
		helpmenu = wx.Menu()
		self.menuBar.Append(helpmenu, _("&Help"))
		_add(helpmenu, _("&Changelog..."), _("Show changelog"), self.onHelpChangelog)
		_add(helpmenu, _("&About..."), _("Informations about this program"), self.onHelpAbout, wx.ID_ABOUT)

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
		new_file = ''
		path = str(wx.Config.Get().core.default_path)
		dlg = wx.FileDialog(self, _("Select savegame to load"), path, "",\
							_("Savegames") + " (*.sav)|*.sav|" + _("All files") + " (*.*)|*.*",\
							wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			new_file = os.path.join(dlg.Directory, dlg.Filename)

		if len(new_file) > 0 and os.path.isfile(new_file):
			self.__load(new_file)
			
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
		self.onFileClose(None)
		self.Close(True)
			

	def onEditOptions(self, event):
		OptionsDlg.OptionsDlg(self).ShowModal()


	def onHelpChangelog(self, event):
		ChangelogDlg.ChangelogDlg(self).ShowModal()

	def onHelpAbout(self, event):
		AboutDlg.AboutDlg(self).ShowModal()


	'''
	Random event handlers
	'''

	def onClose(self, event):
		wx.App.Get().SetTopWindow(None)
		cfg = wx.Config.Get()
		cfg.window.pos_x, cfg.window.pos_y = self.Position
		cfg.window.size_x, cfg.window.size_y = self.Size
		Log.Log("Shutting down...")
		event.Skip()

	def onUpdateUI(self, event):
		self.update_ui()


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
	UI state handling
	'''

	def set_busy(self, update=True):
		#self._mouse("wait", update)
		if self.__wait is None:
			self.__disabler = wx.WindowDisabler(True)
			self.__wait = wx.BusyCursor()

	def set_idle(self, update=True):
		#self._mouse("")
		self.update_statusbar()
		self.__wait = self.__disabler = None

	def _mouse(self, cursor, update=True):
		#root.config(cursor=cursor)
		#if update:
		#	Tk.update(root)
		pass


	'''
	Helpers
	'''

	def get_title(self, raw=False):
		s = _(AppConfig.APP_TITLE)
		if self.currFile and not raw:
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
		sleep(0.01)
		
		for obj in self.currFile.Objects:
			self.__show_results(obj)
		
		for obj in self.currFile.Collected:
			self.__show_results(obj)

		if not self.__error_count:
			s = "\n" + _("No errors found")
		else:
			s = "\n\n"+_("A total of {} errors found!").format(self.__error_count)
		Log.Log(s, add_newline=False, add_ts=False)
		self.__cb_results_update(s)
		sleep(0.01)
		self.__cb_results_end()

	def __show_results(self, obj):
		self.__results_count += 1
		if isinstance(obj, Property.Accessor):
			if obj.HasErrors:
				if not self.__indent: # Count as error only on top level?
					self.__error_count += 1
				s = "" if self.__indent else "\n"
				s += ("\t"*self.__indent) + str(obj) + "\n"
				for e in obj.Errors:
					s += ("\t"*self.__indent) + e + "\n"
				Log.Log(s, add_newline=False, add_ts=False)  
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
	Methods
	'''
		
	def __load(self, filename):
		#TODO:
		#- Close current file (prompting for unsaved changes if any)
		#- Delete tree before starting
		#- Disable UI until done

		self.onFileClose(None)

		self.currFile = Savegame.Savegame(filename)

		callback = ProgressDlg.ProgressDlg(self, _("Loading save"))
		self.set_busy()


		def _t():

			# First of all, load da save			
			Log.Log("Loading file:\n-> " + filename)
			callback.SetCountsFormat(_("{:,d} / {:,d} bytes"))
			self.currFile.load(callback)
			Log.Log("Finished loading")

			# Next up, check for errors
			Log.Log("Validating objects")
			callback.SetCountsFormat(_("{:,d} / {:,d} objects"))
			validator = Validator.Validator(self.currFile)
			validator.validate(callback)
			del validator
			Log.Log("Finished validating")

			# Finally, present some tree contents, 
			# or report if we're in checking-only mode
			if False:#SHOW_TREE:
				Log.Log("Building tree")
				self.treeview.setup(self.currFile, callback)
				Log.Log("Finished building tree")
			else:
				Log.Log("Creating report")
				r_callback = Callback.Callback(self, self.result_callback, 0)
				self.show_results(r_callback)
				del r_callback
				Log.Log("Finished reporting")

			# Before exiting, send an update request
			wx.PostEvent(self, self.__update_event_class())
			# ... and instruct progress dialog to destroy itself
			callback.destroy()


		# Do the hard work in a background thread
		t = threading.Thread(target=_t)
		t.start()


	def __check_first_time_options(self):

		feature_info = _("Would you like to activate this feature now?","\n",
						 "\n",
						 "Note: This dialog will only be shown once, this feature","\n",
						 "can also be en-/disabled in the options dialog later.")

		if not wx.Config.Get().deep_analysis.asked:

			caption = _(MainFrame.TITLE, " - ", "Deep Analysis")
			msg = _("This program is capable of parsing any object-specific private data.","\n",
					"\n",
					"This includes, for example, items on conveyors or wire connections.","\n",
					"But if activated, this will increase load times dramatically!","\n",
					"So activate only in case normal analysis won't do.","\n",
					"\n") + feature_info

			res = wx.MessageBox(msg, caption, style=wx.YES_NO|wx.ICON_QUESTION|wx.CENTRE)

			wx.Config.Get().deep_analysis.asked = True
			wx.Config.Get().deep_analysis.enabled = (res == wx.YES)


		if not wx.Config.Get().incident_report.asked:

			caption = _(MainFrame.TITLE, " - ", "Incident Reports")
			msg = _("This program is capable of reporting yet unknown data.","\n",
					"\n",
					"If activated, you'll be shown a report when unknown data was found and","\n",
					"you're free to edit out any details you want before actual transmission.","\n",
					"Sending such reports will help the author in advancing this program.","\n",
					"\n") + feature_info

			res = wx.MessageBox(msg, caption, style=wx.YES_NO|wx.ICON_QUESTION|wx.CENTRE)

			wx.Config.Get().incident_report.asked = True
			wx.Config.Get().incident_report.enabled = (res == wx.YES)

		#TODO: Develop more features :D


'''
Main
'''

app = Application()

root = MainFrame()
root.Show()

app.MainLoop()

sys.exit(0)
