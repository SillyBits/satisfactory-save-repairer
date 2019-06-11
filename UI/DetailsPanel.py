"""
All the panels needed for displaying savegame data
"""


import os
from math import sqrt


import wx

from wx.lib.agw.pycollapsiblepane \
	import PyCollapsiblePane


from Savegame \
	import Property #, PropertyDumper

from Util \
	import Helper

from UI \
	import ImageDlg


EMPTY = None
FONT_MONOSPACED = None


class DetailsPanel(wx.Panel):

	def __init__(self, parent):
		super().__init__(parent, size=(300,600))

		self.__img_path = os.path.join(wx.App.Get().Path, "Resources", "Images")
		self.__mode = DetailsPanel.MODE_NONE

		self.__sizer = wx.FlexGridSizer(1,1, 0,0)
		self.__sizer.AddGrowableCol(0, proportion=1)
		self.__sizer.AddGrowableRow(0, proportion=1)

		self.SetSizerAndFit(self.__sizer)

		global EMPTY, FONT_MONOSPACED
		if EMPTY is None:
			EMPTY = _("<none>")
		if FONT_MONOSPACED is None:
			FONT_MONOSPACED = wx.Font(wx.FontInfo(10).FaceName("Consolas"))
			if not FONT_MONOSPACED.IsOk() or not FONT_MONOSPACED.IsFixedWidth():
				FONT_MONOSPACED = wx.Font(wx.FontInfo(10).FaceName("FixedSys"))
				if not FONT_MONOSPACED.IsOk() or not FONT_MONOSPACED.IsFixedWidth():
					FONT_MONOSPACED = wx.Font(wx.FontInfo(10).FaceName("Terminal"))


	def update(self, text, append=False):
		self.__show_text(text, append)

	def show_property(self, prop):
		if not prop:
			self.__show_text("<no data avail>")
		else:
			self.__show_prop(prop)


	'''
	Private implementation
	'''

	def __delete_all(self):
		self.__sizer.Clear()
		self.DestroyChildren()
		self.__mode = DetailsPanel.MODE_NONE

	def __show_text(self, text, append=False):
		if self.__mode != DetailsPanel.MODE_TEXT:
			self.__delete_all()
			self.__mode = DetailsPanel.MODE_TEXT

			ctrl = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_NOHIDESEL|wx.TE_MULTILINE)
			self.__sizer.Add(ctrl, 1, flag=wx.EXPAND)

			self.Layout()

		# Have not seen a method to reduce tab size with StaticText,
		# so we just convert them down into simple spaces
		text_ = text.replace("\t", "    ")
		
		ctrl = self.GetChildren()[0]
		if append:
			ctrl.Value += text_
		else:
			ctrl.Value = text_

	def __show_prop(self, prop):
		self.__delete_all()
		self.__mode = DetailsPanel.MODE_OBJ
		
		ctrl = Details(self, prop)
		self.__sizer.Add(ctrl, 1, flag=wx.EXPAND)

		self.Layout()


	MODE_NONE = 0
	MODE_TEXT = 1
	MODE_OBJ  = 2



class Details(wx.ScrolledWindow):

	__instance = None

	def __init__(self, parent, prop):
		super().__init__(parent, style=wx.HSCROLL)
		Details.__instance = self
		self.SetScrollRate(0,100)# No vertical scrolling!

		self.__show(prop)


	@staticmethod
	def Instance():
		return Details.__instance
	

	'''
	Private implementation
	'''

	def Destroy(self):
		Details.__instance = None
		super().Destroy()

	def __show(self, prop):

		self.__sizer = wx.GridBagSizer(0,0)
		self.__sizer.SetEmptyCellSize((0,0))
		self.__sizer.SetCols(3)
		self.__sizer.AddGrowableCol(2, proportion=1)
		self.SetSizer(self.__sizer)

		print("Adding property {}".format(prop))
		pane, sizer = self.__add(self, self.__sizer, None, prop)
		
		# Master pane is expanded initially
		pane.GetParent().Expand()


	def __add(self, parent_pane, parent_sizer, name, prop):

		if prop:
			t = prop.TypeName
			if t in globals():
				cls = globals()[t]
				inst = cls(parent_pane, parent_sizer, name, prop)
					
				return parent_pane, parent_sizer
		
		# - mFogOfWarRawData: Show an image?
		if isinstance(prop, Property.ArrayProperty) \
		and prop.Name == "mFogOfWarRawData":
			assert prop.InnerType == "ByteProperty"
			size = sqrt(len(prop.Value)/4)
			assert ((int(size)**2)*4) == len(prop.Value)
			return AsImage(parent_pane, parent_sizer, prop.Name, prop), parent_sizer


		pane = CollapsiblePane(parent_pane, parent_sizer, 
							str(prop) if prop else name)

		sizer = wx.GridBagSizer(5,2)
		sizer.SetEmptyCellSize((10,1))
		sizer.SetCols(4)
		sizer.AddGrowableCol(2, proportion=1)
		pane.GetPane().SetSizer(sizer)

		if prop:
			self.__add_recurs(pane.GetPane(), sizer, prop.Childs)

		sizer.Add(5,1, (0,3))
		sizer.Layout()
		
		return pane.GetPane(), sizer


	def __add_recurs(self, parent_pane, parent_sizer, childs):
		if not len(childs):
			return
		
		# Sort children first by both their "type" and name
		names = [ k for k in childs.keys() ]
		names.sort()
		
		simple = []
		simple2 = []
		props = []
		sets = []
		last = []
		for name in names:
			sub = childs[name]
			if isinstance(sub, (list,dict)):
				if name == "Missing" \
				or (name == "Unknown" and isinstance(sub, list)):
					last.append(name)
				else:
					sets.append(name)
			elif isinstance(sub, Property.Accessor):
				if sub.TypeName in globals():
					simple2.append(name)
				else:
					props.append(name)
			else:
				simple.append(name)

		order = simple + simple2 + props + sets + last
		#print("order: {}".format(order))

		for name in order:
			sub = childs[name]
			#print("__add_recurs: {}".format(type(sub)))

			# Do some testing on property name here as some do need special handling, e.g.
			# - Length : Must be readonly as this will be calculated based on properties stored.
			# - Missing: Should show a (readonly) hex dump
			if name == "Length":
				ReadonlyValue(parent_pane, parent_sizer, name, sub)
				continue
			if name == "Missing":
				Hexdump(parent_pane, parent_sizer, name, sub)
				continue
			if name == "Unknown" and isinstance(sub, list):
				# There are several .Unknown properties, dump only list-based ones
				Hexdump(parent_pane, parent_sizer, name, sub)
				continue

			if isinstance(sub, (list,dict)):
				label = "{} [{}]".format(name, len(sub))
				sub_parent, sub_sizer = self.__add(parent_pane, parent_sizer, label, None)
				for obj in sub:
					if isinstance(obj, Property.Accessor):
						label = str(obj)
						self.__add(sub_parent, sub_sizer, label, obj)

			elif isinstance(sub, Property.Accessor):
				self.__add(parent_pane, parent_sizer, name, sub)

			else:
				SimpleValue(parent_pane, parent_sizer, name, sub)


class BasePane:
	def __init__(self, parent, sizer):
		self.__parent = parent
		self.__sizer = sizer


class CollapsiblePane(PyCollapsiblePane):
	__img_path = None
	__img_size = (16,16)
	__img_collapsed = None
	__img_expanded = None

	def __init__(self, parent, sizer, label):
		if not CollapsiblePane.__img_path:
			CollapsiblePane.__img_path = os.path.join(wx.App.Get().Path, "Resources", "Images")
			CollapsiblePane.__img_collapsed = wx.Bitmap(os.path.join(self.__img_path, 
				"Button.Collapse.{}.png".format(CollapsiblePane.__img_size[0])))
			CollapsiblePane.__img_expanded = wx.Bitmap(os.path.join(self.__img_path, 
				"Button.Expand.16.png".format(CollapsiblePane.__img_size[0])))

		self.__label = label

		super().__init__(parent, label="", agwStyle=0)#, style=wx.BORDER)

		self.__btn = wx.Button(self, style=wx.BORDER_NONE, size=CollapsiblePane.__img_size)
		self.__btn.SetBitmap(CollapsiblePane.__img_collapsed)
		self.SetButton(self.__btn)

		if sizer:
			row = sizer.GetRows()
			sizer.Add(self, (row,1), span=wx.GBSpan(1,2), flag=wx.EXPAND)


	def OnButton(self, event):
		super().OnButton(event)
		#print("OnButton: collapsed={}".format(self.IsCollapsed()))
		self.__btn.SetBitmap(CollapsiblePane.__img_collapsed if self.IsCollapsed() 
						else CollapsiblePane.__img_expanded)
		# Ugly, but easiest way to get it up the chain
		Details.Instance().PostSizeEvent()

	def GetBtnLabel(self):
		return self.__label
	def GetLabel(self):
		return self.__label


'''
Actual value controls

Those will not only take care of displaying value correctly,
but will also take care of validating the user input
'''

class Value:
	def __init__(self, parent, sizer, label, val):
		self.parent = parent
		self.sizer = sizer
		self.row = sizer.GetRows()
		
		self.addLabel(wx.StaticText(parent, label=label + ":"))
		self.createControl(val)


	def addLabel(self, control):
		self.sizer.Add(control, (self.row,1), flag=wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)

	def addValue(self, control, expand=True):
		self.sizer.Add(control, (self.row,2), flag=wx.EXPAND if expand else 0)
				
	def createControl(self, val):
		pass


class SimpleValue(Value):
	def createControl(self, val):
		expand = False

		if isinstance(val, bool):
			#control = wx.TextCtrl(self.parent, value=str(val), 
			#					style=wx.ALIGN_RIGHT, size=(100,0))
			control = wx.CheckBox(self.parent)
			control.Value = wx.CHK_CHECKED if val else wx.CHK_UNCHECKED

		elif isinstance(val, float):
			control = wx.TextCtrl(self.parent, value=str(val), 
								style=wx.ALIGN_RIGHT, size=(100,-1))

		elif isinstance(val, int):
			width = 150 if val > 1e10 else 100 # Handle LOOOOONG values :D
			control = wx.TextCtrl(self.parent, value=str(val), 
								style=wx.ALIGN_RIGHT, size=(width,-1))

		else:
			control = wx.TextCtrl(self.parent, value=str(val))
			expand = True

		self.addValue(control, expand)

class ReadonlyValue(SimpleValue):
	def addValue(self, control, expand=True):
		control.Disable()
		super().addValue(control, expand)


class SimpleProperty(SimpleValue):
	def __init__(self, parent, sizer, label, val):
		assert isinstance(val, Property.Accessor)
		super().__init__(parent, sizer, val.Name, val.Value)

class ReadonlyProperty(SimpleProperty):
	def addValue(self, control, expand=True):
		control.Disable()
		super().addValue(control, expand)


class Hexdump(Value):
	def createControl(self, val):
		if val is not None and len(val):
			dump = Helper.dump_hex(val, indent=0)
			control = wx.TextCtrl(self.parent, #value=dump, 
								style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
			control.Font = FONT_MONOSPACED
			control.Value = dump
			expand = True
		else:
			control = wx.TextCtrl(self.parent, value=EMPTY)
			expand = False

		self.addValue(control, expand)


class AsImage(Value):
	#def __init__(self, parent, sizer, label, val):
	def createControl(self, val):
		assert isinstance(val, Property.ArrayProperty)
		assert val.InnerType == "ByteProperty"
		size = int(sqrt(len(val.Value)/4))
		assert ((size**2)*4) == len(val.Value)
		
		self.__imgdata = val.Value
		self.__image = None
		self.__size = size

		self.__sizer = wx.FlexGridSizer(2, 10,0)
	
		self.__info = wx.StaticText(self.parent, label="RGBA image of size {} x {}".format(size, size))
		self.__sizer.Add(self.__info, 1, flag=wx.ALIGN_CENTER_VERTICAL)
		
		self.__btn = wx.Button(self.parent, label=_("Show..."))
		self.__sizer.Add(self.__btn, 0, flag=wx.FIXED_MINSIZE|wx.ALIGN_RIGHT)
		self.__btn.Bind(wx.EVT_BUTTON, self.__onClick)
		self.__sizer.Layout()

		self.addValue(self.__sizer)

	def __onClick(self, event):
		if self.__image is None:
			# First click will generate image
			data = bytearray()
			print("Converting {} bytes of data into {}x{}x4 image data"\
				.format(len(self.__imgdata), self.__size, self.__size))
			for pixel in self.__imgdata:
				data.append(pixel)
			self.__imgdata = None

			#img = wx.Image(self.__size, self.__size, data)
			#-> Will create a monochrome image, sadfully

			bmp = wx.Bitmap.FromBufferRGBA(self.__size, self.__size, data)
			img = bmp.ConvertToImage() #wx.Image(self.__size, self.__size, data)
			data = bmp = None

			#vvvvv DEBUG
			filepath = os.path.join(wx.App.Get().Path, "fog.png")
			img.SaveFile(filepath, wx.BITMAP_TYPE_PNG)
			#^^^^^ DEBUG

			if self.__size > 512:
				new_size = self.__size // 2 
				print("- Scaling down to {}x{}x4".format(new_size, new_size))
				img_new = img.Scale(new_size, new_size, wx.IMAGE_QUALITY_HIGH)
				img.Destroy()
				img = img_new

			self.__image = img.ConvertToBitmap()
			img.Destroy()

			print("Created bitmap of size {}".format(self.__image.Size))

		ImageDlg.ImageDlg(self.parent, "", self.__image).ShowModal()


"""
class Accessor:


'''
Actual save values following
'''

class Property(Accessor):

class PropertyList(Accessor):


'''
Simple types
'''
"""

class BoolProperty(SimpleProperty): pass
class ByteProperty(SimpleProperty): pass
class IntProperty(SimpleProperty): pass
class FloatProperty(SimpleProperty): pass
class StrProperty(SimpleProperty): pass

"""

'''
Complex types
'''

class Header(Accessor):

class Collected(Accessor): #TODO: Find correct name, if any

class StructProperty(Property):
"""

class Vector(Value):
	def createControl(self, val):
		self.__sizer = wx.FlexGridSizer(3, 10,0)
	
		self.__x = wx.TextCtrl(self.parent, value=str(val.X), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__x, 1, flag=wx.EXPAND)
		
		self.__y = wx.TextCtrl(self.parent, value=str(val.Y), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__y, 1, flag=wx.EXPAND)
		
		self.__z = wx.TextCtrl(self.parent, value=str(val.Z), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__z, 1, flag=wx.EXPAND)
		
		self.__sizer.Layout()

		self.addValue(self.__sizer)

class Rotator(Vector): pass
class Scale(Vector): pass

"""
class Box(Accessor):
"""

class Color(Value):
	def createControl(self, val):
		self.__sizer = wx.FlexGridSizer(4, 5,0)
		size = (50,-1)
	
		self.__r = wx.TextCtrl(self.parent, value=str(val.R), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__r, 1, flag=wx.EXPAND)
		
		self.__g = wx.TextCtrl(self.parent, value=str(val.G), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__g, 1, flag=wx.EXPAND)
		
		self.__b = wx.TextCtrl(self.parent, value=str(val.B), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__b, 1, flag=wx.EXPAND)
		
		self.__a = wx.TextCtrl(self.parent, value=str(val.A), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__a, 1, flag=wx.EXPAND)
		
		self.__sizer.Layout()
		
		self.addValue(self.__sizer)

class LinearColor(Value):
	def createControl(self, val):
		self.__sizer = wx.FlexGridSizer(4, 5,0)
		size = (100,-1)
	
		self.__r = wx.TextCtrl(self.parent, value=str(val.R), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__r, 1, flag=wx.EXPAND)
		
		self.__g = wx.TextCtrl(self.parent, value=str(val.G), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__g, 1, flag=wx.EXPAND)
		
		self.__b = wx.TextCtrl(self.parent, value=str(val.B), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__b, 1, flag=wx.EXPAND)
		
		self.__a = wx.TextCtrl(self.parent, value=str(val.A), style=wx.ALIGN_RIGHT, size=size)
		self.__sizer.Add(self.__a, 1, flag=wx.EXPAND)
		
		self.__sizer.Layout()
		
		self.addValue(self.__sizer)

"""
class Transform(PropertyList):
"""

class Quat(Value):
	def createControl(self, val):
		self.__sizer = wx.FlexGridSizer(4, 5,0)
	
		self.__a = wx.TextCtrl(self.parent, value=str(val.A), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__a, 1, flag=wx.EXPAND)
		
		self.__b = wx.TextCtrl(self.parent, value=str(val.B), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__b, 1, flag=wx.EXPAND)
		
		self.__c = wx.TextCtrl(self.parent, value=str(val.C), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__c, 1, flag=wx.EXPAND)
		
		self.__d = wx.TextCtrl(self.parent, value=str(val.D), style=wx.ALIGN_RIGHT)
		self.__sizer.Add(self.__d, 1, flag=wx.EXPAND)
		
		self.__sizer.Layout()
		
		self.addValue(self.__sizer)

"""
class RemovedInstanceArray(PropertyList):

class RemovedInstance(PropertyList):

class InventoryStack(PropertyList):

class InventoryItem(Accessor):#TODO: Might also be some PropertyList? Investigate	
			
class PhaseCost(PropertyList):

class ItemAmount(PropertyList):

class ResearchCost(PropertyList):
	
class CompletedResearch(PropertyList):

class ResearchRecipeReward(PropertyList):

class ItemFoundData(PropertyList):

class RecipeAmountStruct(PropertyList):

class MessageData(PropertyList):

class SplinePointData(PropertyList):

class SpawnData(PropertyList):

class FeetOffset(PropertyList):

class SplitterSortRule(PropertyList):

class ArrayProperty(Property):
"""			

class ObjectProperty(SimpleValue):
	def __init__(self, parent, sizer, label, val):
		super().__init__(parent, sizer, val.Name or "None", val.PathName)

class EnumProperty(SimpleProperty): pass
class NameProperty(SimpleProperty): pass

"""
class MapProperty(Property):
	class Entry(PropertyList):
	
class TextProperty(Property):

class Entity(PropertyList):

class NamedEntity(Entity):
	class Name(Accessor):

class Object(Accessor):

class Actor(Accessor):
"""



"""
# EXPERIMENTAL -> property .Private

class PrivateData(Accessor):

class BP_PlayerState_C(Accessor):

class BP_CircuitSubsystem_C(Collected):

class BP_GameState_C(Collected):

class BP_RailroadSubsystem_C(Accessor):

class BP_GameMode_C(Accessor):

class Build_ConveyorBelt(Accessor):
class Build_ConveyorBeltMk1_C(Build_ConveyorBelt): pass
class Build_ConveyorBeltMk2_C(Build_ConveyorBelt): pass
class Build_ConveyorBeltMk3_C(Build_ConveyorBelt): pass
class Build_ConveyorBeltMk4_C(Build_ConveyorBelt): pass

class Build_PowerLine_C(Collected):

class Build_ConveyorLift(Accessor):
class Build_ConveyorLiftMk1_C(Build_ConveyorLift): pass
class Build_ConveyorLiftMk2_C(Build_ConveyorLift): pass
class Build_ConveyorLiftMk3_C(Build_ConveyorLift): pass
class Build_ConveyorLiftMk4_C(Build_ConveyorLift): pass

class BP_Vehicle(Accessor):
class BP_Tractor_C(BP_Vehicle):
class BP_Truck_C(BP_Vehicle):
"""



'''
Types of controls avail
'' '

class BaseControl:
	def __init__(self, parent, label, val): 
		parent.add(label, self.get_control(parent, val))
	
	def get_control(self, parent, val):
		pass
	
	#def set_limits(self, lower, upper):
	#	self.__lower_bounds = lower
	#	self.__upper_bounds = upper
	#
	#def check_bounds(self):
	#	pass

class BoolControl(BaseControl):
	def get_control(self, parent, val):
		ctrl = wx.CheckBox(parent.Panel)#, validator=?)
		ctrl.Value = wx.CHK_CHECKED if val else wx.CHK_UNCHECKED
		ctrl.Enable(False)
		return ctrl

class ByteControl(BaseControl):
	def get_control(self, parent, val):
		#TODO: Use a spinner and add suitable limits
		ctrl = wx.TextCtrl(parent.Panel, value=val)
		ctrl.Enable(False)
		return ctrl

class IntControl(BaseControl):
	def get_control(self, parent, val):
		#TODO: Use a spinner and add suitable limits
		ctrl = wx.TextCtrl(parent.Panel, value=val)
		ctrl.Enable(False)
		return ctrl

class FloatControl(BaseControl):
	def get_control(self, parent, val):
		#TODO: Use a spinner and add suitable limits? Might be hard to spin on floats, we'll see
		ctrl = wx.TextCtrl(parent.Panel, value=val)
		ctrl.Enable(False)
		return ctrl

class StrControl(BaseControl):
	def get_control(self, parent, val):
		#TODO: Any limits to apply here? Besides not being empty
		ctrl = wx.TextCtrl(parent.Panel, value=val)
		ctrl.Enable(False)
		return ctrl

class GroupControl():
	pass
"""

'''