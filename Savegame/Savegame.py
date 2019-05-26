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
		
		reader = Reader.Reader(self.__filename)
		self.__cb_read_start(reader)

		try:		
			self.Header = Property.Header().read(reader)
			self.__cb_read_update(reader)
			
			self.Objects = []
			count = reader.readInt()
			for i in range(count):
				prev_pos = reader.Pos
				_type = reader.readInt()
				if _type == 1:
					obj = Property.Actor()
				elif _type == 0:
					obj = Property.Object()
				else:
					raise AssertionError("Savegame at pos {}: Unknown type {}"\
										.format(prev_pos, _type))
				self.Objects.append(obj.read(reader))
				self.__cb_read_update(reader)
				
			count_ = reader.readInt()
			assert count == count_
	
			#TODO: 2nd object fails badly :(		
			for obj in self.Objects:
				obj.read_entity(reader)
				self.__cb_read_update(reader)
	
			self.Collected = []
			count = reader.readInt()
			for i in range(count):
				self.Collected.append(Property.Collected().read(reader))
				self.__cb_read_update(reader)
	
			self.Missing = reader.readNByte(reader.Size - reader.Pos)
			self.__cb_read_update(reader)
			

		except Property.Property.PropertyReadException as exc:
			print(exc)
			raise
		except Reader.Reader.ReadException as exc:
			print(exc)
			raise
			
		except Exception as exc:  
			print("Catched an exception while reading somewhere around pos {}".format(reader.Pos))
			print(exc)
			raise
		
		finally:
			self.__update_totals()
			sleep(1)
			self.__cb_read_end(reader)
			del reader


	def __save(self, filename, callback):
		writer = Writer.Writer(filename, callback)
		#...
		del writer


	def __update_totals(self):
		# Count total number of elemts avail
		self.__total = 0
				
		for obj in self.Objects:
			self.__total += 1
			childs = obj.Childs
			if childs:
				self.__total += self._count_recurs(childs)
				
		#self.__total += 1 + len(
		for obj in self.Collected:
			self.__total += 1
			# Does this entry need more depth analysis?

	def _count_recurs(self, childs):
		count = 0
		for name in childs:
			sub = childs[name]

			count += 1
			if isinstance(sub, (list,dict)):
				for obj in sub:
					count += 1
					childs = obj.Childs
					if childs:
						count += self._count_recurs(childs)
			else:
				childs = sub.Childs
				if childs:
					count += self._count_recurs(childs)

		return count



