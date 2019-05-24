"""
About dialog for satisfactory savegame repairer
"""

import sys
import os

import wx
#import wx.adv


class AboutDlg(wx.Dialog):
	
	def __init__(self, parent):
		super().__init__(parent, title="About Satisfactory Savegame Repairer", \
						style=wx.DEFAULT_DIALOG_STYLE)
		
		file = os.path.join(os.path.dirname(sys.argv[0]), "README.md")
		with open(file, "rt") as file:
			s = file.read()
				
		self.v_sizer = wx.BoxSizer(wx.VERTICAL)
		self.v_sizer.AddSpacer(5)
		self.v_sizer.Add(wx.StaticText(parent=self, label=s, size=(600,300), style=wx.ALIGN_LEFT)\
						, 1, wx.EXPAND)
		self.v_sizer.AddSpacer(10)
		self.v_sizer.Add(wx.Button(parent=self, label="OK", size=wx.DefaultSize, id=wx.ID_OK)\
						, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
		self.v_sizer.AddSpacer(5)
		
		self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.h_sizer.AddSpacer(5)
		self.h_sizer.Add(self.v_sizer)
		self.h_sizer.AddSpacer(5)
		
		self.SetSizerAndFit(self.h_sizer)
		

'''
Neat, but somewhat clumsy with all those sections


class AboutDlg:
	
	def __init__(self, parent):
		description = """Presents a somewhat automated way of repairing
borked savegames with different options to choose from.
"""
		
		licence = """'Satisfactory Savegame Repairer' is free software; 
you can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software 
Foundation; either version 2 of the License, or (at your option) 
any later version.

'Satisfactory Savegame Repairer' is distributed in the hope that it 
will be useful, but WITHOUT ANY WARRANTY; without even the implied 
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details. You should have
received a copy of the GNU General Public License along with this program;
if not, write to the Free Software Foundation, Inc., 59 Temple Place,
Suite 330, Boston, MA  02111-1307  USA"""
		
		info = wx.adv.AboutDialogInfo()
	
		#info.SetIcon(wx.Icon('hunter.png', wx.BITMAP_TYPE_PNG))
		info.SetName("Satisfactory Savegame Repairer")
		info.SetVersion('1.0')
		info.SetDescription(description)
		info.SetCopyright('(C) 2019 SillyBits')
		#info.SetWebSite('http://www.github.com/SillyBits/satisfactory-savegame-repairer')
		info.SetWebSite('http://www.satisfactory-forum.de')
		info.SetLicence(licence)
		info.AddDeveloper('SillyBits')
		#info.AddDeveloper('bitOwl (as some ideas are based on his work)')
		#info.AddDeveloper('Goz3rr (as some ideas are based on his work)')
		#info.AddDocWriter('SillyBits')
		#info.AddArtist('SillyBits')
		#info.AddTranslator('SillyBits')
		
		wx.adv.AboutBox(info)
'''

