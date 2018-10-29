FROM python:3.6-alpine AS dev
WORKDIR /maniwani
RUN pip install pipenv
COPY . /maniwani
COPY ./build-helpers/docker-entrypoint.sh ./docker-entrypoint.sh
RUN adduser -D maniwani
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add ffmpeg

ENV LIBRARY_PATH=/lib:/usr/lib
RUN pipenv install --system --deploy
RUN touch secret
RUN python makedb.py
EXPOSE 5000
RUN chown -R maniwani:maniwani ./
USER maniwani

ENTRYPOINT ["sh", "./docker-entrypoint.sh", "devmode"]

FROM dev AS prod
USER root
RUN apk add uwsgi-python3 uwsgi-http
USER maniwani
WORKDIR /maniwani
RUN rm test.db
COPY ./build-helpers/config-template.cfg ./maniwani.cfg
ENV MANIWANI_CFG=./maniwani.cfg
# workaround for uwsgi inexplicably not picking up /usr/local/lib even though
# system python has it
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6/site-packages
COPY ./build-helpers/uwsgi.ini ./uwsgi.ini

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
