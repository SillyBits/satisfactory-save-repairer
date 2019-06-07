

import wx 

from pubsub \
	import pub


"""
TODO:
Develop some popup with gauge and texts to be populated

- Way nicer than this status bar thingy and eliminates the "gauge not
  resizing if frame resizes"-problem with some elegance.
- Also more clean code-wise, could use sub-classing to move code into it.
- Could also embed all relevant thread handling there.
- There could be a status text top-left with some counter shown top-right
  (using the max passed in and update to change current value).
- There might also be room for additional info, e.g. the node being worked on.
- Might also allow for cancelling the operation.
- Another neat one: Could try to estimate remaining time and show it.

  <Status...                    ...>   <Count> of <Total>
  <Node info...                                      ...>
  <##########------------------------------------------->
                          <Cancel>



Rough sketch is done, now for the delicate parts:

- Destroying when done
  Had some crashes doing so, but it seems those were caused by not 
  unsubscribing our listeners.
  => "D" works now, yay, another huge step forward :)

- Implement worker thread stuff
  Still not sure on how to implement, esp. with chaining different threads
  (e.g. Load -> Validate -> Report).

"""

class ProgressDlg(wx.Dialog):

	CANCELLABLE = 1
	SHOW_COUNTS = 2
	SHOW_INFO = 4
	
	
	def __init__(self, parent, caption, style=wx.CAPTION|wx.SYSTEM_MENU|wx.CENTER|wx.STAY_ON_TOP,
				flags=CANCELLABLE|SHOW_COUNTS|SHOW_INFO, interval=0, counts_format=None):

		#if flags & ProgressDlg.CANCELLABLE == 0:
		#	style |= wx.CLOSE_BOX

		super().__init__(parent=parent, title=caption, style=style)
		#self.SetDoubleBuffered(True) -> Still flickering like crazy. Same with Freeze/Thaw :-(

		width = 450

		s = (2*width//3, wx.DefaultSize[1]) 
		self.__status = wx.StaticText(self, size=s, label="Status ...")
		
		#TODO: Remove if no flag given?
		self.__counts_format = counts_format or "{:,d} / {:,d}"
		s = (width//3, wx.DefaultSize[1])
		self.__counts = wx.StaticText(self, size=s, 
			label=self.__counts_format.format(0, 0), style=wx.ALIGN_RIGHT)

		if flags & ProgressDlg.SHOW_INFO:		
			s = (width, wx.DefaultSize[1])
			self.__info = wx.StaticText(self, size=s, label="Info goes here...")
		else:
			self.__info = None

		s = (width, 25)
		self.__gauge = wx.Gauge(self, size=s, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)

		if flags & ProgressDlg.CANCELLABLE:		
			self.__cancel = wx.Button(parent=self, label=_("Cancel"), size=wx.DefaultSize) 
			self.Bind(wx.EVT_BUTTON, self.__onCancel, self.__cancel)
		else:
			self.__cancel = None

		sizer = wx.GridBagSizer(5, 5)
		sizer.SetEmptyCellSize((5,5))
		colspan = wx.GBSpan(1, 2)
		sizer.Add(5, 5, (1,3)) #spacer
		row = 1
		sizer.Add(self.__status, (row,1), flag=wx.EXPAND)
		sizer.Add(self.__counts, (row,2), flag=wx.EXPAND)
		row += 1
		if self.__info:
			sizer.Add(self.__info, (row,1), span=colspan, flag=wx.EXPAND)
			row += 1
		row += 1 #spacer
		sizer.Add(self.__gauge, (row,1), span=colspan, flag=wx.EXPAND)
		row += 1
		row += 1 #spacer
		if self.__cancel:
			sizer.Add(self.__cancel, (row,1), span=colspan, flag=wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
			row += 1
		sizer.Add(5, 5, (row,3)) #spacer

		self.SetSizerAndFit(sizer)
		if style & wx.CENTER:
			# Re-center after all UI elements are placed
			self.Center()

		# A simple un-protected bool should do for passing on those cancel requests
		# (only one writer, our dialog, so this should be safe all times)
		self.__cancelled = False

		# Listen to our "commands"
		pub.subscribe(self.__onStart  , "S")
		pub.subscribe(self.__onUpdate , "U")
		pub.subscribe(self.__onEnd    , "E")
		pub.subscribe(self.__onDestroy, "D")
		# ... and prepare for unsubscription
		self.Bind(wx.EVT_CLOSE, self.__onClose)



	"""
	def Start(self):
		self.Bind(self.__event, handler=self.__event)
		self.Show()
		self.start(...)
		#TODO: Start thread

	def Stop(self):
		self.end(...)
		self.Hide()
		#TODO: Signal thread to end
		#self.Unbind(self.__event, handler=self.__event)
	"""

	def SetCountsFormat(self, fmt):
		self.__counts_format = fmt


	'''
	THREAD: Worker
	'''
	def start(self, maxval, status=None, info=None):
		pub.sendMessage("S", maxval=maxval, status=status, info=info)

	def update(self, val, data=None, status=None, info=None):
		#TODO: Get rid of 'data' object
		pub.sendMessage("U", val=val, status=status, info=info)
		return not self.__cancelled

	def end(self, state, status=None, info=None):
		pub.sendMessage("E", state=state, status=status, info=info)

	def destroy(self):
		pub.sendMessage("D")


	'''
	Private implementation
	'''

	def __onCancel(self, event):
		# Only for now, later this will set a signal for thread to stop
		self.__cancelled = True
		self.__info.SetLabel(_("Stopping..."))
		self.EndModal(wx.CANCEL)
		event.Skip()

	def __onClose(self, event):
		pub.unsubscribe(self.__onStart  , "S")
		pub.unsubscribe(self.__onUpdate , "U")
		pub.unsubscribe(self.__onEnd    , "E")
		pub.unsubscribe(self.__onDestroy, "D")
		#event.Skip()		


	'''
	THREAD: Main
	'''
	def __onStart(self, maxval, status, info):
		self.__maxval = maxval
		self.__gauge.SetValue(0)
		self.__gauge.SetRange(self.__maxval)
		self.__update_ui(0, status, info)
		if not self.IsShown():
			self.Show()

	def __onUpdate(self, val, status, info, data=None):
		self.__update_ui(val, status, info)

	def __onEnd(self, state, status, info):
		if self.IsShown():
			self.Hide()

	def __onDestroy(self):
		wx.CallAfter(self.Close)


	def __update_ui(self, val, status, info):
		#self.Freeze()

		if status:
			self.__status.SetLabel(status)

		if self.__info and not self.__cancelled and info:
			self.__info.SetLabel(info)

		if isinstance(val, int):
			self.__gauge.SetValue(val)

		#if self.__counts:
		self.__counts.SetLabel(self.__counts_format.format(val, self.__maxval))

		#self.Thaw()


