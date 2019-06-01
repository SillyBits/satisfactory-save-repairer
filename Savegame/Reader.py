
"""
All code related to reading binary data from files
"""

import os
import struct


TYPE_INT   = struct.Struct('i')
TYPE_FLOAT = struct.Struct('f')
TYPE_LONG  = struct.Struct('q')
TYPE_BYTE  = struct.Struct('B')


class Reader:
	
	def __init__(self, filename, callback=None):
		self.__filename = filename
		self.__callback = callback
		
		self.__f = open(self.__filename, "rb")
		if not self.__f:
			raise FileNotFoundError(self.__filename)
		
		self.__f.seek(0, os.SEEK_END)
		self.__filesize = self.__f.tell()
		self.__f.seek(0, os.SEEK_SET)

		self.__prev_pos = -1
		self.__pos = 0
		
		self.__cb_start()


	def __del__(self):
		if self.__f:
			self.__f.close()
			self.__f = None


	@property
	def Filename(self): return self.__filename
	
	@property
	def Pos(self): return self.__pos	

	@property
	def PrevPos(self): return self.__prev_pos	

	@property
	def Size(self): return self.__filesize


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
		last_pos = self.__prev_pos = self.__pos	
		
		length = _len or self.readInt()
		
		sz = ""
	
		if length < 0:
			# Read unicode string
			
			length = length * -2
	
			chars = self.__f.read(length-2)
	
			zero = self.__f.read(2)
			if zero != b'\x00\x00':  # We assume that the last byte of a string is always \x00
				raise Reader.ReadException(self, "String terminator is '{}' in '{}'".format(zero, chars))
					
			sz = chars.decode('utf-16')
	
		elif length > 0:
			# Read 8bit-ASCII
			
			chars = self.__f.read(length-1)
	
			zero = self.__f.read(1)
			if zero != b'\x00':  # We assume that the last byte of a string is always \x00
				raise Reader.ReadException(self, "String terminator is '{}' in '{}'".format(zero, chars))
			
			sz = chars.decode('ascii')

		self.__pos = self.__f.tell()
		
		return sz

		
	class ReadException(Exception):
		def __init__(self, reader, msg):
			self.reader = reader
			self.message = "[{}@{}] "\
				.format(os.path.basename(reader.Filename), reader.PrevPos) + msg
				
		def __str__(self, *args, **kwargs):
			return self.message + "\n" + Exception.__str__(self, *args, **kwargs) 
		
		
	'''
	Private implementation
	'''
		
	def __cb_start(self):
		if self.__callback: self.__callback.start(self.__filesize)
		
	def __cb_update(self):
		if self.__callback: self.__callback.update(self.__pos)
		
	def __cb_end(self, state):
		if self.__callback: self.__callback.end(state)


	def __read(self, fmt):
		self.__prev_pos = self.__pos
		val = fmt.unpack(self.__f.read(fmt.size))[0]
		self.__pos += fmt.size
		self.__cb_update()
		return val

	def __readN(self, fmt, length):
		self.__prev_pos = self.__pos
		total = fmt.size * length
		#vals = fmt.unpack_from(self.__f.read(total))
		vals = []
		for v in fmt.iter_unpack(self.__f.read(total)):
			vals.append(v[0])
		if len(vals) != length:
			raise Reader.ReadError(self, "Read {} out of requested {}".format(len(vals), length))
		self.__pos += total
		self.__cb_update()
		return vals

