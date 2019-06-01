'''
Savegame class
'''

import os
from time import sleep


from Savegame \
	import Property, Reader, Writer


class Savegame:
	
	def __init__(self, filename):
		self.__filename = filename


	def load(self, callback=None):
		self.__load(callback)
		
	def save(self, callback=None):
		self.__save(self.__filename, callback)
	
	def save_as(self, new_filename, callback=None):
		self.__save(new_filename, callback)
	
	
	@property
	def Filename(self):
		return os.path.basename(self.__filename)
	
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

	def __cb_read_start(self, reader):
		if self.__callback: self.__callback.start(reader.Size)
		
	def __cb_read_update(self, reader):
		if self.__callback: self.__callback.update(reader.Pos)
		
	def __cb_read_end(self, reader):
		if self.__callback: self.__callback.end(reader.Pos == reader.Size)


	def __load(self, callback):
		self.__callback = callback
		
		reader = Reader.FileReader(self.__filename)
		self.__cb_read_start(reader)

		try:		
			self.Header = Property.Header(self).read(reader)
			self.__total = 1
			self.__cb_read_update(reader)
			
			self.Objects = []
			count = reader.readInt()
			for i in range(count):
				prev_pos = reader.Pos
				_type = reader.readInt()
				if _type == 1:
					obj = Property.Actor(self)
				elif _type == 0:
					obj = Property.Object(self)
				else:
					raise AssertionError("Savegame at pos {}: Unhandled type {}"\
										.format(prev_pos, _type))
				new_child = obj.read(reader) 
				self.Objects.append(new_child)
				#childs = new_child.Childs
				#if childs:
				#	self.__total += self.__count_recurs(childs)
				#-> Entity not yet read, so down below instead
				self.__cb_read_update(reader)
				
			count_ = reader.readInt()
			assert count == count_
	
			for obj in self.Objects:
				obj.read_entity(reader)
				childs = obj.Childs
				if childs:
					self.__total += self.__count_recurs(childs)
				self.__cb_read_update(reader)
	
			self.Collected = []
			count = reader.readInt()
			for i in range(count):
				new_child = Property.Collected(self).read(reader)
				self.Collected.append(new_child)
				childs = new_child.Childs
				if childs:
					self.__total += self.__count_recurs(childs)
				self.__cb_read_update(reader)
	
			self.Missing = reader.readNByte(reader.Size - reader.Pos)
			if self.Missing and len(self.Missing):
				self.__total += 1
			self.__cb_read_update(reader)
			

		except Property.Property.PropertyReadException as exc:
			print(exc)
			raise
		except Reader.ReaderBase.ReadException as exc:
			print(exc)
			raise
			
		except Exception as exc:  
			print("Catched an exception while reading somewhere around pos {}".format(reader.Pos))
			print(exc)
			raise
		
		finally:
			#self.__update_totals() -> Now done while loading
			sleep(0.01)
			self.__cb_read_end(reader)
			del reader


	def __save(self, filename, callback):
		writer = Writer.Writer(filename, callback)
		#...
		del writer


	def __count_recurs(self, childs):
		#print(("  "*self.__depth)+"- Recursing on {}".format(childs))
		#self.__depth += 1
		count = 0
		for name in childs:
			#print(("  "*self.__depth)+"Counting recurs on " + name)
			sub = childs[name]

			count += 1
			if isinstance(sub, (list,dict)):
				for obj in sub:
					if isinstance(sub, Property.Accessor):
						count += 1
						sub_childs = obj.Childs
						if sub_childs:
							count += self.__count_recurs(sub_childs)
					#else:
					#	print(("  "*self.__depth)+"Skipping child '{}'".format(obj))
						
			else:
				if isinstance(sub, Property.Accessor):
					sub_childs = sub.Childs
					if sub_childs:
						count += self.__count_recurs(sub_childs)
					#else:
					#	print(("  "*self.__depth)+"Skipping child '{}'".format(sub))

		#self.__depth -= 1
		return count



