

import wx


class OptionsDlg(wx.Dialog):

	def __init__(self, parent):
		super().__init__(parent, title=_("Satisfactory Savegame Checker", " - ", "Options"),
			style=wx.DEFAULT_DIALOG_STYLE|wx.CENTRE)

		self.__tweak()


	'''
	Private implementation
	'''

	def __tweak(self):

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.__add_options(sizer)

		btns = wx.BoxSizer(wx.HORIZONTAL)
		btns.AddStretchSpacer()
		self.__ok = wx.Button(parent=self, label=_("Save"), size=wx.DefaultSize, id=wx.ID_OK)
		self.__ok.Bind(wx.EVT_BUTTON, self.__onOk)
		btns.Add(self.__ok, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
		btns.AddSpacer(5)
		self.__cancel = wx.Button(parent=self, label=_("Cancel"), size=wx.DefaultSize, id=wx.ID_CANCEL)
		btns.Add(self.__cancel, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
		#btns.AddStretchSpacer()
		btns.AddSpacer(5)
		sizer.Add(btns, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)

		self.SetSizerAndFit(sizer)



	def __add_options(self, sizer):
		flagsExpand = wx.SizerFlags(0)
		flagsExpand.Expand().Border(wx.ALL, 5)

		label_feature = _("Feature is active")
		label_asked = "<span foreground='red'>" + _("On startup, do not ask again") + "</span>"

		cfg = wx.Config.Get()


		'''
		Default path
		'''
		group = wx.StaticBoxSizer(wx.VERTICAL, self, _("Default path"))
		info = _("Location where your save games do reside") + ":"
		group.Add(wx.StaticText(group.GetStaticBox(), label=info), flagsExpand)

		self.__default_path = wx.TextCtrl(group.GetStaticBox(), value=str(cfg.core.default_path))
		group.Add(self.__default_path, 1, wx.EXPAND)
		self.__default_path_browse = wx.Button(parent=group.GetStaticBox(), label=_("Browse..."))
		self.__default_path_browse.Bind(wx.EVT_BUTTON, self.__onDefaultPathBrowse)
		group.Add(self.__default_path_browse, 0, wx.FIXED_MINSIZE|wx.ALIGN_RIGHT)

		sizer.Add(group, flagsExpand)


		'''
		Deep analysis
		'''
		group = wx.StaticBoxSizer(wx.VERTICAL, self, _("Deep Analysis"))
		info = _("This program is capable of parsing any object-specific private data.","\n",
					"This includes, for example, items on conveyors or wire connections.","\n",
					"But if activated, this will increase load times dramatically!","\n",
					"So activate only in case normal analysis won't do.")
		group.Add(wx.StaticText(group.GetStaticBox(), label=info), flagsExpand)

		self.__deep_analysis__enabled = wx.CheckBox(group.GetStaticBox(), label=label_feature)
		self.__deep_analysis__enabled.Value = (cfg.deep_analysis.enabled == True)
		group.Add(self.__deep_analysis__enabled, flagsExpand)

		#chk = wx.CheckBox(group.GetStaticBox(), label=label_asked)
		self.__deep_analysis__asked = wx.CheckBox(group.GetStaticBox(), label="")
		self.__deep_analysis__asked.SetLabelMarkup(label_asked)
		self.__deep_analysis__asked.Value = (cfg.deep_analysis.asked == True)
		group.Add(self.__deep_analysis__asked, flagsExpand)

		sizer.Add(group, flagsExpand)


		'''
		Incident reports
		'''
		group = wx.StaticBoxSizer(wx.VERTICAL, self, _("Incident Reports"))
		info = _("This program is capable of reporting yet unknown data.","\n",
				 "If activated, you'll be shown a report when unknown data was found and","\n",
				 "you're free to edit out any details you want before actual transmission.","\n",
				 "Sending such reports will help the author in advancing this program.")
		group.Add(wx.StaticText(group.GetStaticBox(), label=info), flagsExpand)

		self.__incident_report__enabled = wx.CheckBox(group.GetStaticBox(), label=label_feature)
		self.__incident_report__enabled.Value = (cfg.incident_report.enabled == True)
		group.Add(self.__incident_report__enabled, flagsExpand)

		#chk = wx.CheckBox(group.GetStaticBox(), label=label_feature)
		self.__incident_report__asked = wx.CheckBox(group.GetStaticBox(), label="")
		self.__incident_report__asked.SetLabelMarkup(label_asked)
		self.__incident_report__asked.Value = (cfg.incident_report.asked == True)
		group.Add(self.__incident_report__asked, flagsExpand)

		sizer.Add(group, flagsExpand)


		#end of options


	def __onDefaultPathBrowse(self, event):
		with wx.DirDialog(self, message=_("Location where your save games do reside"), 
			defaultPath=self.__default_path.Value,style=wx.DD_DEFAULT_STYLE) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.__default_path.Value = dlg.Path


	def __onOk(self, event):
		event.Skip()

		cfg = wx.Config.Get()

		cfg.core.default_path       = self.__default_path.Value

		cfg.deep_analysis.enabled   = self.__deep_analysis__enabled.Value
		cfg.deep_analysis.asked     = self.__deep_analysis__asked.Value

		cfg.incident_report.enabled = self.__incident_report__enabled.Value
		cfg.incident_report.asked   = self.__incident_report__asked.Value
		
		cfg.Flush()


		self.EndModal(wx.OK)

