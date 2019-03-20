captchouli - Docker support
===========================

This directory contains a Dockerfile for [captchouli](https://github.com/bakape/captchouli), a
booru-backed CAPTCHA provider.

Quickstart
----------

	docker build . -t captchouli
	docker run -p 8512:8512 captchouli

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
