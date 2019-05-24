
"""
All code related to writing binary data to files
"""


from Savegame.Reader \
	import TYPE_INT, TYPE_FLOAT, TYPE_LONG, TYPE_BYTE


class Writer: pass
	#TODO
	
"""
	def __init__(self, filename, callback=None):
		self.__filename = filename
		self.__callback = callback
		
		self.__f = open(self.__filename, "wb")
		if not self.__f:
			raise FileNotFoundError(self.__filename)
		
		self.__prev_pos = -1
		self.__pos = 0


	def __del__(self):
		if self.__f:
			self.__f.close()
			self.__f = None


	@property
	def Pos(self): return self.__pos	

	@property
	def PrevPos(self): return self.__prev_pos	

	#@property
	#def Size(self): return self.__filesize


	'''
	Writers for basic types: int, float, long & byte.
	'''

	def writeInt(self, val):     self.__write(TYPE_INT, val)
	def writeNInt(self, vals):   self.__writeN(TYPE_INT, vals)
	
	def writeFloat(self, val):   self.__write(TYPE_FLOAT, val)
	def writeNFloat(self, vals): self.__writeN(TYPE_FLOAT, vals)
		
	def writeLong(self, val):    self.__write(TYPE_LONG, val)		
	def writeNLong(self, vals):  self.__writeN(TYPE_LONG, vals)   

	def writeByte(self, val):    self.__write(TYPE_BYTE, val)
	def writeNByte(self, vals):  self.__writeN(TYPE_BYTE, vals)

	'''
	Write a string, if prefix=True it's assumed to be prefixed with its length.
	'''
	def writeStr(self, s, prefix=True):
		#TODO: Distinguish between ASCII and UTF-16
		
		if prefix:
			self.writeInt(len(s)+1)
		self.__f.write(s)
		self.__f.write(b'\x00')

		self.__pos = self.__f.ftell()

		
	'''
	Private implementation
	'''
		
	def __cb_start(self):
		if self.__callback: self.__callback("_start", 0xFFFFFFFF)
		
	def __cb_update(self):
		if self.__callback: self.__callback("_update", self.__pos)
		
	def __cb_end(self, state):
		if self.__callback: self.__callback("_end", state)


	def __write(self, fmt, val):
		self.__prev_pos = self.__pos
		self.__f.write(fmt.pack(val))
		self.__pos += fmt.size
		self.__cb_update()

	def __writeN(self, fmt, vals):
		self.__prev_pos = self.__pos
		for v in vals:
			self.__f.write(fmt.pack(v))
		self.__pos += fmt.size * len(vals)
		self.__cb_update()
"""	
