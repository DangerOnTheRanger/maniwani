#!/bin/sh

# dev mode - file storage backend, sqlite, no wsgi/nginx, etc.
if [ $1 = "devmode" ]; then
	flask run -h 0.0.0.0
# attempting to bootstrap a production environment?
elif [ $1 = "bootstrap" ]; then
	python3 bootstrap.py
# database migration?
elif [ $1 = "migrate" ]; then
	flask db upgrade
# running normal production mode startup
else
	uwsgi --ini ./deploy-configs/uwsgi.ini
fi
