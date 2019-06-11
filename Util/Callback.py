
from wx \
	import PostEvent, ID_ANY

from wx.lib \
    import newevent


#Deprecated:
# Only one runner is using this still: Report generation ... remove this soonish
class Callback:
	"""
    Provides some callback object to deal with messaging over threads and
    allows for sending 'Start', 'Update' and 'End' notifications.
    (mainly to inform UI to update, e.g. a progress bar when loading a save)
    """

	def __init__(self, target=None, func=None, interval=1000):
		"""
	    :param target: Window to send events to (using .Bind)
	    :param func: Function to be triggered
	    :param interval: Interval for letting update messages pass
	       (This is to reduce event load if .update is being called way to often)
	    """
		if not Callback.__EvtCls:
			Callback.__EvtCls, Callback.__Evt = newevent.NewEvent()
		if target and func:
			self.bind(target, func)
		self.__interval = interval


	def bind(self, target, func):
		self.__target = target
		Callback.__Evt.Bind(target, ID_ANY, ID_ANY, func)

	def unbind(self):
		Callback.__Evt.Unbind(self.__target, ID_ANY, ID_ANY)
		self.__target = None
	
				
	def start(self, maxval):
		self.__last_seen_val = -(self.__interval + 1)
		self.__trigger(which=Callback.START, maxval=maxval)
		
	def update(self, val, data=None):
		if self.__last_seen_val + self.__interval < val:  # Reduce load a bit
			self.__last_seen_val = val
			self.__trigger(which=Callback.UPDATE, val=val, data=data)
			
	def end(self, state):
		self.__trigger(which=Callback.END, state=state)


	START  = 0
	UPDATE = 1
	END    = 2
	

	'''
	Private implementation
	'''
	
	__EvtCls = None
	__Evt    = None

	def __trigger(self, **kw):
		if self.__target:
			evt = Callback.__EvtCls(**kw)  # Create the event
			PostEvent(self.__target, evt)  # Post the event



