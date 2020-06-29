#!/bin/sh

# explanation of the included files:
# cacert.pem - certs for requests
# PIL/Pillow.libs - plugins/shared objects needed by Pillow, easier to include them
# this way than to create a crafted HTTP request to get them all
# fractions.py - module needed by Pillow's JPEG plugin
# xml/html5lib - packages needed by bleach
# gevent - gevent is partially included thanks to the default probe but misses some things
# ffmpeg - missed by the probe (a probe request could be crafted to grab it but would need video)
# maniwani/* - folders either missed entirely by the default HTTP probe or only partially included
docker-slim build --include-shell \
			--include-path /usr/local/lib/python3.8/dist-packages/certifi/cacert.pem \
			--include-path /usr/local/lib/python3.8/dist-packages/PIL \
			--include-path /usr/local/lib/python3.8/dist-packages/Pillow.libs \
			--include-path /usr/lib/python3.8/fractions.py \
			--include-path /usr/lib/python3.8/xml \
			--include-path /usr/local/lib/python3.8/dist-packages/bleach/_vendor/html5lib \
			--include-path /usr/local/lib/python3.8/dist-packages/gevent \
			--include-path /maniwani/ffmpeg \
			--include-path /maniwani/templates \
			--include-path /maniwani/static \
			--include-path /maniwani/migrations \
			--include-path /maniwani/uploads \
			"$@"
