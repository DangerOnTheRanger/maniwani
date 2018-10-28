FROM python:3.6-slim AS dev
WORKDIR /app
RUN pip install pipenv
COPY . /app
RUN pipenv install --system --deploy
WORKDIR build-helpers
RUN python ffmpeg_bootstrap.py
WORKDIR ..
RUN python makedb.py
EXPOSE 5000

CMD ["flask", "run"]