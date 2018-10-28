FROM python:3.6-alpine AS dev
WORKDIR /maniwani
RUN pip install pipenv
COPY . /maniwani
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

CMD ["flask", "run", "-h", "0.0.0.0"]
