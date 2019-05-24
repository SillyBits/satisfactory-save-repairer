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


	'''
	Private implementation
	'''

	def __cb_start(self, reader):
		if self.__callback: self.__callback.start(reader.Size)
		
	def __cb_update(self, reader):
		if self.__callback: self.__callback.update(reader.Pos)
		
	def __cb_end(self, reader):
		if self.__callback: self.__callback.end(reader.Pos == reader.Size)


	def __load(self, callback):
		self.__callback = callback
		
		reader = Reader.Reader(self.__filename)#, callback)
		self.__cb_start(reader)

		try:		
			self.Header = Savegame.Header().read(reader)
			self.__cb_update(reader)
			
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
				self.__cb_update(reader)
				
			count_ = reader.readInt()
			assert count == count_
	
			#TODO: 2nd object fails badly :(		
			for obj in self.Objects:
				obj.read_entity(reader)
				self.__cb_update(reader)
	
			self.Collected = []
			count = reader.readInt()
			for i in range(count):
				self.Collected.append(Savegame.Collected().read(reader))
				self.__cb_update(reader)
	
			self.Missing = reader.readNByte(reader.Size - reader.Pos)
			self.__cb_update(reader)
			

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
			sleep(1)
			self.__cb_end(reader)
			del reader


	def __save(self, filename, callback):
		writer = Writer.Writer(filename, callback)
		#...
		del writer
		

	class Header:
		#@property
		#def Type(self): return self.__class__
		
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

	class Collected: #TODO: Find correct name, if any
		@property
		def Type(self): return self.__class__
		
		def read(self, reader):
			self.LevelName = reader.readStr()
			self.PathName = reader.readStr()
			return self

		@property
		def Label(self):
			return '[COLL] ' + self.PathName

		@property
		def Childs(self):
			return None #{ 'Entity': self.Entity }



