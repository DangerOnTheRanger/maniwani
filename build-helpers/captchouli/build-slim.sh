#!/bin/sh
docker-slim build --include-shell --include-bin /home/captchouli/go/bin/captchouli \
			--include-bin /bin/sleep --include-bin /bin/nc --include-bin /bin/killall \
			"$@" 
