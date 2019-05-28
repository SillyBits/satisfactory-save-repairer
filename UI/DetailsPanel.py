"""
All the panels needed for displaying savegame data
"""

import wx


"""
Simple text-based panel
"" "
class DetailsPanel(wx.StaticText):
	
	def __init__(self, parent):
		super().__init__(parent, size=(300,600))


	def update(self, text, append=False):
		if append:
			self.SetLabel(self.GetLabel() + "\n" + text)
		else:
			self.SetLabel(text)

"""

class DetailsPanel(wx.Panel):
	
	def __init__(self, parent):
		super().__init__(parent, size=(300,600))
		self.__sizer = wx.FlexGridSizer(0, 0, 5, 5)
		self.__sizer.AddGrowableRow(0, proportion=1)
		self.__sizer.AddGrowableCol(0, proportion=1)
		self.SetSizer(self.__sizer)
		self.SetAutoLayout(True)
		self.Layout()
		self.__mode = DetailsPanel.MODE_NONE

	def update(self, text, append=False):
		self.__show_text(text, append)


	def show_property(self, prop):
		pass
		#if not prop:
		#	self.__show_text("<no data avail>")
		#else:
		#	self.__show_prop(prop)


	'''
	Private implementation
	'''
			
	def __delete_all(self):
		self.__mode = DetailsPanel.MODE_NONE
		#self.DestroyChildren()
		self.__sizer.Clear()

	def __show_text(self, text, append=False):
		if self.__mode != DetailsPanel.MODE_TEXT:
			self.__delete_all()
			#ctrl = wx.StaticText(self, label="")#, style=wx.SUNKEN_BORDER)
			ctrl = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_NOHIDESEL|wx.TE_MULTILINE)#|wx.HSCROLL|wx.VSCROLL)#|wx.TE_RICH2)
			#ctrl.HideNativeCaret()
			#ctrl = wx.richtext.RichTextCtrl(self, style=wx.richtext.RE_MULTILINE|wx.richtext.RE_READONLY)
			# Sadfully, caret can't be suppressed with those two controls :-/
			#ctrl.Size = self.ClientSize
			self.__sizer.Add(ctrl, proportion=1, flag=wx.EXPAND)
			self.__sizer.Layout()
			self.__mode = DetailsPanel.MODE_TEXT

		# Have not seen a method to reduce tab size with StaticText,
		# so we just convert them down into simpe spaces
		text_ = text.replace("\t", "    ")
		
		ctrl = self.GetChildren()[0]
		if append:
			#ctrl.SetLabel(ctrl.GetLabel() + text_)
			ctrl.Value += text_
		else:
			#ctrl.SetLabel(text_)
			ctrl.Value = text_

	def __show_prop(self, prop):
		self.__delete_all()
		self.__mode = DetailsPanel.MODE_OBJ
		
		t = prop.TypeName
		if not t in globals():
			self.__show_text(str(prop))
			return
		
		constr = globals()[t]
		inst = constr(self)
		ctrl = inst.populate(self, prop)
		self.__sizer.Add(ctrl, proportion=1, flag=wx.EXPAND)
		self.__sizer.Layout()


		#TODO: Init panel, which might init more sub-panels itself
		#TODO: Use a recursive method for all the hard work
		'''
		collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Details:")
		
		# add the pane with a zero proportion value to the 'sz' sizer which contains it
		sz.Add(collpane, 0, wx.GROW | wx.ALL, 5)
		
		# now add a test label in the collapsible pane using a sizer to layout it:
		win = collpane.GetPane()
		paneSz = wx.BoxSizer(wx.VERTICAL)
		paneSz.Add(wx.StaticText(win, wx.ID_ANY, "test!"), 1, wx.GROW | wx.ALL, 2)
		win.SetSizer(paneSz)
		paneSz.SetSizeHints(win)		
		'''


	MODE_NONE = 0
	MODE_TEXT = 1
	MODE_OBJ  = 2


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

	
'' '
Panels avail
'' '
	
class BasePanel:#(wx.Panel):
	# Actually not really a panel

	def populate(self, parent, prop): 
		parent.add(prop.Name, wx.StaticText(parent.Panel, str(prop.Value)))
	

class GroupPanel(wx.CollapsiblePane):

	@property
	def Panel(self):
		return self.GetPane()
	
	def __init__(self, parent):
		super().__init__(parent, size=parent.ClientSize)
		self.__rows = 0
		self.__grid = wx.GridBagSizer(5, 5)
		self.GetPane().SetSizer(self.__grid)	
		
	def populate(self, parent, prop):
		self.__grid.Layout()

	def add(self, label, ctrl):
		self.__grid.Add(wx.StaticText(self.Panel, label=label), \
					pos=(self.__rows,0), flag=wx.TOP|wx.LEFT|wx.BOTTOM)
		self.__grid.Add(ctrl, pos=(self.__rows,1), flag=wx.TOP|wx.LEFT|wx.BOTTOM)
		self.__grid.AddGrowableRow(self.__rows)
		self.__rows += 1



"""

'' '
Actual save values following
'' '

class Property(Accessor):
	
	Name = None
	Length = 0
	Index = 0
	Value = None

	#@property
	#def Childs(self):
	#	return None #{ 'Entity': self.Entity }


	def __init__(self, name=None, length=None, index=None, value=None):
		self.Name = name
		self.Length = length
		self.Index = index
		self.Value = value

	def __str__(self):
		return '[' + self.TypeName + '] ' + getSafeStr(self.Name)


	@staticmethod
	def read(reader):
		name = reader.readStr()
		if name == 'None': 
			return
		
		prop = reader.readStr()
		if not prop in globals():
			raise Property.PropertyReadException(reader, "Unknown type '{}'".format(prop))
		
		length = reader.readInt()
		index = reader.readInt()

		inst = globals()[prop](name, length, index)
		return inst.read(reader)


	def checkNullByte(self, reader):
		val = reader.readByte()
		if val != 0:
			#Property.raise_error(reader.Pos, "NULL byte expected but found {}".format(val))
			raise Property.PropertyReadException(reader, "NULL byte expected but found {}".format(val))

	def checkNullInt(self, reader):
		val = reader.readInt()
		if val != 0:
			#Property.raise_error(reader.Pos, "NULL int expected but found {}".format(val))
			raise Property.PropertyReadException(reader, "NULL int expected but found {}".format(val))


	def write(self, writer): pass


	@staticmethod
	def raise_error(pos, msg):
		raise "ERROR at pos {}: {}".format(pos, msg)
		#raise Property.PropertyReadException(reader, msg) 		

		
	class PropertyReadException(Exception):
		def __init__(self, reader, msg):
			self.reader = reader
			self.message = "[{}@{}] "\
				.format(os.path.basename(reader.Filename), reader.PrevPos) + msg
				
		def __str__(self, *args, **kwargs):
			return self.message + "\n" + Exception.__str__(self, *args, **kwargs)


class PropertyList(Accessor):
	def __str__(self):
		return '[{}] '.format(len(self.Value)) \
			+ (getSafeStr(self.Value[0]) if len(self.Value) else '<?>')

	@property
	def Childs(self):
		return { 'Values': self.Value }
	
	def read(self, reader):
		self.Value = []
		while (True):
			prop = Property.read(reader)
			if not prop:
				break
			self.Value.append(prop)
		return self


	

'' '
Complex types
'' '

class Header(Accessor):
	def read(self, reader):
		self.Type = reader.readInt()
		self.Version = reader.readInt()
		self.BuildVersion = reader.readInt()
		self.MapName = reader.readStr()
		self.MapOptions = reader.readStr()
		self.SessionName = reader.readStr()
		self.PlayDuration = reader.readInt() # in seconds
		self.SaveDateTime = reader.readLong()
		self.Visibility = reader.readByte()
		return self
		"""
		to convert SaveDateTime to a unix timestamp use:
			saveDateSeconds = SaveDateTime / 10000000
			print(saveDateSeconds-62135596800)
		see https://stackoverflow.com/a/1628018
		"""

class Collected(Accessor): #TODO: Find correct name, if any
	def __str__(self):
		return '[COLL] ' + self.PathName

	@property
	def Childs(self):
		return None #{ 'Entity': self.Entity }
	
	def read(self, reader):
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		return self

class StructProperty(Property):
	#TODO
	#@property
	#def Childs(self):
	#	return { 'Entity': self.Entity }

	def read(self, reader):
		self.IsArray = False

		inner = reader.readStr()
		if not inner in globals():
			raise Property.PropertyReadException(reader, "Unknown inner structure type '{}'".format(inner))

		self.Unknown = reader.readNByte(17)

		self.Value = globals()[inner]()
		self.Value.read(reader)
		return self

	def read_as_array(self, reader, count):
		self.IsArray = True

		inner = reader.readStr()
		if not inner in globals():
			raise Property.PropertyReadException(reader, "Unknown inner structure type '{}'".format(inner))

		self.Unknown = reader.readNByte(17)
		
		constr = globals()[inner]
		self.Value = []
		for i in range(count):
			inst = constr()
			self.Value.append(inst.read(reader))
		return self

class Vector(Accessor):
	def read(self, reader):
		self.X = reader.readFloat()
		self.Y = reader.readFloat()
		self.Z = reader.readFloat()
		return self

class Rotator(Vector): 
	pass

class Box(Accessor):
	def read(self, reader):
		self.MinX = reader.readFloat()
		self.MinY = reader.readFloat()
		self.MinZ = reader.readFloat()
		self.MaxX = reader.readFloat()
		self.MaxY = reader.readFloat()
		self.MaxZ = reader.readFloat()
		self.IsValid = reader.readByte()#TODO: readBool?
		return self

class Color(Accessor):
	def read(self, reader):
		self.R = reader.readByte()
		self.G = reader.readByte()
		self.B = reader.readByte()
		self.A = reader.readByte()
		return self

class LinearColor(Color):
	def read(self, reader):
		self.R = reader.readFloat()
		self.G = reader.readFloat()
		self.B = reader.readFloat()
		self.A = reader.readFloat()
		return self

class Transform(PropertyList):
	pass
	
class Quat(Accessor):
	def read(self, reader):
		self.A = reader.readFloat()
		self.B = reader.readFloat()
		self.C = reader.readFloat()
		self.D = reader.readFloat()
		return self

class RemovedInstanceArray(PropertyList):
	pass

class RemovedInstance(PropertyList):
	pass

class InventoryStack(PropertyList):
	def read(self, reader):
		return PropertyList.read(self, reader)

class InventoryItem(Accessor):#TODO: Might also be some PropertyList? Investigate	
	def __str__(self):
		return '[' + self.TypeName + '] ' + getSafeStr(self.ItemName)
	
	def read(self, reader):
		self.Unknown = reader.readStr()
		self.ItemName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.Value = Property.read(reader)
		return self
			
class PhaseCost(PropertyList):
	pass

class ItemAmount(PropertyList):
	pass

class ResearchCost(PropertyList):
	pass
	
class CompletedResearch(PropertyList):
	pass

class ResearchRecipeReward(PropertyList):
	pass

class ItemFoundData(PropertyList):
	pass

class RecipeAmountStruct(PropertyList):
	pass

class MessageData(PropertyList):
	pass

class SplinePointData(PropertyList):
	pass

class SpawnData(PropertyList):
	pass

class FeetOffset(PropertyList):
	pass

class SplitterSortRule(PropertyList):
	pass

class ArrayProperty(Property):
	#TODO
	#@property
	#def Childs(self):
	#	return { 'Entity': self.Entity }

	def read(self, reader):
		self.InnerType = reader.readStr()
		
		if self.InnerType == "StructProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			name = reader.readStr()
			_type = reader.readStr()
			assert _type == self.InnerType
			length = reader.readInt()
			index = reader.readInt()
			self.Value = StructProperty(name, length, index)
			self.Value.read_as_array(reader, count)
		elif self.InnerType == "ObjectProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = []
			for i in range(count):
				self.Value.append(ObjectProperty().read(reader, False))
		elif self.InnerType == "IntProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = reader.readNInt(count)
		elif self.InnerType == "ByteProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = reader.readNByte(count)
		else:
			raise Property.PropertyReadException(reader, "Unknown inner array type '{}'".format(self.InnerType))

		return self
	
class ObjectProperty(Property):
	def read(self, reader, nullCheck=True):
		if nullCheck:
			self.checkNullByte(reader)
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		return self
	
class EnumProperty(Property):
	def read(self, reader):
		self.EnumName = reader.readStr()
		self.checkNullByte(reader)
		self.Value = reader.readStr() # ValueName
		return self
	
class NameProperty(StrProperty):
	#def read(self, reader):
	#	self.checkNullByte(reader)
	#	self.value = reader.readStr()
	#	return self
	pass

class MapProperty(Property):
	def read(self, reader):
		self.MapName = reader.readStr()
		self.ValueType = reader.readStr()
		for i in range(5):
			self.checkNullByte(reader)
		count = reader.readInt()
		self.Value = {}
		for i in range(count):
			key = reader.readInt();
			entry = MapProperty.Entry(key)
			self.Value[key] = entry.read(reader)
		return self

	class Entry(PropertyList):
		def __init__(self, key):
			self.Key = key
	
class TextProperty(Property):
	def read(self, reader):
		self.checkNullByte(reader)
		self.Unknown = reader.readNByte(13)
		self.Value = reader.readStr()
		return self

class Entity(PropertyList):
	def __str__(self):
		return '[ENTITY] ' + getSafeStr(self.PathName)

	#@property
	#def Childs(self):
	#	return None #{ 'Entity': self.Entity }
	
	def __init__(self, level_name=None, path_name=None, children=None):
		self.LevelName = level_name
		self.PathName = path_name
		self.Children = children
	
	def read(self, reader, length):
		last_pos = reader.Pos
		super().read(reader)
		bytesRead = reader.Pos - last_pos
		if bytesRead < 0:
			raise Property.PropertyReadException(reader, "Negative offset")
		if bytesRead != length:
			self.Missing = reader.readNByte(length - bytesRead) 
		else:
			self.Missing = None
		return self

class NamedEntity(Entity):
	def __str__(self):
		return '[ENTITY] ' + getSafeStr(self.PathName)

	#@property
	#def Childs(self):
	#	return { 'Children': self.Children }
	
	def read(self, reader, length):
		last_pos = reader.Pos
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		count = reader.readInt()
		self.Children = []
		for i in range(count): 
			self.Children.append(NamedEntity.Name().read(reader))
		bytesRead = reader.Pos - last_pos
		if bytesRead < 0:
			raise Property.PropertyReadException(reader, "Negative offset")
		super().read(reader, length - bytesRead)
		return self
		
	class Name:
		def read(self, reader):
			self.LevelName = reader.readStr()
			self.PathName = reader.readStr()
			return self

class Object(Accessor):
	def __str__(self):
		return '[OBJ] ' + getSafeStr(self.ClassName)

	@property
	def Childs(self):
		return { 'Entity': self.Entity }
	
	def read(self, reader):
		self.Type = 0
		self.ClassName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.OuterPathName = reader.readStr()
		return self

	def read_entity(self, reader):
		length = reader.readInt()
		self.Entity = Entity().read(reader, length)
"""

'' '
Simple types
'' '

class BoolProperty(BasePanel): pass

class ByteProperty(BasePanel): pass
	
class IntProperty(BasePanel): pass

class FloatProperty(BasePanel): pass
	
class StrProperty(BasePanel): pass



class Actor(GroupPanel):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.__controls = {}
		
	def populate(self, parent, prop):
		#pass#BasePanel.populate(self, prop)
		#self._add("Label", wx.StaticText(parent, "Ctrl"))
		"""
		self.add("ClassName", StrProperty().populate(self.Panel, prop.ClassName))
		self.add("LevelName", StrProperty().populate(self.Panel, prop.LevelName))
		self.add("PathName", StrProperty().populate(self.Panel, prop.PathName))
		self.add("NeedTransform", StrProperty().populate(self.Panel, prop.NeedTransform))
		self.add("Rotation", StrProperty().populate(self.Panel, prop.Rotation))
		self.add("Translate", StrProperty().populate(self.Panel, prop.Translate))
		self.add("Scale", StrProperty().populate(self.Panel, prop.Scale))
		self.add("WasPlacedInLevel", IntProperty().populate(self.Panel, prop.WasPlacedInLevel))
		"""
		self.__controls['ClassName'] = StrControl(self, "ClassName", prop.ClassName)
		self.__controls['LevelName'] = StrControl(self, "LevelName", prop.LevelName)
		self.__controls['PathName']  = StrControl(self, "PathName" , prop.PathName)
		self.__controls['NeedTransform'] = BoolControl(self, "NeedTransform", prop.NeedTransform)
		#StrProperty().populate(self, prop.Rotation)
		#StrProperty().populate(self, prop.Translate)
		#StrProperty().populate(self, prop.Scale)
		self.__controls['WasPlacedInLevel'] = BoolControl(self, "WasPlacedInLevel", prop.WasPlacedInLevel)
		super().populate(parent, prop)
		


	"""
	def __str__(self):
		return '[ACTOR] ' + getSafeStr(self.PathName)

	@property
	def Childs(self):
		return { 'Entity': self.Entity }
	
	def read(self, reader):
		self.Type = 1
		self.ClassName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.NeedTransform = reader.readInt()
		self.Rotation = Quat().read(reader)
		self.Translate = Vector().read(reader)
		self.Scale = Vector().read(reader)
		self.WasPlacedInLevel = reader.readInt()
		return self

	def read_entity(self, reader):
		length = reader.readInt()
		self.Entity = NamedEntity().read(reader, length)
	"""



'' '
Helpers
'' '
		
def getSafeStr(s):
	return s or '<none>'

'''