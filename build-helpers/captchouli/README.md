captchouli - Docker support
===========================

This directory contains a Dockerfile for [captchouli](https://github.com/bakape/captchouli), a
booru-backed CAPTCHA provider.

Quickstart
----------

	docker build . -t captchouli
	docker run -p 8512:8512 captchouli

If you have [docker-slim](https://github.com/docker-slim/docker-slim) installed you can also run
the following, assuming you passed `-t captchouli` to `docker build`:

	./build-slim.sh captchouli
	
This will generate a significantly smaller image named `captchouli.slim`, around 300MB compared
to the 1.5GB image created by `docker build`.

There is also a `bootstrap` option that waits for captchouli to build an initial database before
stopping the container, which can prove very useful; building the database for the first time can potentially
take a while:

	docker run -p 8512:8512 captchouli bootstrap
	
Save the container's `/home/captchouli/.captchouli` directory as a bind mount or volume if you want to
take advantage of this feature, otherwise the database will simply be erased when the container stops.

Configuring
-----------

You can set the environment variable `CAPTCHOULI_FLAGS` if you would like to pass custom flags to
captchouli. Keep in mind the `bootstrap` option of the Docker entrypoint always assumes captchouli
will listen on 8512, so if you would like to use the `bootstrap` option, you cannot modify the port
that captchouli runs on.

License
-------

`entrypoint.sh`, `captchouli.sh`, and the Dockerfile contained within this directory are licensed under
the MIT license; captchouli itself is covered by the GNU AGPL 3.0.
