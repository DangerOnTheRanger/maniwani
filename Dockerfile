FROM python:3.6-alpine AS dev
WORKDIR /maniwani
RUN pip install pipenv
COPY . /maniwani
COPY ./build-helpers/docker-entrypoint ./docker-entrypoint.sh
RUN adduser -D maniwani
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add ffmpeg

ENV LIBRARY_PATH=/lib:/usr/lib
RUN pipenv install --system --deploy
RUN python makedb.py
EXPOSE 5000
RUN chown -R maniwani:maniwani ./
USER maniwani

ENTRYPOINT ["./docker-entrypoint.sh", "devmode"]

FROM dev AS prod
RUN apk add uwsgi-python3
WORKDIR /maniwani
COPY ./build-helpers/config-template.cfg ./maniwani.cfg
ENV MANIWANI_CFG=./maniwani.cfg
COPY ./build-helpers/uwsgi.ini ./uwsgi.ini

ENTRYPOINT ["./docker-entrypoint.sh"]
