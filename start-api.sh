#!/bin/sh
sudo service nginx restart
set -e
source venv/bin/activate
nohup uwsgi api.ini &>> /var/log/algotips/api.log &
