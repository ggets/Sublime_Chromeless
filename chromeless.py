__author__='GG [github.com/ggetsov/]'
__version__='2.0.3'
__license__='Apache 2'
__copyright__='Copyright 2020, Dreamflame Inc.'

import sublime
import sublime_plugin
import os.path
import sys
import time
import random
from screeninfo import get_monitors,Enumerator
from ctypes import windll,wintypes,pointer,c_int,c_void_p
user32=windll.user32
import win32gui
import win32con
import win32api
import threading
import time
name																							=os.path.basename(os.path.abspath(os.path.dirname(__file__)))
name																							=name.replace('.sublime-package','')
settings_file																			='%s.sublime-settings'%name
settings																					=None
winstyle																					=None
initialized																				=False
GetWindowLongPtr=user32.GetWindowLongA
GetWindowLongPtr.argtypes=[c_int,c_int]
GetWindowLongPtr.restype=c_void_p


if(int(sublime.version())<4050):
	def plugin_loaded():
		win=sublime.active_window()
		if(win is None):
			return sublime.set_timeout(lambda:plugin_loaded(),100)
		init()

def init():
	win=(sublime.active_window() or sublime.windows()[0])
	if(win is not None):
		global winstyle
		winstyle=GetWindowLongPtr(win.hwnd(),win32con.GWL_STYLE)
		load_settings()
		if(get_setting('persistent_chromeless_states',False)):
			for win in sublime.windows():
				if(win.settings().get('_chromeless_state',False)):
					win.run_command('chromeless_on')
		time.sleep(0.1)
		global initialized
		initialized=True


# def settings_reset():
	# global persistent
	# setting=get_setting('persistent_chromeless_states',False)
	# if(persistent!=setting):
	# print("a setting has changed.")
		# persistent=setting
def load_settings():
	global settings,settings_file
	settings=sublime.load_settings(settings_file)
	# settings.add_on_change('chromeless',settings_reset)
def save_settings():
	global settings,settings_file
	sublime.save_settings(settings_file)
	# print("save settings: ",settings)
def get_setting(k,d=None):
	global settings
	try:
		settings
	except NameError:
		load_settings()
	return settings.get(k,d)
def set_setting(k,d=None):
	global settings
	# print("set setting: ",settings)
	try:
		settings
	except NameError:
		load_settings()
	settings.set(k,d)
def monitor_dimens(i=0):
	m=get_monitors(Enumerator.Windows)[i]
	# print(("Monitor "+m.name+" Size:"),m.width_workarea,"x",m.height_workarea)
	# print(("Monitor "+m.name+" Size (work area):"),m.width_workarea,"x",m.height_workarea)
	r={
		"wa":{
			"w":(m.width_workarea or -1),
			"h":(m.height_workarea or -1)
		},
		"da":{
			"w":(m.width or -1),
			"h":(m.height or -1)
		}
	}
	return r

def get_fs(win=sublime.active_window()):
	hwnd=win.hwnd()
	state="unknown"
	p=GetWindowLongPtr(hwnd,win32con.GWL_STYLE)
	if(p>0):
		cap=(p&win32con.WS_CAPTION)
		state=(not(cap))
	return state

class ChromelessOn(threading.Thread):
		__instance=None
		hwnd=None
		@staticmethod
		def get_instance():
				if(self.__instance==None):self()
				return self.__instance
		def __init__(self,win,style=None):
				if(win is None):return None
				if(self.__instance!=None):
						raise Exception("Cannot create next instance of this class (singleton).")
				else:
						self.__instance=self
						self.running=True
						self.counter=1
						threading.Thread.__init__(self)
				self.win=win
				self.hwnd=win.hwnd()
				global winstyle
				style=(style or winstyle)
				self.style=(style or GetWindowLongPtr(self.hwnd,win32con.GWL_STYLE))
				if(self.__instance==None):self()
		def run(self):
				# print("SetWindowLong",self.hwnd)
				win32api.SetWindowLong(self.hwnd,win32con.GWL_STYLE,self.style & ~win32con.WS_BORDER & ~win32con.WS_THICKFRAME & ~win32con.WS_DLGFRAME)
				ChromelessResize(self.win).start()
				# md=monitor_dimens()
				global initialized
				if(initialized):
					win32gui.ShowWindow(self.hwnd,win32con.SW_MINIMIZE)
					win32gui.ShowWindow(self.hwnd,win32con.SW_RESTORE)
				# win32gui.MoveWindow(self.hwnd,0,0,md["wa"]["w"],md["wa"]["h"],True)
				# print("MoveWindow",md["wa"]["w"],md["wa"]["h"])
				self.stop()
		def stop(self):
				self.running=False

class ChromelessOff(threading.Thread):
		__instance=None
		hwnd=None
		@staticmethod
		def get_instance():
				if(self.__instance==None):self()
				return self.__instance
		def __init__(self,win,style=None):
				if(win is None):return None
				if(self.__instance!=None):
						raise Exception("Cannot create next instance of this class (singleton).")
				else:
						self.__instance=self
						self.running=True
						self.counter=1
						threading.Thread.__init__(self)
				self.win=win
				self.hwnd=win.hwnd()
				global winstyle
				style=(style or winstyle)
				self.style=(style or GetWindowLongPtr(self.hwnd,win32con.GWL_STYLE))
				if(self.__instance==None):self()
		def run(self):
				win32api.SetWindowLong(self.hwnd,win32con.GWL_STYLE,self.style)
				obj=self.win.settings()
				r=obj.get('_chromeless_restored',None)
				if(r is not None):
					if(r["m"] is not None):
						if(r["m"]):
							win32gui.ShowWindow(self.hwnd,win32con.SW_MAXIMIZE)
						else:
							win32gui.ShowWindow(self.hwnd,win32con.SW_MINIMIZE)
							win32gui.ShowWindow(self.hwnd,win32con.SW_RESTORE)
					win32gui.MoveWindow(self.hwnd,r["x"],r["y"],r["w"],r["h"],True)
				self.stop()
		def stop(self):
				self.running=False

class ChromelessResize(threading.Thread):
		__instance=None
		hwnd=None
		@staticmethod
		def get_instance():
				if(self.__instance==None):self()
				return self.__instance
		def __init__(self,win,style=None):
				if(win is None):return None
				if(self.__instance!=None):
						raise Exception("Cannot create next instance of this class (singleton).")
				else:
						self.__instance=self
						self.running=True
						self.counter=1
						threading.Thread.__init__(self)
				self.hwnd=win.hwnd()
				if(self.__instance==None):self()
		def run(self):
				# print("SetWindowLong",self.hwnd)
				# win32gui.ShowWindow(self.hwnd,win32con.SW_RESTORE)
				md=monitor_dimens()
				win32gui.MoveWindow(self.hwnd,0,0,md["wa"]["w"],md["wa"]["h"],True)
				# print("MoveWindow",md["wa"]["w"],md["wa"]["h"])
				self.stop()
		def stop(self):
				self.running=False

class ChromelessOnCommand(sublime_plugin.WindowCommand):
	def run(self,**arg):
		win=self.window
		if(get_fs(win) is False):
			obj=win.settings()
			obj.set('_chromeless_state',True)
			rect=wintypes.RECT()
			ff=user32.GetWindowRect(win.hwnd(),pointer(rect))
			iz=user32.IsZoomed(win.hwnd())
			if(ff>0):
				obj.set('_chromeless_restored',{"x":rect.left,"y":rect.top,"w":(rect.right-rect.left),"h":(rect.bottom-rect.top),"m":bool(iz)})
			# print("on",win.hwnd())
			ChromelessOn(win).start()

class ChromelessOffCommand(sublime_plugin.WindowCommand):
	def run(self,**arg):
		win=self.window
		if(get_fs(win) is True):
			obj=win.settings()
			obj.set('_chromeless_state',False)
			# print("off",win.hwnd())
			ChromelessOff(win).start()

class ToggleChromelessCommand(sublime_plugin.TextCommand):
	def run(self,edit,**arg):
		win=self.view.window()
		fs_state=get_fs(win)
		# print("toggle Chromeless",fs_state)
		if(
					(fs_state is True)
			 or	(not arg.get('state',True))
		 ):
			win.run_command('chromeless_off')
		else:
			win.run_command('chromeless_on')

class ChromelessViewEventListener(sublime_plugin.EventListener):
	# if(int(sublime.version())>=4050):
	def on_init(self,views):
		init()
	def on_activated_async(self,view):
		win=(view.window() or sublime.active_window())
		if(
					(win is not None)
			and	(get_fs(win))
		):
			ChromelessResize(win).start()



class ChromelessEventListener(sublime_plugin.EventListener):
	def on_query_context(self,view,key,operator,operand,match_all):
		if(
					(key=='chromeless.replace_default_fs_shortcut')
			and	(operator==0)
			and	(operand==True)
		):
			if(not view.window()):
				return
			return get_setting('replace_default_fs_shortcut',False)

	if(int(sublime.version())<4050):
		def on_new_async(self,view):
			# print("on_new_async()")
			win=(view.window() or sublime.active_window())
			if(
						(len(win.views())==0)
				and	(get_setting('go_chromeless_on_new_window',False))
			):
				md=monitor_dimens()
				win.run_command('chromeless_on')
	else:	# On new window (4050+):
		def on_new_window_async(self,win):
			# print("on_new_window_async()")
			if(
						(get_setting('go_chromeless_on_new_window',False))
				 or	(
									(get_setting('persistent_chromeless_states',False))
							and	(win.settings().get('_chromeless_state',False))
						)
				):
				win.run_command('chromeless_on')
