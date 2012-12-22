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
_xbmcrevision = xbmc.getInfoLabel('System.BuildVersion')
_addonid   = 'script.openvpn'

# Initialise settings.
_settings = settings.Settings(_addonid, sys.argv)

# Get addon information.
_addonname = _settings.get_name()
_version   = _settings.get_version()


def log_debug(msg):
	if _settings.get('debug') == 0:
		print msg

def proto_enum_to_string(value):
	if value == 0:
		return 'UDP'
	else:
		return 'TCP'

log_debug('========================================')
log_debug('  Addon Id:   %s' % (_addonid))
log_debug('  Addon Name: %s' % (_addonname))
log_debug('  Version:    %s' % (_version))
log_debug('========================================')

# Get addon settings values.
_openvpn		   = _settings.get('openvpn')
_ca				   = _settings.get('ca')
_cert			   = _settings.get('cert')
_key			   = _settings.get('key')
_ta				   = _settings.get('ta')
if _settings.get('useconnections') == 'true':
	_connections   = _settings.get('connections')
else:
	_connections   = None
_defaultport	   = int(_settings.get('defaultport'))
_defaultproto 	   = proto_enum_to_string(_settings.get('defaultproto'))
_defaultcipher	   = _settings.get('defaultcipher')
_defaultstartdelay = int(_settings.get('defaultstartdelay'))
_defaultstopdelay  = int(_settings.get('defaultstopdelay'))
_options           = _settings.get('options')

def read_connections():
	if _connections:
		f = open(_connections, 'r')
		connections = BeautifulSoup(f.read())
		f.close()
	else:
		connections = []
		vpn = {'id':     _settings.get('vpn1id'), 
			   'host':   _settings.get('vpn1host'),
			   'port':   _settings.get('vpn1port'),
			   'proto':  proto_enum_to_string(_settings.get('vpn1proto')),
			   'cipher': _settings.get('vpn1cipher'),
			   'delay':  _settings.get('vpn1delay')}
		connections.append(vpn)
		vpn = {'id':     _settings.get('vpn2id'), 
			   'host':   _settings.get('vpn2host'),
			   'port':   _settings.get('vpn2port'),
			   'proto':  proto_enum_to_string(_settings.get('vpn2proto')),
			   'cipher': _settings.get('vpn2cipher'),
			   'delay':  _settings.get('vpn2delay')}
		connections.append(vpn)
	return connections

def write_configuration(id, host, port, proto, cipher):
	if proto.lower() == 'tcp':
		proto = 'tcp-client'
	
	file = _settings.get_datapath('config.conf')
	f = open(file, 'w')
	f.write('# OpenVPN configuration file: %s\n' % id)
	f.write('remote %s %d %s\n' % (host, port, proto.lower()))
	f.write('pull\n')
	f.write('tls-client\n')
	f.write('ns-cert-type server\n')
	if proto == 'tcp-client':
		f.write('tls-auth \"%s\" 1\n' % _ta)
	f.write('persist-key\n')
	f.write('ca \"%s\"\n' % _ca)
	f.write('nobind\n')
	f.write('persist-tun\n')
	f.write('cert \"%s\"\n' % _cert)
	f.write('comp-lzo\n')
	f.write('dev tun\n')
	f.write('key \"%s\"\n' % _key)
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

	if _connections:
		vpnconnections = read_connections().vpns.findAll('vpn')
	else:
		vpnconnections = read_connections()

	for vpn in vpnconnections:
		vpns.append(vpn['id'])
	vpns.sort()
	
	country = ''
	geolocation = get_geolocation()
	if geolocation and geolocation.lookup:
		country = geolocation.lookup.country_name.string
	vpns.append(_settings.get_string(1000) % country)
	return vpns

def create_configuration(vpns, index):
	configuration = {}
	id = vpns[index]

	if _connections:
		vpnconnections = read_connections().vpns.findAll('vpn')
	else:
		vpnconnections = read_connections()
	
	for vpn in vpnconnections:
		if vpn['id'] == id:
			port = int(vpn.get('port', _defaultport))
			proto = vpn.get('proto', _defaultproto)
			cipher = vpn.get('cipher', _defaultcipher)
			configuration['delay'] = int(vpn.get('delay', _defaultstartdelay))
			configuration['file'] = write_configuration(id, vpn['host'], port, proto, cipher)
			log_debug(vpn)
	return configuration

def sudo_prefix():
	prefix = ''
	if _settings.get('sudo') == 'true':
		sudopwd = _settings.get('sudopwd')
		if _settings.get('sudoprompt') == 'true':
			sudopwd = utils.keyboard(heading=_settings.get_string(3003), hidden=True)
		if sudopwd != None and len(sudopwd) > 0:
			prefix = 'echo \'%s\' | ' % sudopwd
			return '%ssudo -S ' % prefix
	return prefix

def display_location(geolocation):
	if geolocation != None:
		image = _settings.get_path('%s%s%s' % ('resources/images/', geolocation.lookup.country_code.string.lower() , '.png'))
		utils.notification(_addonname, _settings.get_string(4000) % (geolocation.lookup.ip.string, geolocation.lookup.country_name.string), image=image)

def display_notification(id):
	image = _settings.get_path('icon.png')
	utils.notification(_addonname, _settings.get_string(id), image=image)

def start_openvpn(config):
	display_notification(4001)
			
	prefix = sudo_prefix()
	cmdline = '%s\'%s\' --cd \'%s\' --config \'%s\' %s --daemon' % (prefix, _openvpn, os.path.dirname(config['file']), os.path.basename(config['file']), _options)
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(int(config['delay']))
	geolocation = get_geolocation()
	display_location(geolocation)
	
def stop_openvpn():
	display_notification(4002)
			
	prefix = sudo_prefix()
	cmdline = '%skillall -TERM %s' % (prefix, os.path.basename(_openvpn))
	log_debug(cmdline)
	proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			
	time.sleep(_defaultstopdelay)
	geolocation = get_geolocation()
	display_location(geolocation)

if ( __name__ == '__main__' ):
	vpns = get_vpns()
	if _settings.get_argc() == 1:
		index = utils.select(_settings.get_string(3000), vpns)
	else:
		index = int(_settings.get_argv(1)) - 1
	if index != -1:
		if index >= len(vpns) - 1:
			stop_openvpn()
		else:
			config = create_configuration(vpns, index)
			if 'file' in config and len(config['file']) == 0 or not os.path.exists(config['file']):
				utils.ok(_addonname, _settings.get_string(3001), _settings.get_string(3002))
				xbmc.log('Configuration file does not exist: %s' % config['file'], xbmc.LOGERROR)
			else:
				stop_openvpn()
				start_openvpn(config)
	else:
		geolocation = get_geolocation()
		display_location(geolocation)

