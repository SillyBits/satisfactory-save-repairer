"""
About dialog for satisfactory savegame repairer
"""

import sys
import os
import webbrowser

import wx
import wx.html


class AboutDlg(wx.Dialog):

	def __init__(self, parent):
		super().__init__(parent, title="About Satisfactory Savegame Repairer", \
						style=wx.DEFAULT_DIALOG_STYLE)

		file = os.path.join(os.path.dirname(sys.argv[0]), "Resources/About.res")
		with open(file, "rt") as file:
			s = file.read()

		self.v_sizer = wx.BoxSizer(wx.VERTICAL)

		self.v_sizer.AddSpacer(5)

		text = wx.html.HtmlWindow(self, size=(666,333), style=wx.html.HW_SCROLLBAR_NEVER)
		text.SetPage(s)
		text.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.onLink)
		self.v_sizer.Add(text, 1, wx.EXPAND)

		self.v_sizer.AddSpacer(10)

		self.v_sizer.Add(wx.Button(parent=self, label="OK", size=wx.DefaultSize, id=wx.ID_OK)\
						, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)

		self.v_sizer.AddSpacer(5)

		self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.h_sizer.AddSpacer(5)

		self.h_sizer.Add(self.v_sizer)

		self.h_sizer.AddSpacer(5)

		self.SetSizerAndFit(self.h_sizer)

	def onLink(self, event):
		webbrowser.open(event.LinkInfo.Href, new=2)
	
