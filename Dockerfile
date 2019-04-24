FROM python:3.6-alpine AS dev
WORKDIR /maniwani
# uwsgi and associated plugins
RUN apk add uwsgi-python3 uwsgi-gevent3 uwsgi-http
# backend dependencies
RUN pip install pipenv
# dependencies for Pillow
RUN apk add build-base jpeg-dev zlib-dev libwebp-dev
# dependencies for psycopg2
RUN apk add libpq postgresql-dev gcc python3-dev musl-dev
RUN apk add ffmpeg
# frontend dependencies
RUN apk add nodejs nodejs-npm
# workaround for some pip issues on alpine
ENV LIBRARY_PATH=/lib:/usr/lib
COPY Pipfile /maniwani
COPY Pipfile.lock /maniwani
RUN pipenv install --system --deploy
# remove backend build-time dependencies
RUN apk del build-base gcc python3-dev musl-dev jpeg-dev zlib-dev
# point MANIWANI_CFG to the devmode config file
ENV MANIWANI_CFG=./deploy-configs/devmode.cfg
# workaround for uwsgi inexplicably not picking up /usr/local/lib even though
# system python has it
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6/site-packages
# build static frontend files
COPY package.json /maniwani
COPY package-lock.json /maniwani
RUN npm install
COPY Gulpfile.js /maniwani
COPY scss /maniwani/scss
RUN npm run gulp
# remove frontend build-time dependencies
RUN apk del nodejs-npm nodejs
RUN rm -rf node_modules
# copy source files over
COPY migrations /maniwani/migrations
COPY *.py /maniwani/
COPY blueprints /maniwani/blueprints
COPY build-helpers /maniwani/build-helpers
COPY deploy-configs /maniwani/deploy-configs
COPY model /maniwani/model
COPY resources /maniwani/resources
COPY templates /maniwani/templates
COPY ./build-helpers/docker-entrypoint.sh ./docker-entrypoint.sh
# bootstrap dev image
RUN python bootstrap.py
EXPOSE 5000

ENTRYPOINT ["sh", "./docker-entrypoint.sh", "devmode"]

FROM dev AS prod
WORKDIR /maniwani
# clean up dev image bootstrapping
RUN rm ./deploy-configs/test.db
RUN rm -r uploads
ENV MANIWANI_CFG=./deploy-configs/maniwani.cfg
# chown and switch users for security purposes
RUN adduser -D maniwani
RUN chown -R maniwani:maniwani ./
USER maniwani

# expose uWSGI
EXPOSE 3031
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
