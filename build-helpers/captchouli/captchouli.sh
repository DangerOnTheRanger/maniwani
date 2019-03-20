#!/bin/sh

if [ $1 = "bootstrap" ]; then
	./go/bin/captchouli $CAPTCHOULI_FLAGS &
	echo "Waiting for captchouli to finish bootstrapping..."
	# currently assume captchouli will always broadcast on 8512
	while ! nc -z localhost 8512; do   
		sleep 1
	done
	echo "Bootstrap complete"
	killall captchouli
else
	./go/bin/captchouli $CAPTCHOULI_FLAGS
fi
