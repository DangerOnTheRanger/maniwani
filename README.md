Maniwani - an anonymous imageboard for the 21st century
=======================================================

Maniwani is a work-in-progress imageboard implementation using Flask.

Where does the name come from? I could tell you, but by that point
you'd [have been torn to pieces.](https://wikipedia.org/wiki/Katanagatari)


Installation
------------

Please note that Maniwani is currently pre-alpha software and not ready
to be run in a production environment. Deploy to any Internet-facing servers at
your own risk!

Python 3.4+ is required for installation, but I currently use 3.6 for developing
Maniwani; if you're having problems with 3.4, file a bug report, but also try 3.6
if you can.

`pip -r requirements.txt`, ideally inside a `virtualenv`, should take care of
prerequisites. After that, `touch secret` and modify `makedb.py` to your tastes to customize
database initialization before executing `python makedb.py`. Lastly, run
`flask run` from this directory and point your web browser at http://127.0.0.1:5000
to view your new Maniwani installation. If you ever want to wipe the database clean,
that's currently handled by removing `test.db` and re-running the `makedb.py` script.


Features
--------

* Per-thread auto-generated IDs, with avatars! (IDs done, avatars planned)
* Markdown support in posts
* Download all media files in a thread (planned)
* Push notification support for new posts/threads with Javascript enabled (planned)
* Graceful UI degradation if Javascript is *not* enabled
* REST API for 3rd-party clients
* Global WebM audio support, muted by default but user-configurable (user settings not yet done)


Screenshots
-----------

Front page aggregating all boards:

![Front page](https://i.imgur.com/kHhixknh.png)

Viewing a thread:

![Thread view](https://i.imgur.com/hiNt0GTh.png)

Board index (images are pulled from the most recent OP in each board):

![Board index](https://i.imgur.com/dQ8MzKPh.png)

Thread gallery mode:

![Gallery mode](https://i.imgur.com/6QMyd1Mh.png)

Board catalog view, also showing off responsive mode:

![Board catalog](https://i.imgur.com/nb72pxrh.png)







