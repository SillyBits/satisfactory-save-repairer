import os
import configparser


class Options:
        
    # [window]
    geometry = ""
    

    '''
    Handling
    '' '

    _filename = None
    
    def __init__(self, filename=None):
        if not filename:
            raise Exception("Options: Invalid filename passed")
        self._filename = filename
        self._parser = configparser.ConfigParser(interpolation=None)
        self.load() 

    def load(self):
        self._update()
        self._parser.read(self._filename)
        self._populate()

    def save(self):
        with open(self._filename, "wt") as file:
            self._update()
            self._parser.write(file)


    def _update(self):
        self._parser["window"] = {
            "geometry": self.geometry
            }

        #self._parser["options"] = {
        #    "cabinet": self.cabinet,
        #    "extract_location": self.extract_location,
        #    "last_selection": self.last_selection,
        #    "current_marker": self.current_marker 
        #    }

    def _populate(self):
        window = self._parser["window"]
        self.geometry = window["geometry"]
        
        #options = self._parser["options"]
        #self.cabinet = options["cabinet"] 
        #self.extract_location = options["extract_location"]
        #self.last_selection = options["last_selection"]
        #self.current_marker = options["current_marker"]

	'''
