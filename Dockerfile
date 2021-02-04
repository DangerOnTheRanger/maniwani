FROM ubuntu:20.04 AS dev
WORKDIR /maniwani
ENV DEBIAN_FRONTEND=noninteractive
# backend dependencies/frontend depndencies/uwsgi, python and associated plugins
RUN apt-get update && apt-get -y --no-install-recommends install python3 python3-pip \
	pipenv uwsgi-core uwsgi-plugin-python3 uwsgi-plugin-gevent-python3 python3-gevent nodejs npm
# install static build of ffmpeg and compress with upx
COPY build-helpers/ffmpeg_bootstrap.py /maniwani/build-helpers/
WORKDIR /maniwani/build-helpers
RUN python3 ffmpeg_bootstrap.py && apt-get -y install upx-ucl && \
	chmod +w ../ffmpeg/ffmpeg && \
	upx -9 ../ffmpeg/ffmpeg && apt-get autoremove -y upx-ucl && \
	rm -rf /var/lib/apt/lists/*
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
# build react render sidecar
WORKDIR /maniwani-frontend
COPY frontend/package.json /maniwani-frontend
COPY frontend/package-lock.json /maniwani-frontend
RUN npm install
COPY frontend/src /maniwani-frontend/src
COPY frontend/Gulpfile.js /maniwani-frontend
RUN npm run gulp
RUN cp -r build/* /maniwani-frontend/
COPY frontend/devmode-entrypoint.sh /maniwani-frontend
# TODO: how do we do this when running/deploying without docker?
RUN mkdir -p /maniwani/static/js
RUN cp /maniwani-frontend/build/client-bundle/*.js /maniwani/static/js/
# copy source files over
WORKDIR /maniwani
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
RUN apt-get -y autoremove npm nodejs
ENV MANIWANI_CFG=./deploy-configs/maniwani.cfg
# chown and switch users for security purposes
RUN adduser --disabled-login maniwani
RUN chown -R maniwani:maniwani ./
USER maniwani

# expose uWSGI
EXPOSE 3031
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
