__author__='GG [github.com/ggetsov/]'
__version__='1.5.0'
__license__='Apache 2'
__copyright__='Copyright 2020, Dreamflame Inc.'

import sublime
import sublime_plugin
import os.path
import sys
import time
import random
from screeninfo import get_monitors,Enumerator
name																							=os.path.basename(os.path.abspath(os.path.dirname(__file__)))
name																							=name.replace('.sublime-package','')
settings_file																			='%s.sublime-settings'%name
settings																					=None
persistent																				=False

def plugin_loaded():
	win=sublime.active_window()
	if(win is None):
		return sublime.set_timeout(lambda:plugin_loaded(),100)
	load_settings()
	global persistent
	persistent=get_setting('persistent_chromeless_states',False)
	for win in sublime.windows():
		state=win.settings().get('_chromeless_state',False)
		if(persistent):
			if(state):
				# print("{} (ID {})needs to be switched back to chromeless. State: {}".format(win_uid,win.id(),win_state))
				win.run_command("toggle_chromeless",{"returning":True})
		else:
			# Saved state is lost, but consistency is preserved:
			win.settings().set('_chromeless_state',False)

def settings_reset():
	global persistent
	setting=get_setting('persistent_chromeless_states',False)
	if(persistent!=setting):
		print(setting,"changed.")
		persistent=setting
def load_settings():
	global settings,settings_file
	settings=sublime.load_settings(settings_file)
	settings.add_on_change('chromeless',settings_reset)
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


class ToggleChromelessCommand(sublime_plugin.TextCommand):
	def run(self,edit,**arg):
		wa_width=-1
		wa_height=-1
		for m in get_monitors(Enumerator.Windows):
			# print(("Monitor "+m.name+" Size:"),m.width_workarea,"x",m.height_workarea)
			# print(("Monitor "+m.name+" Size (work area):"),m.width_workarea,"x",m.height_workarea)
			wa_width=m.width_workarea
			wa_height=m.height_workarea
		if((wa_width>-1) and (wa_height>-1)):
			win=self.view.window()
			obj=win.settings()
			isfs=obj.get('_chromeless_state',False)
			if(arg.get('returning',False)):
				isfs=not isfs
			# print("_chromeless_state: {}".format(isfs))
			win.run_command('toggle_full_screen')
			if(not isfs):
				win.run_command('resize_window',{'width':wa_width,'height':(wa_height)})
			obj.set('_chromeless_state',not isfs)


class ChromelessEventListener(sublime_plugin.EventListener):
	def on_query_context(self,view,key,operator,operand,match_all):
		if((key=='chromeless.replace_default_fs_shortcut') and (operator==0) and (operand==True)):
			if(not view.window()):
				return
			return get_setting('replace_default_fs_shortcut',False)

	if(int(sublime.version())<4050):
		def on_new_async(self,view):
			# print("on_new_async()")
			win=view.window() or sublime.active_window()
			obj=win.settings()
			# print("on_new_async()",view,win,obj,obj.get('_chromeless_state'))
			# print("on_new_async()",(len(win.views())==0),obj.get('_chromeless_state',None))
			if(obj.get('_chromeless_state',None) is None):
				obj.set('_chromeless_state',False)
				if((len(win.views())==0) and (get_setting('go_chromeless_on_new_window',False))):
						win.run_command("toggle_chromeless")

	# On new window (4050+):
	else:
		def on_new_window_async(self,win):
			# print("on_new_window_async()")
			obj=win.settings()
			obj.set('_chromeless_state',False)
			if(get_setting('go_chromeless_on_new_window',False)):
				win.run_command("toggle_chromeless")

	# This is probably redundant, because of on_new_async()/on_new_window_async():
		def on_load_project_async(self,win):
			# print("on_load_project_async()")
			global persistent
			persistent=get_setting('persistent_chromeless_states',False)
			obj=win.settings()
			state=obj.get('_chromeless_state',None)
			if(state is None):
					obj.set('_chromeless_state',False)
			if(persistent):
				if(state):
					# print("{} (ID {})needs to be switched back to chromeless. State: {}".format(win_uid,win.id(),win_state))
					win.run_command("toggle_chromeless",{"returning":True})
			else:
				# Saved state is lost, but consistency is preserved:
				obj.set('_chromeless_state',False)
