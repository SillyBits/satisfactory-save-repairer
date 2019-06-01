"""
Random helpers which won't fit into any specific class
"""



def dump_hex(data, width:int=16, show_offset:bool=True, show_ascii:bool=True, indent:int=1):
	s = ""
	d_hex = " "
	d_asc = "   "
	ofs = 0
	col = 0
	w = (width*3)+(width//4)

	for val in data:
		if col % 4 == 0:
			d_hex += " "
			#d_asc += " " # Looks awful :-/
		d_hex += " {:02X}".format(val)
		if show_ascii:
			d_asc += chr(val) if 32 <= val <= 127 else "."

		col += 1
		if col >= width:
			if indent:
				s += "\t"*indent
			if show_offset:
				s += "{:04X}".format(ofs)
			s += d_hex
			if len(d_hex) < w:
				s += " "*(w-len(d_hex))
			if show_ascii:
				s += d_asc
			s += "\n"

			ofs += width
			d_hex = " "
			d_asc = "   "
			col = 0

	if col > 0:
		if indent:
			s += "\t"*indent
		if show_offset:
			s += "{:04X}".format(ofs)
		s += d_hex
		if len(d_hex) < w:
			s += " "*(1+w-len(d_hex))
		if show_ascii:
			s += d_asc
		s += "\n"

	return s



