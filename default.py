#/*
# *
# * OpenVPN for Kodi.
# *
# * Copyright (C) 2015 Brian Hornsby
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

import os
import shutil
import sys
import subprocess
import threading
import time
import urllib2
import xbmc
from BeautifulSoup import BeautifulSoup

import resources.lib.openvpn as vpn
import resources.lib.kodisettings as settings
import resources.lib.kodiutils as utils

# Set some global values.
_addonid = 'script.openvpn'

# Initialise settings.
_settings = settings.KodiSettings(_addonid, sys.argv)

# Get addon information.
_addonname = _settings.get_name()
_version = _settings.get_version()


def log_debug(msg):
    if _settings['debug'] == 'true':
        print 'script.openvpn: DEBUG: %s' % msg


def log_error(msg):
    print 'script.openvpn: ERROR: %s' % msg

log_debug('Addon Id:   [%s]' % (_addonid))
log_debug('Addon Name: [%s]' % (_addonname))
log_debug('Version:    [%s]' % (_version))

# 'enum' of connection states
(disconnected, failed, connecting, disconnecting, connected) = range(5)
_state = disconnected

# Get addon settings values.
_openvpn = _settings['openvpn']
_userdata = _settings.get_datapath()
_ip = _settings['ip']
_port = int(_settings['port'])
_args = _settings['args']
_sudo = (_settings['sudo'] == 'true')
if _sudo:
    _sudopwdrequired = (_settings['sudopwdrequired'] == 'true')
else:
    _sudopwdrequired = False

log_debug('OpenVPN:    [%s]' % _openvpn)
log_debug('Userdata:   [%s]' % _userdata)
log_debug('OpenVPN Management Interface IP: [%s]' % _ip)
log_debug('OpenVPN Management Interface Port: [%d]' % _port)
log_debug('OpenVPN Additional Arguments: [%s]' % _args)
log_debug('Sudo: [%s]' % _sudo)
if _sudo:
    log_debug('Sudo Password Required: [%s]' % _sudopwdrequired)


def get_geolocation():
    try:
        url = 'http://api.ipinfodb.com/v3/ip-city/?key=24e822dc48a930d92b04413d1d551ae86e09943a829f971c1c83b7727a16947f&format=xml'
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        result = f.read()
        f.close()
        return BeautifulSoup(result)
    except:
        return None


def display_location():
    geolocation = get_geolocation()
    if geolocation is not None:
        image = _settings.get_path('%s%s%s' % (
            'resources/images/', geolocation.response.countrycode.string.lower(), '.png'))
        utils.notification(_addonname, _settings.get_string(4000) % (
            geolocation.response.ipaddress.string, geolocation.response.countryname.string.title()), image=image)


def display_notification(text, subtext=False):
    image = _settings.get_path('icon.png')
    if subtext:
        text = text + ': ' + subtext
    utils.notification(_addonname, text, image=image)


def disconnect_openvpn():
    log_debug('Disconnecting OpenVPN')
    global _state
    try:
        _state = disconnecting
        response = vpn.is_running(_ip, _port)
        if response[0]:
            vpn.disconnect(_ip, _port)
            if response[1] is not None:
                display_notification(_settings.get_string(4001) % os.path.splitext(os.path.basename(response[1]))[0])
        _state = disconnected
        log_debug('Disconnect OpenVPN successful')
    except vpn.OpenVPNError as exception:
        utils.ok(_settings.get_string(
            3002), _settings.get_string(3011), exception.string)
        _state = failed


def connect_openvpn(config, restart=False, sudopassword=None):
    log_debug('Connecting OpenVPN configuration: [%s]' % config)
    global _state

    if _sudo and _sudopwdrequired and sudopassword is None:
        sudopassword = utils.keyboard(
            heading=_settings.get_string(3012), hidden=True)
    openvpn = vpn.OpenVPN(_openvpn, _settings.get_datapath(
        config), ip=_ip, port=_port, args=_args, sudo=_sudo, sudopwd=sudopassword, debug=(_settings['debug'] == 'true'))
    try:
        if restart:
            openvpn.disconnect()
            _state = disconnected
        openvpn.connect()
        display_notification(_settings.get_string(4002) % os.path.splitext(os.path.basename(config))[0])
        _state = connected
    except vpn.OpenVPNError as exception:
        if exception.errno == 1:
            _state = connected
            if utils.yesno(_settings.get_string(3002), _settings.get_string(3009), _settings.get_string(3010)):
                log_debug('User has decided to restart OpenVPN')
                connect_openvpn(config, True, sudopassword)
            else:
                log_debug('User has decided not to restart OpenVPN')
        else:
            utils.ok(_settings.get_string(
                3002), _settings.get_string(3011), exception.string)
            _state = failed


def select_ovpn():
    global _state
    ovpnfiles = []
    for path in os.listdir(_userdata):
        if os.path.splitext(path)[1] == '.ovpn':
            log_debug('Found configuration: [%s]' % path)
            ovpnfiles.append(path)

    if len(ovpnfiles) == 0:
        return None
    else:
        ovpnfiles.sort()

        response = vpn.is_running(_ip, _port)
        log_debug('Response from is_running: [%s] [%s] [%s]' % (
            response[0], response[1], response[2]))
        if response[0]:
            _state = connected
            ovpnfiles.append(_settings.get_string(3014))

        configs = []
        for ovpn in ovpnfiles:
            config = os.path.splitext(ovpn)[0]
            if response[1] is not None and response[2] is not None and config == os.path.splitext(os.path.basename(response[1]))[0]:
                config = '%s - %s' % (config, response[2])
            configs.append(config)
        idx = utils.select(_settings.get_string(3013), configs)
        if idx >= 0:
            log_debug('Select: [%s]' % ovpnfiles[idx])
            return ovpnfiles[idx]
        else:
            return ''


def delete_ovpn():
    name = select_ovpn()
    if name is not None and len(name) > 0:
        ovpn = _settings.get_datapath(name)
        log_debug('Delete: [%s]' % ovpn)
        if os.path.exists(ovpn):
            if not utils.yesno(_settings.get_string(3002), _settings.get_string(3006)):
                utils.ok(_settings.get_string(
                    3002), _settings.get_string(3007))
            else:
                log_debug('Deleting: [%s]' % (ovpn))
                os.remove(ovpn)
    elif name is None:
        utils.ok(_settings.get_string(3002), _settings.get_string(3008))


def import_ovpn():
    path = utils.browse_files(_settings.get_string(3000), mask='.ovpn|.conf')
    if path and os.path.exists(path) and os.path.isfile(path):
        log_debug('Import: [%s]' % path)
        name = utils.keyboard(heading=_settings.get_string(3001))
        if name and len(name) > 0:
            ovpn = _settings.get_datapath('%s.ovpn' % name)
            if os.path.exists(ovpn) and not utils.yesno(_settings.get_string(3002), _settings.get_string(3003)):
                    utils.ok(_settings.get_string(
                        3002), _settings.get_string(3004))
            else:
                log_debug('Copying [%s] to [%s]' % (path, ovpn))
                shutil.copyfile(path, ovpn)
        else:
            utils.ok(_settings.get_string(3002), _settings.get_string(3005))


if (__name__ == '__main__'):
    if _settings.get_argc() != 1:
        if _settings.get_argv(1) == 'import':
            import_ovpn()
        elif _settings.get_argv(1) == 'delete':
            delete_ovpn()
        elif _settings.get_argv(1) == 'location':
            display_location()
        elif _settings.get_argv(1) == 'disconnect':
            disconnect_openvpn()
        else:
            found = False
            ovpnpath = None
            for path in os.listdir(_userdata):
                if os.path.splitext(path)[1] == '.ovpn' and os.path.splitext(path)[0] == _settings.get_argv(1):
                    ovpnpath = path
                    found = True
                    break
            if found:
                connect_openvpn(ovpnpath)
            else:
                log_error(
                    'Unknown OpenVPN configuration: [%s]' % _settings.get_argv(1))
    else:
        if not os.path.exists(_userdata):
            log_debug('Creating directory: [%s]' % _userdata)
            os.mkdir(_userdata)

        ovpn = select_ovpn()
        if ovpn is None:
            import_ovpn()
        elif len(ovpn) > 0 and ovpn == _settings.get_string(3014) and _state == connected:
            disconnect_openvpn()
        elif len(ovpn) > 0:
            connect_openvpn(ovpn)
