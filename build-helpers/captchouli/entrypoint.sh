#!/bin/sh

# shim for ensuring we can write to .captchouli in the presence
# of a docker mount
mkdir -p .captchouli/images
chown -R captchouli .captchouli
su -c "./captchouli.sh $1" captchouli
