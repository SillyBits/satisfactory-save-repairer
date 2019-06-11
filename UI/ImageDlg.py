

import wx


class ImageDlg(wx.Dialog):

	def __init__(self, parent, title, image):
		super().__init__(parent, title=title,
			style=wx.DEFAULT_DIALOG_STYLE|wx.CENTRE)
		
		self.__tweak(image)


	'''
	Private implementation
	'''

	def __tweak(self, image):

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.__bitmap = wx.StaticBitmap(self, bitmap=image, size=image.Size)
		sizer.Add(self.__bitmap, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)

		btns = wx.BoxSizer(wx.HORIZONTAL)
		btns.AddStretchSpacer()
		self.__ok = wx.Button(parent=self, label=_("OK"), id=wx.ID_OK)
		#self.__ok.Bind(wx.EVT_BUTTON, self.__onOk)
		btns.Add(self.__ok, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
		btns.AddSpacer(5)
		sizer.Add(btns, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)

		self.SetSizerAndFit(sizer)


	def __onOk(self, event):
		event.Skip()
		self.EndModal(wx.OK)

