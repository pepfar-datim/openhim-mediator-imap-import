[![OpenHIM Core](https://img.shields.io/badge/openhim--core-1.5%2B-brightgreen.svg)](http://openhim.readthedocs.org/en/latest/user-guide/versioning.html)

# openhim-mediator-imap-import
OpenHIM Mediator for handling user requests to import indicator mappings in OCL. 

**Repo Owner:** Annah Ngaruro [@angaruro](https://github.com/angaruro)

## installation

- Git clone the repository  into `/usr/share/`
- `sudo vim /usr/share/openhim-mediator-imap-import/config/default.json` to change the config as needed.
- `sudo vim /etc/init/openhim-mediator-imap-import.conf `
```
# OpenHIM imap-import mediator

description "OpenHIM imap-import mediator"

# logs to /var/log/upstart/openhim-mediator-imap-import.log
console log

start on runlevel [2345]
stop on runlevel [!2345]

respawn

setuid openhim
setgid openhim

script
 # export PATH=/home/openhim/.nvm/versions/node/v0.12.7/bin/:$PATH
  export NODE_TLS_REJECT_UNAUTHORIZED=0
  cd /usr/share/openhim-mediator-imap-import
  exec bash -c "source /home/openhim/.nvm/nvm.sh && nvm use 4 && npm start"
end script
```
- cd /usr/share/openhim-mediator-imap-import
- sudo  npm install
- sudo chown -R openhim:openhim /usr/share/openhim-mediator-imap-import/
- Except for the tests folder, copy the rest of files from `/usr/share/openhim-mediator-imap-import/scripts` 
  to the mediator's scripts directory
- The mediator requires a running redis instance and a celery worker, you can find details on 
  on how to install and run redis [here](https://redis.io/download), celery configurations reside in the 
  `celeryconfig.py` file that you copied to the scripts directory above. 
- To start the celery worker, you will need to navigate to the scripts directory and run the command below

  `celery worker -A import_manager -l info -b redis://localhost`
  
  In the command above, `redis://localhost` is the broker url, if redis runs on a different machine or 
  listening on a different port, the broker url needs to be of the form `redis://host_name:port`        
- Start the mediator with `sudo service openhim-mediator-imap-import start`
- restart or stop the mediator with `sudo service openhim-mediator-imap-import restart` or `sudo service openhim-mediator-imap-import stop`
- Logs are available at - `/var/log/upstart/openhim-mediator-imap-import.log`

Now you can setup your HIM channels and the mediator config via the console.

To run celery as a daemon, 
```
apt-get install python-celery
vim /etc/init.d/celeryd and add - https://raw.githubusercontent.com/celery/celery/3.1/extra/generic-init.d/celeryd
chmod a+x /etc/init.d/celeryd
sudo useradd -N -M --system -s /bin/bash celery
sudo groupadd -g 10000 celery
mkdir /var/run/celery/
sudo usermod -a -G celery celery
sudo usermod -a -G celery openhim
chown celery:celery /var/run/celery/
mkdir /var/log/celery/
chown celery:celery /var/log/celery/
vim /etc/default/celeryd
```

```
CELERYD_NODES="worker1"
CELERY_BIN="/usr/local/bin/celery"
CELERY_APP="import_manager"
CELERYD_CHDIR="/opt/openhim-imap-import"
CELERYD_OPTS="-l info -b redis://localhost --concurrency=2"
CELERYD_LOG_FILE="/var/log/celery/%N.log"
CELERYD_PID_FILE="/var/run/celery/%N.pid"
CELERYD_USER="celery"
CELERYD_GROUP="celery"
CELERY_CREATE_DIRS=1
```
Manage the daemon with

`/etc/init.d/celeryd start`

`/etc/init.d/celeryd stop`

`/etc/init.d/celeryd restart`


## License
This software is licensed under the Mozilla Public License Version 2.0.
