"""
About dialog for satisfactory savegame repairer
"""

import sys
import os
import webbrowser

import wx
import wx.html


class AboutDlg(wx.Dialog):
	
	__mem = wx.MemoryFSHandler()

	def __init__(self, parent):
		super().__init__(parent, title="About Satisfactory Savegame Repairer", \
						style=wx.DEFAULT_DIALOG_STYLE)
		
		res = os.path.join(wx.App.Get().Path, "Resources/Logo-128x128.png")
		res = wx.Image(res)
		self.__mem.AddFile('logo.png', res, wx.BITMAP_TYPE_PNG)

		res = os.path.join(wx.App.Get().Path, "Resources/About.res")
		with open(res, "rt") as file:
			content = file.read()
		view = wx.html.HtmlWindow(self, size=(666,333), style=wx.html.HW_SCROLLBAR_NEVER)
		view.SetPage(content)
		view.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.onLink)

		self.v_sizer = wx.BoxSizer(wx.VERTICAL)
		self.v_sizer.AddSpacer(5)
		self.v_sizer.Add(view, 1, wx.EXPAND)
		self.v_sizer.AddSpacer(10)
		self.v_sizer.Add(wx.Button(parent=self, label="OK", size=wx.DefaultSize, id=wx.ID_OK)\
						, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
		self.v_sizer.AddSpacer(5)

		self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.h_sizer.AddSpacer(5)
		self.h_sizer.Add(self.v_sizer)
		self.h_sizer.AddSpacer(5)

		self.SetSizerAndFit(self.h_sizer)

	def ShowModal(self, *args, **kwargs):
		rv = wx.Dialog.ShowModal(self, *args, **kwargs)
		self.__mem.RemoveFile('logo.png')
		return rv
	
	def onLink(self, event):
		webbrowser.open(event.LinkInfo.Href, new=2)
	
