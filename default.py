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
import os, subprocess, time, urllib, urllib2
from BeautifulSoup import BeautifulSoup

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
__timelimit__ = int(__settings__.get('timelimit'))

def log_debug(msg):
	if __settings__.get('debug') == 0:
		xbmc.log(msg, xbmc.LOGDEBUG)

def get_geolocation():
	try:
		url = 'http://ip2country.sourceforge.net/ip2c.php?format=XML'
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		result = f.read()
		f.close()
		return BeautifulSoup(result)
	except:
		return None

def get_configs():
	configs = []
	i = 1
	while i < (__maxcfgs__ + 1):
		id = __settings__.get('configid%d' % i)
		if len(id) > 0:
			configs.append(id)
		i = i + 1
	configs.append(__settings__.get_string(1000))
	return configs

def get_configfile(configs, index):
	config = {}
	i = 1
	while i < (__maxcfgs__ + 1):
		id = __settings__.get('configid%d' % i)
		if len(id) > 0 and id == configs[index]:
			config['file'] = __settings__.get('configfile%d' % i)
			config['id'] = id
			config['delay'] = __settings__.get('configdelay%d' % i)
			break
		i = i + 1
	return config

def sudo_prefix():
	prefix = ''
	if __settings__.get('sudo') == 'true':
		sudopwd = __settings__.get('sudopwd')
		if __settings__.get('sudoprompt') == 'true':
			sudopwd = utils.keyboard(heading=__settings__.get_string(3003), hidden=True)
		if sudopwd != None and len(sudopwd) > 0:
			prefix = 'echo \'%s\' | ' % sudopwd
			return '%ssudo -S ' % prefix
	return prefix

def start_openvpn(config):
	utils.notification(__addonname__, __settings__.get_string(4001))
			
	prefix = sudo_prefix()
	cmdline = '%s\'%s\' --cd \'%s\' --config \'%s\' &' % (prefix, __openvpn__, os.path.dirname(config['file']) ,config['file'])
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(int(config['delay']))
	geolocation = get_geolocation()
	if geolocation != None:
		utils.notification(__addonname__, __settings__.get_string(4000) % (geolocation.lookup.ip.string, geolocation.lookup.country_name.string))

def stop_openvpn():
	utils.notification(__addonname__, __settings__.get_string(4002))
			
	prefix = sudo_prefix()
	cmdline = '%skillall -TERM %s' % (prefix, os.path.basename(__openvpn__))
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(__timelimit__)
	geolocation = get_geolocation()
	if geolocation != None:
		utils.notification(__addonname__, __settings__.get_string(4000) % (geolocation.lookup.ip.string, geolocation.lookup.country_name.string))

if ( __name__ == '__main__' ):
	configs = get_configs()
	index = utils.select(__settings__.get_string(3000), configs)
	if index != -1:
		config = get_configfile(configs, index)
		if index == len(configs) - 1:
			stop_openvpn()
		else:
			if 'file' in config and len(config['file']) == 0 or not os.path.exists(config['file']):
				utils.ok(__addonname__, __settings__.get_string(3001), __settings__.get_string(3002))
				xbmc.log('Configuration file does not exist: %s' % config['file'], xbmc.LOGERROR)
			else:
				stop_openvpn()
				start_openvpn(config)

