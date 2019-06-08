'''
Savegame class
'''

from os \
	import path 


import AppConfig

from Savegame \
	import Property, PropertyDumper, Reader, Writer

from Util \
	import Log


class Savegame:
	
	def __init__(self, filename):
		self.__filename = filename

		self.Header = None
		self.Objects = None
		self.Collected = None
		self.Missing = None


	def load(self, callback=None):
		self.__load(callback)
		
	def save(self, callback=None):
		self.__save(self.__filename, callback)
	
	def save_as(self, new_filename, callback=None):
		self.__save(new_filename, callback)
	
	
	@property
	def Filename(self):
		return path.basename(self.__filename)
	
	#@property
	#def FilePath(self):
	#	return os.path.basename(self.__filename)
	
	@property
	def FullFilename(self):
		return self.__filename

	@property
	def TotalElements(self):
		return self.__total


	'''
	Private implementation
	'''

	def __cb_read_start(self, reader, status=None, info=None):
		if self.__callback: 
			self.__callback.start(reader.Size, status=status, info=info)

	def __cb_read_update(self, reader, status=None, info=None):
		if self.__callback: 
			self.__callback.update(reader.Pos, status=status, info=info)
	def __cb_read_end(self, reader):
		if self.__callback: 
			self.__callback.end(reader.Pos == reader.Size)


	def __load(self, callback):
		self.__callback = callback
		
		reader = Reader.FileReader(self.__filename)
		Log.Log("-> {:,d} Bytes".format(reader.Size), add_ts=False)

		self.__cb_read_start(reader, _("Loading file ..."), "")

		try:		
			self.Header = Property.Header(self).read(reader)
			self.__total = 1
			self.__cb_read_update(reader, None, _("Header"))

			# Writing header to log
			dumper = PropertyDumper.Dumper(
				lambda text: Log.Log(text, add_ts=False, add_newline=False))
			dumper.Dump(self.Header)
			dumper = None

			self.Objects = []
			count = reader.readInt()
			Log.Log("-> {:,d} game objects".format(count), add_ts=False)
			for i in range(count):
				prev_pos = reader.Pos
				_type = reader.readInt()
				if _type == 1:
					obj = Property.Actor(self)
				elif _type == 0:
					obj = Property.Object(self)
				else:
					raise AssertionError("Savegame at pos {:,d}: Unhandled type {}"\
										.format(prev_pos, _type))
				new_child = obj.read(reader) 
				self.__total += 1
				self.Objects.append(new_child)
				#self.__total += self.__count_recurs(new_child.Childs)
				#-> Entity not yet read, so down below instead
				self.__cb_read_update(reader, None, str(obj))

			count_ = reader.readInt()
			assert count == count_
	
			for obj in self.Objects:
				obj.read_entity(reader)
				self.__total += self.__count_recurs(obj.Childs)
				self.__cb_read_update(reader, None, str(obj))
			
			self.Collected = []
			count = reader.readInt()
			Log.Log("-> {:,d} collected objects".format(count), add_ts=False)
			for i in range(count):
				new_child = Property.Collected(self).read(reader)
				self.__total += 1
				self.Collected.append(new_child)
				self.__total += self.__count_recurs(new_child.Childs)
				self.__cb_read_update(reader, None, str(new_child))

			self.Missing = reader.readNByte(reader.Size - reader.Pos)
			if self.Missing and len(self.Missing):
				Log.Log("-> Found extra data of size {:,d} at end of file".format(len(self.Missing)), add_ts=False)
				self.__total += 1
			self.__cb_read_update(reader, None, _("Done loading"))

		except Property.Property.PropertyReadException as exc:
			print(exc)
			if AppConfig.DEBUG: 
				raise

		except Reader.ReaderBase.ReadException as exc:
			print(exc)
			if AppConfig.DEBUG: 
				raise

		except Exception as exc:  
			print("Catched an exception while reading somewhere around pos {:,d}".format(reader.Pos))
			print(exc)
			if AppConfig.DEBUG: 
				raise

		finally:
			#self.__update_totals() -> Now done while loading
			self.__cb_read_end(reader)
			del reader


	def __save(self, filename, callback):
		raise ValueError # Not allowed yet
		#writer = Writer.Writer(filename, callback)
		#...
		#del writer


	def __count_recurs(self, childs):
		#print(("  "*self.__depth)+"- Recursing on {}".format(childs))
		#self.__depth += 1
		count = 0
		for name,prop in childs.items():
			#print(("  "*self.__depth)+"Counting recurs on " + name)
			
			#count += 1 # Count w/ or w/o None objects? A good question
			if prop is None:
				continue
			count += 1 # Count w/ or w/o None objects? A good question

			if isinstance(prop, (list,dict)):
				for obj in prop:
					#count += 1 # <- Moved here to count 'simple' types too (e.g. strings)
					# Sadfully, this would also count .Missing array content -.-
					if isinstance(obj, Property.Accessor):
						count += 1
						count += self.__count_recurs(obj.Childs)

					#TODO: Sub-lists to be counted here too?
					#else:
					#	print(("  "*self.__depth)+"Skipping child '{}'".format(obj))

			elif isinstance(prop, Property.Accessor):
				count += self.__count_recurs(prop.Childs)

			"""			
			elif isinstance(prop, (str,int,float)):
				continue
			else:
				Log.Log("?? Don't know how to count this object\n -> " + str(type(prop)),
					severity=Log.LOG_ERROR)
			"""

		#self.__depth -= 1
		return count



