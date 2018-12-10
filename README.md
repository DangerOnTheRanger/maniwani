Maniwani - an anonymous imageboard for the 21st century
=======================================================

Maniwani is a work-in-progress imageboard implementation using Flask.

Where does the name come from? I could tell you, but by that point
you'd [have been torn to pieces.](https://wikipedia.org/wiki/Katanagatari)


Features
--------

* Per-thread auto-generated IDs, with avatars! (IDs done, avatars planned)
* Markdown support in posts
* Download all media files in a thread (planned)
* Push notification support for new posts/threads with Javascript enabled (planned)
* Graceful UI degradation if Javascript is *not* enabled
* REST API for 3rd-party clients
* Global WebM audio support, muted by default but user-configurable (user settings not yet done)



Installation
------------

Please note that Maniwani is currently pre-alpha software and not ready
to be run in a production environment. Deploy to any Internet-facing servers at
your own risk!

### With Docker - standalone development image

In this directory, run the following to build a development Docker image:

	docker build -t maniwani-dev --target dev .
	
To run your new instance, then type:

	docker run -p 5000:5000 maniwani-dev
	
Point your web browser at http://127.0.0.1:5000 to view your new installation. Note
that running Maniwani in this way will not save any data after the container is closed.
This Docker method is intended to easily see what Maniwani is capable of, as well as
serve as a quick and easily-replicated testbed.

### With Docker - production image and environment

It is also possible through `docker-compose` to spin up an environment very similar
to what one might use in production for Maniwani (uWSGI in addition to Postgres
and Minio), though for the time being this setup is Linux-only and requires `docker-compose`.
In this directory, type:

	docker-compose build
	docker-compose up -d
	docker-compose run maniwani bootstrap
	
The last command will only need to be run once per clean installation of the production
environment. If you ever want to remove all database and storage data, remove the
`compose-data` directory, though you'll likely need root permissions to do so since
some subdirectories are created by other users. At this point, you can use the normal
`docker-compose start` and `docker-compose stop` to start and stop the production
environment, navigating to http://127.0.0.1:5000 as per usual to view Maniwani.

As a final sidenote, this method will run all of your computer's traffic through
a local DNS proxy while active, as otherwise it would not be possible to view
attachments, since the local S3 server would be unreachable via hostname. If
you want to audit the DNS proxy code (which is an open-source 3rd-party container),
feel free to do so at https://github.com/mageddo/dns-proxy-server .

### Without Docker

Note that building without Docker takes a lot less time but is less straightforward and does
not simulate a production environment. If you're interested in working on Maniwani, this is
a good setup option, but otherwise you're probably better off using Docker to test or deploy
a Maniwani instance.

Python 3.4+ in addition to Pipenv and npm are required for installation, but I currently use 3.6
for developing Maniwani; if you're having problems with 3.4, file a bug report, but also
try 3.6 if you can. To install everything save for `ffmpeg` (see the following "Notes on ffmpeg"
section for more), run the following commands in this directory:

	pipenv install
	npm install
	npm run gulp
	
You'll also want to initialize a database with some initial options; so run:

	pipenv run python bootstrap.py
	
Next, to run the development server, type `pipenv run flask run` and point your web browser at
http://127.0.0.1:5000 to view your new Maniwani installation. If you ever want to wipe the database
clean, that's currently handled by removing `test.db` (and the `uploads` directory if you uploaded
anything) and re-running the bootstrap.py script.

#### Notes on ffmpeg

Installing `ffmpeg` can either be done with your system's package manager if you
do not already have it installed, or you can use the `ffmpeg_bootstrap.py` script
to grab a static build of `ffmpeg` like so, assuming you are in the same directory
as the script itself:

	python3 ffmpeg_bootstrap.py
	cp ffmpeg-stub-config.cfg ../maniwani.cfg
	echo MANIWANI_CFG=maniwani.cfg > ../.env


Screenshots
-----------

Front page aggregating all boards:

![Front page](https://i.imgur.com/qCx2Jn9h.png)

Viewing a thread:

![Thread view](https://i.imgur.com/DT0DCWeh.png)

Board index (images are pulled from the most recent OP in each board):

![Board index](https://i.imgur.com/zmgUG8nh.png)

Thread gallery mode:

![Gallery mode](https://i.imgur.com/sG1fzJbh.png)

Board catalog view, also showing off responsive mode:

![Board catalog](https://i.imgur.com/oskEajch.jpg)







