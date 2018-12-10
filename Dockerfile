FROM python:3.6-alpine AS dev
WORKDIR /maniwani
# backend dependencies
RUN pip install pipenv
RUN adduser -D maniwani
# dependencies for Pillow
RUN apk add build-base jpeg-dev zlib-dev
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
COPY *.py /maniwani/
COPY blueprints /maniwani/blueprints
COPY build-helpers /maniwani/build-helpers
COPY model /maniwani/model
COPY templates /maniwani/templates
COPY ./build-helpers/docker-entrypoint.sh ./docker-entrypoint.sh
# bootstrap dev image
RUN python bootstrap.py
EXPOSE 5000
RUN chown -R maniwani:maniwani ./
USER maniwani

ENTRYPOINT ["sh", "./docker-entrypoint.sh", "devmode"]

FROM dev AS prod
USER root
RUN apk add uwsgi-python3 uwsgi-http
USER maniwani
WORKDIR /maniwani
# clean up dev image bootstrapping
RUN rm test.db
RUN rm -r uploads
COPY ./build-helpers/config-template.cfg ./maniwani.cfg
ENV MANIWANI_CFG=./maniwani.cfg
# workaround for uwsgi inexplicably not picking up /usr/local/lib even though
# system python has it
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6/site-packages
COPY ./build-helpers/uwsgi.ini ./uwsgi.ini

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
