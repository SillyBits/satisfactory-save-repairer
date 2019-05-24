
'''
Provides sort of callback object to deal with messaging over threads and
allows for sending 'Start', 'Update' and 'End' notifications.
(mainly to inform UI to update something, e.g. progress bar when loading a save)
'''

import wx
import wx.lib.newevent


'''
def NewEvent():
    """
    Generates a new `(event, binder)` tuple.

    ::

        MooEvent, EVT_MOO = NewEvent()

    """

    evttype = wx.NewEventType()

    class _Event(wx.PyEvent):
        def __init__(self, **kw):
            wx.PyEvent.__init__(self)
            self.SetEventType(evttype)
            self._getAttrDict().update(kw)

    return _Event, wx.PyEventBinder(evttype)
'''


class Callback:

	def __init__(self, target=None, func=None, interval=1000):
		if not Callback.__EvtCls:
			Callback.__EvtCls,Callback.__Evt = wx.lib.newevent.NewEvent()
		if target and func:
			self.bind(target, func)
		self.__interval = interval

	def __del__(self):
		if self.__target:
			self.unbind()


	def bind(self, target, func):
		self.__target = target
		Callback.__Evt.Bind(target, wx.ID_ANY, wx.ID_ANY, func)

	def unbind(self):
		Callback.__Evt.Unbind(self.__target, wx.ID_ANY, wx.ID_ANY)
		self.__target = None
	
				
	def start (self, maxval): 
		self.__last_seen_val = -(self.__interval+1) #-1001
		self.__trigger(which=Callback.START, maxval=maxval)
		
	def update(self, val, data=None):
		if self.__last_seen_val + self.__interval < val: # Reduce load a bit
			self.__last_seen_val = val
			self.__trigger(which=Callback.UPDATE, val=val, data=data)
			
	def end   (self, state):  
		self.__trigger(which=Callback.END, state=state)


	START  = 0
	UPDATE = 1
	END    = 2
	

	'''
	Private
	'''
	
	__EvtCls = None
	__Evt    = None

	def __trigger(self, **kw):
		if self.__target:
			evt = Callback.__EvtCls(**kw)      # Create the event
			wx.PostEvent(self.__target, evt) # Post the event



