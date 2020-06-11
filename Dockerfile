FROM ubuntu:20.04 AS dev
WORKDIR /maniwani
ENV DEBIAN_FRONTEND=noninteractive
# backend dependencies/frontend depndencies/uwsgi, python and associated plugins
RUN apt-get update && apt-get -y --no-install-recommends install python3 python3-pip \
	pipenv uwsgi-core uwsgi-plugin-python3 python3-gevent nodejs npm && \
	rm -rf /var/lib/apt/lists/*
# install static build of ffmpeg
COPY build-helpers/ffmpeg_bootstrap.py /maniwani/build-helpers/
WORKDIR /maniwani/build-helpers
RUN python3 ffmpeg_bootstrap.py
WORKDIR /maniwani
COPY Pipfile /maniwani
COPY Pipfile.lock /maniwani
RUN pipenv install --system --deploy
# point MANIWANI_CFG to the devmode config file
ENV MANIWANI_CFG=./deploy-configs/devmode.cfg
# build static frontend files
COPY package.json /maniwani
COPY package-lock.json /maniwani
COPY Gulpfile.js /maniwani
COPY scss /maniwani/scss
RUN npm install && npm run gulp && rm -rf node_modules
# copy source files over
COPY migrations /maniwani/migrations
COPY *.py /maniwani/
COPY blueprints /maniwani/blueprints
COPY build-helpers/docker-entrypoint.sh /maniwani/build-helpers/
COPY deploy-configs /maniwani/deploy-configs
COPY model /maniwani/model
COPY resources /maniwani/resources
COPY templates /maniwani/templates
COPY ./build-helpers/docker-entrypoint.sh ./docker-entrypoint.sh
# bootstrap dev image
RUN python3 bootstrap.py
EXPOSE 5000

ENTRYPOINT ["sh", "./docker-entrypoint.sh", "devmode"]

FROM dev AS prod
WORKDIR /maniwani
# clean up dev image bootstrapping
RUN rm ./deploy-configs/test.db
RUN rm -r uploads
ENV MANIWANI_CFG=./deploy-configs/maniwani.cfg
# chown and switch users for security purposes
RUN adduser --disabled-login maniwani
RUN chown -R maniwani:maniwani ./
USER maniwani

# expose uWSGI
EXPOSE 3031
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
