
import os


'''
To allow for abstract access to property values

Quite some abuse here and there, but doing the "job" well
'''
class Accessor:

	# List of reserved name not to be populated by 'Keys'
	__reserved_names = [ "Keys", "Childs" ]


	@property
	def TypeName(self):
		'''
		Returns property name
		'''
		return self.__class__.__qualname__
	
	@property
	def Keys(self):
		'''
		Returns list of iterable properties
		'''
		if not hasattr(self, Accessor.__prop_keys):
			# Create new cache of keys avail
			self.__keys = []
			for member in dir(self):
				if member.startswith('_'):
					continue # Skip private members
				if member in self.__reserved_names:
					continue # A reserved name like 'Keys'
				value = self[member]
				if callable(value):
					continue # Skip callables
				self.__keys.append(member)
		return self.__keys

	@property
	def Childs(self):
		'''
		Returns list of childs to be processed as well
		Might be removed in favour of Keys() and detecting sequences
		''' 
		return None


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


	__prop_keys = '_Accessor__keys'
	__prop_error = '_Accessor__errors'


'''
Actual save values following
'''

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

class Actor(Accessor):
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



'''
Helpers
'''
		
def getSafeStr(s):
	return s or _('<none>')



