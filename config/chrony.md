* `sudo apt install chrony -y`


* `sudo systemctl enable chrony`
* `sudo systemctl start chrony`

### Edit chrony config
* `sudo gedit /etc/chrony/chrony.conf`

* `sudo systemctl restart chronyd.service`

### Debug commands
* `chronyc sourcestats -v`
* `chronyc tracking`


