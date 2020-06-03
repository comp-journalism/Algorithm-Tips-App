#!/bin/sh
set -e
source venv/bin/activate
uwsgi --stop api.pid
