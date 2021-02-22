
* enable SSH & VNC
* "Appearance Settings" -> "Defaults" -> "For large screens"

* `sudo apt install gedit -y`

* uncomment VNC resolution settings in /boot/config.txt \
`sudo gedit /boot/config.txt` \
https://www.raspberrypi.org/forums/viewtopic.php?p=1248161&sid=7bcda1b2cacd19f1ee30be0a18681dc5#p1248161 \
or setup it via `sedo raspi-config` if *"Cannot currently show the dekstop"* pops up 

* set static ip \
`sudo gedit /etc/dhcpcd.conf` \
https://www.ionos.com/digitalguide/server/configuration/provide-raspberry-pi-with-a-static-ip-address \
*NOTE: Raspberry Pi connects via **wlan0** not **eth0***

* change hostname