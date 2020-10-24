__author__='GG [github.com/ggetsov/]'
__version__='1.1.2'
__license__='Apache 2'
__copyright__='Copyright 2020, Dreamflame Inc.'
# Requires the FullScreenStatus sublime package (via Package Control)
import sublime
import sublime_plugin
import os.path
import sys
from screeninfo import get_monitors,Enumerator
name																						=os.path.basename(os.path.abspath(os.path.dirname(__file__)))
name																						=name.replace('.sublime-package','')
settings_file																		='%s.sublime-settings'%name

def plugin_loaded():
	global _chromeless
	_chromeless=False
	load_settings()
	onload_reenter=get_setting('auto_reenter_on_plugin_load',False)
	if(onload_reenter):
		window=sublime.active_window()
		if(window is None):
			return sublime.set_timeout(lambda:plugin_loaded(),100)
		window.run_command("chromeless_toggle")

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

class ChromelessToggleCommand(sublime_plugin.TextCommand):
	def save_state(self):
		global _chromeless
		set_setting("last_state",_chromeless)
		save_settings()

	def run(self, edit):
		global _chromeless
		wa_width=-1
		wa_height=-1
		for m in get_monitors(Enumerator.Windows):
			# print(("Monitor "+m.name+" Size:"),m.width_workarea,"x",m.height_workarea)
			# print(("Monitor "+m.name+" Size (work area):"),m.width_workarea,"x",m.height_workarea)
			wa_width=m.width_workarea
			wa_height=m.height_workarea
		if((wa_width>-1) and (wa_height>-1)):
			isfs=sublime.active_window().settings().get('fss_on_full_screen')
			self.view.window().run_command('toggle_full_screen')
			_chromeless=not isfs
			if(not isfs):
				self.view.window().run_command('resize_window', {'width':wa_width,'height':(wa_height)})
			self.save_state()

