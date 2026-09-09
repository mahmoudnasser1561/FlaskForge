#!/bin/sh
set -e

flask deploy

exec gunicorn -b 0.0.0.0:5000 -w 2 app:app
