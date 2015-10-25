OpenVPN for Kodi
==========
A script that allows you to control OpenVPN from within Kodi.

Features
-----
- Start and stop OpenVPN from with Kodi.
- Setup multiple VPN connections.
- Display current geo-location.

Screenshots
-----
<img alt="Select OpenVPN configuration dialog" src="https://raw.github.com/brianhornsby/www_brianhornsby_com/master/img/openvpn_select_configuration.png" height="128"/>
<img alt="Geo-location notifications" src="https://raw.github.com/brianhornsby/www_brianhornsby_com/master/img/openvpn_geolocation_notification.png" height="128"/>

Installation
------
Download the latest zip file and install the addon. See [http://kodi.wiki/view/HOW-TO:Install_an_Add-on_from_a_zip_file][1] for more details on installing addons from zip file.

Usage
------
The SimilarTracks script can be accessed from the Programs menu or called using the RunScript builtin function (RunScript(script.openvpn)). The script can be passed the following arguments; e.g. RunScript(script.openvpn, Los Angeles).

**import**: Run the import configuration dialog.

**delete**: Run the delete configuration dialog.

**location**: Display the current geo-location. Uses IPInfoDB API.

**disconnect**: Disconnect the current OpenVPN connection.

**\<openvpn configuration\>**: Run the specified OpenVPN configuration.

Settings
--------
The following settings are available.

**Import OpenVPN Configuration File**: Selecting this setting invokes the import configuration dialog.

**Delete OpenVPN Configuration File**: Selecting the option invokes the delete configuration dialog.

**OpenVPN**: Set this to the OpenVPN binary. Default: /usr/bin/openvp

**Management IP Address**: Use this option to change the IP address used by OpenVPN management interface. Default: 127.0.0.1

**Management Port**: Use this option to change the port used by the OpenVPN management interface. Default: 1337

**Additional Arguments**: Use this option to specify any extra command line arguments to be supplied to OpenVPN.

**Use sudo when running OpenVPN**: Set this option to true if you require OpenVPN to be run using sudo. Default: false

**Password is required**: Set to true if a password is required when using sudo. Default: true

FAQ
---

**Is this plugin available in a Kodi addons repository?** No

**I can't get the OpenVPN plugin to work on Raspberry Pi?** Before asking me for help I suggest reading the following [guide][3].

License
------
OpenVPN for Kodi is licensed under the [GPL 3.0 license][2].

[1]: http://kodi.wiki/view/HOW-TO:Install_an_Add-on_from_a_zip_file
[2]: http://www.gnu.org/licenses/gpl-3.0.html
[3]: http://forums.tvaddons.ag/threads/24769-How-to-set-up-your-VPN-on-raspberry-pi-using-Brain-Hornsby-Openvpn-for-XBMC
