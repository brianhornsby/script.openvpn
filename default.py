#/*
# *
# * OpenVPN add-on for XBMC.
# *
# * Copyright (C) 2012 Brian Hornsby
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

import resources.lib.xbmcsettings as settings
import resources.lib.xbmcutils as utils

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
__openvpn__			  = __settings__.get('openvpn')
__ca__				  = __settings__.get('ca')
__cert__			  = __settings__.get('cert')
__key__				  = __settings__.get('key')
__ta__				  = __settings__.get('ta')
__connections__		  = __settings__.get('connections')
__defaultport__		  = int(__settings__.get('defaultport'))
if __settings__.get('defaultproto') == 0:
	__defaultproto__  = 'UDP'
else:
	__defaultproto__  = 'TCP'
__defaultcipher__	  = __settings__.get('defaultcipher')
__defaultstartdelay__ = int(__settings__.get('defaultstartdelay'))
__defaultstopdelay__  = int(__settings__.get('defaultstopdelay'))
__options__           = __settings__.get('options')

def log_debug(msg):
	if __settings__.get('debug') == 0:
		xbmc.log(msg, xbmc.LOGDEBUG)

def read_connections():
	f = open(__connections__, 'r')
	connections = BeautifulSoup(f.read())
	f.close()
	return connections

def write_configuration(id, host, port, proto, cipher):
	if proto.lower() == 'tcp':
		proto = 'tcp-client'
	
	file = __settings__.get_datapath('config.conf')
	f = open(file, 'w')
	f.write('# OpenVPN configuration file: %s\n' % id)
	f.write('remote %s %d %s\n' % (host, port, proto.lower()))
	f.write('pull\n')
	f.write('tls-client\n')
	f.write('ns-cert-type server\n')
	if proto == 'tcp-client':
		f.write('tls-auth \"%s\" 1\n' % __ta__)
	f.write('persist-key\n')
	f.write('ca \"%s\"\n' % __ca__)
	f.write('nobind\n')
	f.write('persist-tun\n')
	f.write('cert \"%s\"\n' % __cert__)
	f.write('comp-lzo\n')
	f.write('dev tun\n')
	f.write('key \"%s\"\n' % __key__)
	f.write('resolv-retry infinite\n')
	f.write('mssfix 1450\n')
	f.write('mute 20\n')
	f.write('fast-io\n')
	f.write('cipher %s\n' % cipher.lower())
	f.write('tun-mtu 1300\n')
	f.write('redirect-gateway def1\n')
	f.close()
	return file

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

def get_vpns():
	vpns = []
	for vpn in read_connections().vpns.findAll('vpn'):
		vpns.append(vpn['id'])
	vpns.sort()
	
	country = ''
	geolocation = get_geolocation()
	if geolocation and geolocation.lookup:
		country = geolocation.lookup.country_name.string
	vpns.append(__settings__.get_string(1000) % country)
	return vpns

def create_configuration(vpns, index):
	configuration = {}
	id = vpns[index]
	
	for vpn in read_connections().vpns.findAll('vpn'):
		if vpn['id'] == id:
			port = int(vpn.get('port', __defaultport__))
			proto = vpn.get('proto', __defaultproto__)
			cipher = vpn.get('cipher', __defaultcipher__)
			configuration['delay'] = int(vpn.get('delay', __defaultstartdelay__))
			configuration['file'] = write_configuration(id, vpn['host'], port, proto, cipher)
	return configuration

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

def display_location(geolocation):
	if geolocation != None:
		image = __settings__.get_path('%s%s%s' % ('resources/images/', geolocation.lookup.country_code.string.lower() , '.png'))
		utils.notification(__addonname__, __settings__.get_string(4000) % (geolocation.lookup.ip.string, geolocation.lookup.country_name.string), image=image)

def display_notification(id):
	image = __settings__.get_path('icon.png')
	utils.notification(__addonname__, __settings__.get_string(id), image=image)

def start_openvpn(config):
	display_notification(4001)
			
	prefix = sudo_prefix()
	cmdline = '%s\'%s\' --cd \'%s\' --config \'%s\' %s --daemon' % (prefix, __openvpn__, os.path.dirname(config['file']), os.path.basename(config['file']), __options__)
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(int(config['delay']))
	geolocation = get_geolocation()
	display_location(geolocation)
	
def stop_openvpn():
	display_notification(4002)
			
	prefix = sudo_prefix()
	cmdline = '%skillall -TERM %s' % (prefix, os.path.basename(__openvpn__))
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(__defaultstopdelay__)
	geolocation = get_geolocation()
	display_location(geolocation)

if ( __name__ == '__main__' ):
	vpns = get_vpns()
	if __settings__.get_argc() == 1:
		index = utils.select(__settings__.get_string(3000), vpns)
	else:
		index = int(__settings__.get_argv(1)) - 1
	if index != -1:
		if index >= len(vpns) - 1:
			stop_openvpn()
		else:
			config = create_configuration(vpns, index)
			if 'file' in config and len(config['file']) == 0 or not os.path.exists(config['file']):
				utils.ok(__addonname__, __settings__.get_string(3001), __settings__.get_string(3002))
				xbmc.log('Configuration file does not exist: %s' % config['file'], xbmc.LOGERROR)
			else:
				stop_openvpn()
				start_openvpn(config)
	else:
		geolocation = get_geolocation()
		display_location(geolocation)

