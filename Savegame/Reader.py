
"""
All code related to reading binary data, either from files or from memory streams
"""

import os
import struct


TYPE_INT   = struct.Struct('i')
TYPE_FLOAT = struct.Struct('f')
TYPE_LONG  = struct.Struct('q')
TYPE_BYTE  = struct.Struct('B')


class ReaderBase:

	def __init__(self, callback=None):
		self.__callback = callback

		self.__prev_pos = -1
		self.__pos = 0

		self.__cb_start()


	@property
	def Pos(self): 
		return self.__pos	

	@property
	def PrevPos(self): 
		return self.__prev_pos	

	@property
	def Size(self): 
		pass

	@property
	def Name(self): 
		pass


	'''
	Readers for basic types: int, float, long & byte.
	'''

	def readInt(self):            return self.__read(TYPE_INT)
	def readNInt(self, length):   return self.__readN(TYPE_INT, length)

	def readFloat(self):          return self.__read(TYPE_FLOAT)
	def readNFloat(self, length): return self.__readN(TYPE_FLOAT, length)

	def readLong(self):           return self.__read(TYPE_LONG)		
	def readNLong(self, length):  return self.__readN(TYPE_LONG, length)   

	def readByte(self):           return self.__read(TYPE_BYTE)
	def readNByte(self, length):  return self.__readN(TYPE_BYTE, length)


	'''
	Reads a string, if len=None it's assumed to be prefixed with its length.
	'''
	def readStr(self, _len=None):
		self.__prev_pos = self.__pos	

		length = _len or self.readInt()

		sz = ""

		if length < 0:
			# Read unicode string

			length = length * -2

			chars = self.get(length-2)
			self.__pos += length-2

			zero = self.get(2)
			self.__pos += 2
			if zero != b'\x00\x00':  # We assume that the last byte of a string is always \x00
				raise ReaderBase.ReadException(self, 
					"String terminator is '{}' in '{}'".format(zero, chars))

			sz = chars.decode('utf-16')

		elif length > 0:
			# Read 8bit-ASCII

			chars = self.get(length-1)
			self.__pos += length-1
			
			zero = self.get(1)
			self.__pos += 1
			if zero != b'\x00':  # We assume that the last byte of a string is always \x00
				raise ReaderBase.ReadException(self, 
					"String terminator is '{}' in '{}'".format(zero, chars))

			sz = chars.decode('ascii')

		return sz


	class ReadException(Exception):
		def __init__(self, reader, msg):
			self.reader = reader
			self.message = "[{}@{:,d}] "\
				.format(reader.Name, reader.PrevPos) + msg

		def __str__(self, *args, **kwargs):
			return self.message + "\n" + Exception.__str__(self, *args, **kwargs) 


	'''
	Private implementation
	'''

	def __cb_start(self):
		if self.__callback: self.__callback.start(self.Size)

	def __cb_update(self):
		if self.__callback: self.__callback.update(self.Pos)

	def __cb_end(self, state):
		if self.__callback: self.__callback.end(state)


	def __read(self, fmt):
		self.__prev_pos = self.__pos
		val = fmt.unpack(self.get(fmt.size))[0]
		self.__pos += fmt.size
		self.__cb_update()
		return val

	def __readN(self, fmt, length):
		self.__prev_pos = self.__pos
		total = fmt.size * length
		vals = []
		for v in fmt.iter_unpack(self.get(total)):
			vals.append(v[0])
		if len(vals) != length:
			raise ReaderBase.ReadError(self, 
				"Read {:,d} out of requested {:,d}".format(len(vals), length))
		self.__pos += total
		self.__cb_update()
		return vals


	def get(self, size):
		pass



class FileReader(ReaderBase):
	'''
	Implementation for reading from files
	'''

	def __init__(self, filename:str, callback=None):
		self.__filename = filename

		self.__f = open(self.__filename, "rb")
		if not self.__f:
			raise FileNotFoundError(self.__filename)

		self.__f.seek(0, os.SEEK_END)
		self.__filesize = self.__f.tell()
		self.__f.seek(0, os.SEEK_SET)

		super().__init__(callback)


	def __del__(self):
		if self.__f:
			self.__f.close()
			self.__f = None

	@property
	def Size(self): 
		return self.__filesize

	@property
	def Name(self): 
		return os.path.basename(self.__Filename)

	@property
	def Filename(self): 
		return self.__filename


	'''
	Private implementation
	'''

	def get(self, size):
		return self.__f.read(size)



class MemoryReader(ReaderBase):
	'''
	Implementation for reading from memory
	'''

	def __init__(self, buffer, callback=None):
		assert buffer != None
		assert len(buffer) > 0
		
		self.__buffer = bytes(buffer) if not isinstance(buffer, bytes) else buffer
		self.__size = len(buffer)

		super().__init__(callback)


	@property
	def Size(self): 
		return self.__size

	@property
	def Name(self): 
		return str(self.__buffer.__class__)


	'''
	Private implementation
	'''

	def get(self, size):
		assert (self.Pos + size) <= self.__size
		return self.__buffer[self.Pos:self.Pos+size]


