#!/bin/sh
set -e
source venv/bin/activate
nohup uwsgi api.ini &
