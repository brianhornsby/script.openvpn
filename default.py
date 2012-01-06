#/*
# *
# * OpenVPN: OpenVPN add-on for XBMC.
# *
# * Copyright (C) 2011 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, subprocess, urllib, urllib2

import xbmcsettings as settings
import xbmcutils as utils

# Set some global values.
__xbmcrevision__ = xbmc.getInfoLabel('System.BuildVersion')
__addonid__   = 'script.openvpn'
__author__    = 'Brian Hornsby'
__maxcfgs__   = 3

# Initialise settings.
__settings__ = settings.Settings(__addonid__, sys.argv)

# Get addon information.
__addonname__ = __settings__.get_name()
__version__   = __settings__.get_version()

# Get addon settings values.
__openvpn__ = __settings__.get('openvpn')
__sudo__ = __settings__.get('sudo') == 'true'
__sudopwd__ = __settings__.get('sudopwd')

if ( __name__ == '__main__' ):
	__configs__ = []
	__configfile__ = ''
	i = 1
	while i < (__maxcfgs__ + 1):
		id = __settings__.get('configid%d' % i)
		if len(id) > 0:
			__configs__.append(id)
		i = i + 1

	__configs__.append(__settings__.get_string(1000))
	
	index = xbmcgui.Dialog().select(__settings__.get_string(3000), __configs__)

	i = 1
	while i < (__maxcfgs__ + 1):
		id = __settings__.get('configid%d' % i)
		if len(id) > 0 and id == __configs__[index]:
			__configfile__ = __settings__.get('configfile%d' % i)
			break
		i = i + 1

	if index == len(__configs__) - 1:
		command = 'Notification(%s, %s)' % (__addonname__, 'Kill VPN')
		xbmc.executebuiltin(command)
	else:
		if len(__configfile__) == 0 or not os.path.exists(__configfile__):
			utils.ok(__addonname__, __settings__.get_string(3001), __settings__.get_string(3002))
			xbmc.log('Configuration file does not exist: %s' % __configfile__, xbmc.LOGERROR)
		else:
			prefix = ''
			if __sudo__:
				if len(__sudopwd__) > 0:
					prefix = 'echo \'%s\' | ' % __sudopwd__
				prefix = '%ssudo -S ' % prefix
			cmdline = '%s\'%s\' --cd \'%s\' --config \'%s\'' % (prefix, __openvpn__, os.path.dirname(__configfile__) ,__configfile__)
			if __settings__.get('debug') == 0:
				xbmc.log(cmdline, xbmc.LOGDEBUG)
			proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			for line in proc.stdout:
				if __settings__.get('debug') == 0:
					xbmc.log(line, xbmc.LOGDEBUG)
	
			command = 'Notification(%s, %s)' % (__addonname__, (__settings__.get_string(4000)))
			xbmc.executebuiltin(command)
	
