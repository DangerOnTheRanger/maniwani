#!/bin/bash

# dev mode - file storage backend, sqlite, no wsgi/nginx, etc.
if [[ $1 = "devmode" ]]; then
	flask run -h 0.0.0.0
# attempting to bootstrap a production environment?
elif [ $1 = "bootstrap" ]; then
	python prod_bootstrap.py
# running normal production mode startup
else
	uwsgi --ini uwsgi.ini
fi
