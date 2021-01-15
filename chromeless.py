__author__='GG [github.com/ggetsov/]'
__version__='1.3.3'
__license__='Apache 2'
__copyright__='Copyright 2020, Dreamflame Inc.'
# Requires the FullScreenStatus sublime package (via Package Control)
import sublime
import sublime_plugin
import os.path
import sys
import time
import random
from screeninfo import get_monitors,Enumerator
name																						=os.path.basename(os.path.abspath(os.path.dirname(__file__)))
name																						=name.replace('.sublime-package','')
settings_file																		='%s.sublime-settings'%name
_chromeless={}

def plugin_loaded():
	global _chromeless
	load_settings()
	onload_reenter=get_setting('persistent_chromeless_states',False)
	if(onload_reenter):
		window=sublime.active_window()
		if(window is None):
			return sublime.set_timeout(lambda:plugin_loaded(),100)
		_chromeless=get_setting('last_states',{})
		_chromeless_clear={}
		for win in sublime.windows():
			obj=win.settings()
			win_uid=obj.get('_chromeless_uid')
			if(win_uid is not None):
				if(win_uid in _chromeless):
					win_state=_chromeless[win_uid]
				else:
					win_state=False
				if(win_state):
					# print("{} (ID {})needs to be switched back to chromeless. State: {}".format(win_uid,win.id(),win_state))
					#To re-enter if last state was True, we need to fake it to False first (no FS detection)
					_chromeless[win_uid]=False
					win.run_command("toggle_chromeless_internal")
					_chromeless_clear[win_uid]=_chromeless[win_uid]
		set_setting("last_states",_chromeless_clear)
		save_settings()


# for ST2 - manual call to plugin_loaded()
if(sys.version_info<(3,)):
	plugin_loaded()



def load_settings():
	global settings,settings_file
	settings=sublime.load_settings(settings_file)
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


class ToggleChromelessInternalCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		global _chromeless
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
			uid=obj.get('_chromeless_uid')
			gen=str(time.time()).translate(str.maketrans('','','.')).ljust(16,'0')+str(random.randrange(10000,99999))
			if((uid is None) and (gen is not None)):
				obj.set('_chromeless_uid',gen)
			uid=obj.get('_chromeless_uid')
			if(uid is not None):
				isfs=_chromeless.get(uid,False)
				# print("_chromeless: {}".format(_chromeless[uid]))
				win.run_command('toggle_full_screen')
				if(not isfs):
					win.run_command('resize_window',{'width':wa_width,'height':(wa_height)})
				_chromeless[uid]=not isfs


class ToggleChromelessCommand(sublime_plugin.TextCommand):
	def save_states(self):
		global _chromeless
		# win=self.view.window()
		# obj=win.settings()
		# uid=obj.get('_chromeless_uid')
		# print("set last_state to: {}".format(_chromeless[uid]))
		set_setting("last_states",_chromeless)
		save_settings()

	def run(self,edit):
		win=self.view.window()
		win.run_command("toggle_chromeless_internal")
		self.save_states()


class ChromelessQueryContextListener(sublime_plugin.EventListener):
	def on_query_context(self,view,key,operator,operand,match_all):
		if((key=='chromeless.replace_default_fs_shortcut') and (operator==0) and (operand==True)):
			if(not view.window()):
				return
			return get_setting('replace_default_fs_shortcut',False)

