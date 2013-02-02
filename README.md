OpenVPN Add-on for XBMC
======================

About
-----
This addon allows a user to run a [OpenVPN][1] configuration in XBMC. 

See [wiki][3] for more information on using add-on.

Prerequisites
-----
- Ubuntu 12.04 (Precise Penguin) or Mac OS X (Mountain Lion)
- XBMC 12.0 (Frodo)
- OpenVPN 2.2.0 or greater

Installation Instructions
-----
1. Download the latest zip file for add-on from [Download][4] section.

2. Install add-on into XBMC using 'install from zip file' option. The plugin will be installed in the programs add-ons section.

3. You need to create a file called connections.xml in the addons userdata directory.

- Linux (Ubuntu): ~/.xbmc/userdata/addon_data/script.openvpn
- Mac: ~/Library/Application Support/XBMC/userdata/addon_data/script.openvpn

This file will be used to store your openvpn connections.
The contents of the file should look like below, but change attributes to match your connections.
You need to add one vpn element for each vpn connection.

`<?xml version="1.0" encoding="utf-8" standalone="yes"?>`

`<vpns>`

`<vpn id="VPN1" host="tcp.vpnhost.net" port="80" proto="tcp"/>`

`<vpn id="VPN2" host="udp.vpnhost.net" port="1194" proto="udp" delay="20"/>`

`</vpns>`

- id: Set to the name you want to appear in the select dialog, e.g. 'US VPN' or 'UK VPN'. Mandatory.
- host: The hostname for the openvpn connection. Mandatory.
- port: The port that should be used for openvpn connection. Mandatory.
- proto: tcp or udp. Mandatory.
- delay: Number of seconds to wait before showing notification, after connection. Not Mandatory.

Third-party Libraries
---------------------
- BeautifulSoup

License
-------
This software is released under the [GPL 3.0 license] [2].

[1]: http://openvpn.net
[2]: http://www.gnu.org/licenses/gpl-3.0.html
[3]: https://github.com/brianhornsby/openvpn-xbmc/wiki
[4]: https://github.com/brianhornsby/openvpn-xbmc/downloads