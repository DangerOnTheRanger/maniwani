#!/bin/sh

# dev mode - file storage backend, sqlite, no nginx, etc.
if [ $1 = "devmode" ]; then
	# start up internal pubsub server
	python storestub.py &
	uwsgi --ini ./deploy-configs/uwsgi-devmode.ini
# attempting to bootstrap?
elif [ $1 = "bootstrap" ]; then
	python3 bootstrap.py
# version upgrade?
elif [ $1 = "update" ]; then
	python3 update.py
# running normal production mode startup
else
	uwsgi --ini ./deploy-configs/uwsgi.ini
fi
