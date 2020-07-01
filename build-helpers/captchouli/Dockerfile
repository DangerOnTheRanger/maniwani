FROM debian:buster-slim
# install prereqs, utils for bootstrapping watcher
RUN apt-get update && apt-get install -y golang libopencv-dev git \
	netcat-openbsd psmisc && \
	rm -rf /var/lib/apt/lists/*
# make a new user so we don't run as root
RUN useradd -r captchouli
WORKDIR /home/captchouli
RUN chown -R captchouli /home/captchouli
# preemptively make the supporting directory so docker won't
# attempt to make a new directory owned by root (aids when
# attempting to persist .captchouli)
RUN mkdir -p .captchouli/images
RUN chown -R captchouli .captchouli
# install captchouli
USER captchouli
RUN go get github.com/bakape/captchouli/cmd/captchouli
# setup entrypoint and port
COPY entrypoint.sh .
COPY captchouli.sh .
EXPOSE 8512
# entrypoint switches back to the captchouli user but needs to
# start with root privileges
USER root
ENTRYPOINT ["sh", "./entrypoint.sh"]
