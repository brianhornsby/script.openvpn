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
import os, urllib, urllib2
from subprocess import Popen, PIPE, STDOUT

import xbmcsettings as settings
import xbmcutils as utils

# Set some global values.
__xbmcrevision__ = xbmc.getInfoLabel('System.BuildVersion')
__addonid__   = 'script.openvpn'
__author__    = 'Brian Hornsby'

# Initialise settings.
__settings__ = settings.Settings(__addonid__, sys.argv)

# Get addon information.
__addonname__ = __settings__.get_name()
__version__   = __settings__.get_version()

# Get addon settings values.
__openvpn__ = __settings__.get('openvpn')
__configdir__ = __settings__.get('configdir')

if ( __name__ == "__main__" ):
	__configfile__ = xbmcgui.Dialog().browse(1, __settings__.get_string(3000), 'files', '', False, False, __configdir__)
	cmdline = '%s --config %s' % (__openvpn__, __configfile__)
	print cmdline
	#xbmc.executebuiltin('XBMC.Notification(%s)' % __settings__.get_string(4000))
	#p = Popen( cmdline, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT )
	#x = p.stdout.read()
	#import time
	#while p.poll() == None:
	#	time.sleep(2)
	#	x = p.stdout.read()
	#xbmc.executebuiltin('XBMC.Notification(%s)' % __settings__.get_string(4000))

