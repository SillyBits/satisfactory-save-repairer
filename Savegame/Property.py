
import os


from Util \
	import Log


class Accessor:
	'''
	To allow for abstract access to property values.
	
	'''

	@property
	def TypeName(self):
		'''
		Returns property name
		'''
		return self.__class__.__qualname__


	# List of reserved name to be skipped at all times
	__reserved_names = [ 
		"TypeName", "Keys", "Exclusions", "Childs", "Root", "Parent",
		"HasErrors", "Errors", "AddError",
	]
	__keys = {}

	@property
	def Keys(self):
		'''
		Returns list of iterable properties.
		Will be cached for each property on first call 
		'''
		t = self.TypeName
		if t not in Accessor.__keys:
			# Create new cache entry for this type of property
			keys = []
			for member in dir(self):
				if member.startswith('_'):
					continue # Skip any private member
				if member in Accessor.__reserved_names:
					continue # A any reserved name like 'Keys'
				#if member in self.Exclusions:
				#	continue # Explicit exclusion
				if callable(self[member]):
					continue # Skip callables
				keys.append(member)
			Accessor.__keys[t] = keys
			Log.Log("** New mapping for type {}\n   -> {}".format(t, keys), 
						severity=Log.LOG_DEBUG)
		return Accessor.__keys[t]
	
	"""
	@property
	def Exclusions(self):
		'''
		Returns a list of values to exclude
		(NOT yet used)
		''' 
		return []
	"""
	
	@property
	def Childs(self):
		'''
		Returns a dict of childs to be processed recursively
		''' 
		childs = {}
		for k in self.Keys:
			childs[k] = self[k]
		return childs

	@property
	def Root(self):
		'''
		Find top-most parent property
		'''
		curr = self
		while curr:
			if not isinstance(curr.__parent, Accessor):
				break
			curr = curr.__parent
		return curr

	@property
	def Parent(self):
		return self.__parent


	@property
	def HasErrors(self):
		'''
		Did validation encounter any errors in this property
		'''
		return hasattr(self, Accessor.__prop_error)
	
	@property
	def Errors(self):
		'''
		Return list of errors encountered in this property, or None
		'''
		return self.__errors if hasattr(self, Accessor.__prop_error) else None
	
	def AddError(self, info):
		'''
		Adds a validation error to this property
		'''
		if not hasattr(self, Accessor.__prop_error):
			self.__errors = []
		self.__errors.append(info)

	__prop_error = '_Accessor__errors'


	'''
	Private implementation
	'''

	def __init__(self, parent):
		self.__parent = parent

	def __getitem__(self, key):
		v = object.__getattribute__(self, key)
		if hasattr(v, '__get__'):
			return v.__get__(None, self)
		return v

	def __setitem__(self, key, value):
		raise ValueError # Not allowed yet
		v = object.__getattribute__(self, key)
		if hasattr(v, '__set__'):
			v.__set__(None, self, value)
		else:
			v = value

	def __str__(self):
		return "[" + self.TypeName + "]"



'''
Actual save values following
'''

class Property(Accessor):

	def __init__(self, parent, name=None, length=None, index=None, value=None):
		super().__init__(parent)
		self.Name = name
		self.Length = length
		self.Index = index
		self.Value = value

	def __str__(self):
		return '[' + self.TypeName + '] ' + getSafeStr(self.Name)


	def read(self, reader):
		name = reader.readStr()
		if name == 'None': 
			return
		
		prop = reader.readStr()
		if not prop in globals():
			raise Property.PropertyReadException(reader, 
				"Unknown type '{}'".format(prop))
		
		length = reader.readInt()
		index = reader.readInt()

		cls = globals()[prop]
		inst = cls(self, name, length, index)
		return inst.read(reader)


	def checkNullByte(self, reader):
		val = reader.readByte()
		if val != 0:
			raise Property.PropertyReadException(reader, 
				"NULL byte expected but found {}".format(val))

	def checkNullInt(self, reader):
		val = reader.readInt()
		if val != 0:
			raise Property.PropertyReadException(reader, 
				"NULL int expected but found {}".format(val))


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
	'''
	Multiple properties of same type as array
	'''
	def __str__(self):
		return "[{}].Value[0-{}]".format(self.TypeName, len(self.Value)-1)
	
	def read(self, reader):
		self.Value = []
		while (True):
			prop = Property(self).read(reader)
			if not prop:
				break
			self.Value.append(prop)
		return self


'''
Simple types
'''
	
class BoolProperty(Property):
	def read(self, reader):
		self.Value = reader.readByte()
		self.checkNullByte(reader)
		return self
	
class ByteProperty(Property):
	def read(self, reader):
		self.Unknown = reader.readStr()
		self.checkNullByte(reader)
		if self.Unknown == "None":
			self.Value = reader.readByte()
		else:
			self.Value = reader.readStr()
		return self
	
class IntProperty(Property):
	def read(self, reader):
		self.checkNullByte(reader)
		self.Value = reader.readInt()
		return self

class FloatProperty(Property):
	def read(self, reader):
		self.checkNullByte(reader)
		self.Value = reader.readFloat()
		return self
	
class StrProperty(Property):
	def read(self, reader):
		self.checkNullByte(reader)
		self.Value = reader.readStr()
		return self
	

'''
Complex types
'''

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
		# According to Goz3rr's loader, this byte is avail only with Version>=5?
		self.Visibility = reader.readByte()
		return self
		'''
		to convert SaveDateTime to a unix timestamp use:
			saveDateSeconds = SaveDateTime / 10000000
			print(saveDateSeconds-62135596800)
		see https://stackoverflow.com/a/1628018
		'''

class Collected(Accessor): #TODO: Find correct name, if any
	def __str__(self):
		return "[" + self.TypeName + "] " + self.PathName

	def read(self, reader):
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		return self

class StructProperty(Property):
	def read(self, reader):
		self.IsArray = False

		inner = reader.readStr()
		if not inner in globals():
			raise Property.PropertyReadException(reader, 
				"Unknown inner structure type '{}'".format(inner))

		self.Unknown = reader.readNByte(17)

		cls = globals()[inner]
		inst = cls(self)
		self.Value = inst.read(reader)
		return self

	def read_as_array(self, reader, count):
		self.IsArray = True

		inner = reader.readStr()
		if not inner in globals():
			raise Property.PropertyReadException(reader, 
				"Unknown inner structure type '{}'".format(inner))

		self.Unknown = reader.readNByte(17)
		
		cls = globals()[inner]
		self.Value = []
		for i in range(count):
			inst = cls(self)
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

# 'Scale' is a pseudo-class and not contained, added for the 
# validation step as different set of bounds must be used
class Scale(Vector):
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
	pass

class InventoryItem(Accessor):#TODO: Might also be some PropertyList? Investigate	
	def __str__(self):
		return "[" + self.TypeName + "] " + getSafeStr(self.ItemName)
	
	def read(self, reader):
		self.Unknown = reader.readStr()
		self.ItemName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.Value = Property(self).read(reader)
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
			self.Value = StructProperty(self, name, length, index)
			self.Value.read_as_array(reader, count)
		elif self.InnerType == "ObjectProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = []
			for i in range(count):
				self.Value.append(ObjectProperty(self).read(reader, False))
		elif self.InnerType == "IntProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = reader.readNInt(count)
		elif self.InnerType == "ByteProperty":
			self.checkNullByte(reader)
			count = reader.readInt()
			self.Value = reader.readNByte(count)
		else:
			raise Property.PropertyReadException(reader, 
				"Unknown inner array type '{}'".format(self.InnerType))

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
			entry = MapProperty.Entry(self, key)
			self.Value[key] = entry.read(reader)
		return self

	class Entry(PropertyList):
		def __init__(self, parent, key):
			super().__init__(parent)
			self.Key = key
	
class TextProperty(Property):
	def read(self, reader):
		self.checkNullByte(reader)
		self.Unknown = reader.readNByte(13)
		self.Value = reader.readStr()
		return self

class Entity(PropertyList):
	def __str__(self):
		return "[" + self.TypeName + "] " + getSafeStr(self.PathName)
	
	def __init__(self, parent, level_name=None, path_name=None, children=None):
		super().__init__(parent)
		self.LevelName = level_name
		self.PathName = path_name
		self.Children = children
	
	def read(self, reader, length):
		last_pos = reader.Pos
		super().read(reader)
		#TODO: There is an extra 'int' following, investigate!
		# Not sure if this is valid for all elements which are of type
		# PropertyList. For now,  we will handle it only here
		self.Unknown = reader.readInt()
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
		return "[" + self.TypeName + "] " + getSafeStr(self.PathName)

	def read(self, reader, length):
		last_pos = reader.Pos
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		count = reader.readInt()
		self.Children = []
		for i in range(count): 
			self.Children.append(NamedEntity.Name(self).read(reader))
		bytesRead = reader.Pos - last_pos
		if bytesRead < 0:
			raise Property.PropertyReadException(reader, "Negative offset")
		super().read(reader, length - bytesRead)
		return self

	class Name(Accessor):
		def read(self, reader):
			self.LevelName = reader.readStr()
			self.PathName = reader.readStr()
			return self

class Object(Accessor):
	def __str__(self):
		return "[" + self.TypeName + "] " + getSafeStr(self.ClassName)
	
	def read(self, reader):
		self.Type = 0
		self.ClassName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.OuterPathName = reader.readStr()
		return self

	def read_entity(self, reader):
		length = reader.readInt()
		self.Entity = Entity(self).read(reader, length)

class Actor(Accessor):
	def __str__(self):
		return "[" + self.TypeName + "] " + getSafeStr(self.PathName)
	
	def read(self, reader):
		self.Type = 1
		self.ClassName = reader.readStr()
		self.LevelName = reader.readStr()
		self.PathName = reader.readStr()
		self.NeedTransform = reader.readInt()
		self.Rotation = Quat(self).read(reader)
		self.Translate = Vector(self).read(reader)
		self.Scale = Scale(self).read(reader)
		self.WasPlacedInLevel = reader.readInt()
		return self

	def read_entity(self, reader):
		length = reader.readInt()
		self.Entity = NamedEntity(self).read(reader, length)



'''
Helpers
'''
		
def getSafeStr(s):
	return s or _('<none>')



