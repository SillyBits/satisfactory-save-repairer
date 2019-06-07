"""
Allows for creating complete dumps on properties
"""


from Util \
	import Helper

from Savegame \
	import Property


class Dumper:
	
	def __init__(self, write_func):
		self.__write = write_func
		self.__indent = ""
		self.__reported_properties = []


	def Dump(self, prop):
		self.__indent = ""
		self.__add(prop)


	'''
	Private implementation
	'''

	def __add(self, obj):
		'''
		Add given object to output
		Note that this is called recursively if required!
		'''
		simple = self.__is_simple(obj)
		if simple:
			self.__add_line(simple)
			return

		if isinstance(obj, Property.Accessor):
			if obj not in self.__reported_properties:
				self.__reported_properties.append(obj)
				self.__add_property(obj)
			
		elif isinstance(obj, dict):
			self.__add_dict(obj)
			
		elif isinstance(obj, list):
			self.__add_list(obj)
			
		else:
			# Final resort: Raw display
			self.__add_line("**" + obj.__class__.__qualname__ + ": " + str(obj))


	def __push(self, count=1, char="\t"):
		assert len(char) == 1
		self.__indent += char*count
		
	def __pop(self, count=1):
		assert len(self.__indent) >= count
		self.__indent = self.__indent[:-count]

	def __add_line(self, text, nl=True):
		self.__write(self.__indent)
		self.__write(text)
		if nl:
			self.__write("\n")


	def __add_list(self, l:list):
		simple = self.__is_simple(l)
		if simple:
			self.__add_line(simple)
		else:
			self.__add_line("/ List with {:,d} elements:".format(len(l)))
			self.__push(char="|")
	
			if isinstance(l[0], (Property.Accessor,list,dict)):
				for e in l:
					self.__add(e)
			else:
				if isinstance(l[0], str):
					str_vals = [ "'" + val + "'" for val in l ]
				else:
					str_vals = [ str(val) for val in l ]
				str_vals = ", ".join(str_vals)
				self.__add_line("  " + l[0].__class__.__qualname__ + ":[ " + str_vals + " ]")
	
			self.__pop()
			self.__add_line("\\ end of list")

	def __add_dict(self, d:dict):
		simple = self.__is_simple(d)
		if simple:
			self.__add_line(simple)
		else:
			self.__add_line("/ Dict with {:,d} elements:".format(len(d)))
			self.__push(char="|")
			for key,val in d.items():
				if val != None and isinstance(val, (Property.Accessor,list,dict)):
					self.__add_line("Key '{}':".format(key))
					self.__push()
					self.__add(val)
					self.__pop()
				else:
					# Inline simple values, incl. any None
					if isinstance(val, str):
						s_val = "str:'" + val + "'"
					else:
						if val != None:
							s_val = val.__class__.__qualname__ + ":" + str(val)
						else:
							s_val = "<empty>"
					self.__add_line("Key " + key + " = " + s_val)
			self.__pop()
			self.__add_line("\\ end of dict")

	def __add_property(self, prop):
		self.__add_line("-> " + str(prop))
		#self.__push()
		for name,val in prop.Childs.items():
			if name == "Missing":
				# This needs special handling, for now, might add a specialized class later
				self.__add_line("  .Missing")
				self.__push()
				dump = Helper.dump_hex(val, indent=0)
				for line in dump.splitlines():
					self.__add_line(line)
				self.__pop()
			else:
				simple = self.__is_simple(val)
				if simple:
					self.__add_line("  ." + name + " = " + simple)
				else:
					# Inline as much as possible to keep the report short
					if isinstance(val, Property.Accessor):
						self.__add_line("  ." + name + " =")
						self.__push()
						self.__add(val)
						self.__pop()
					elif isinstance(val, list):
						self.__add_line("  ." + name + " =")
						self.__push()
						self.__add(val)
						self.__pop()
					elif isinstance(val, dict):
						self.__add_line("  ." + name + " =")
						self.__push()
						self.__add(val)
						self.__pop()
					else:
						# Inline simple values, incl. any None
						s_val = str(val)
						if isinstance(val, str):
							s_val = "str:'" + val + "'"
						else:
							if val != None:
								s_val = val.__class__.__qualname__ + ":" + str(val)
							else:
								s_val = "<empty>"
						self.__add_line("  **." + name + " = " + s_val)
		#self.__pop()
		pass


	def __is_simple(self, obj):
		'''
		Analyze given objectchain, returning either the simplified text
		version or 'None' if this can't be inlined due to its complexity.
		'''
		if not obj:
			return "<empty>"

		if isinstance(obj, Property.Accessor):
			return None

		if isinstance(obj, dict):
			if not len(obj):
				return "<empty dict>"

			# Could check for one value only, but nahh
			return None

		if isinstance(obj, list):
			if not len(obj):
				return "<empty list>"

			val = obj[0]
			val_t = type(val)
			for i in range(1, len(obj)):
				if not isinstance(obj[i], val_t):
					# Mixed types can't be inlined
					return None

			chk = self.__is_simple(val)
			if not chk:
				return None # Has complex types stored in it

			t = None
			vals = None
			if isinstance(val, str):
				#vals = "[ " + ", ".join([ "'" + val + "'" for val in obj ]) + " ]"
				vals = "[ '" + "', '".join(obj) + "' ]"
			elif isinstance(val, int):
				# Extra check for those empty .Unknown[N]
				if sum(obj) == 0:
					t = "list({:,d})".format(len(obj))
					vals = "[0,]"
				else:
					vals = "[ " + ", ".join([ "{:,d}".format(val) for val in obj ]) + " ]"				
			if not t:
				t = val.__class__.__qualname__
			if not vals:
				vals = "[ " + ", ".join([ str(val) for val in obj ]) + " ]"
			return t + ":" + vals

		# None of the above so this is "defined" to be simple :D
		if isinstance(obj, str):
			s = "'" + obj + "'"
		elif isinstance(obj, int):
			s = "{:,d}".format(obj)
		else:
			s = str(obj)
		return obj.__class__.__qualname__ + ":" + s





