import datetime
import json

from flask.json import jsonify
from sqlalchemy import desc

import cache
from shared import app, db
from model.Board import Board
from model.BoardListCatalog import BoardCatalog
from model.Post import render_for_catalog
from model.Thread import Thread
from model.ThreadPosts import _datetime_handler


class Firehose:
    def get(self):
        return jsonify(self._get_threads())

    def get_impl(self):
        threads = self._get_threads()
        for thread in threads:
            board_id = thread["board"]
            board = db.session.query(Board).get(board_id)
            thread["board"] = board.name
        render_for_catalog(threads)
        return threads

    def _get_threads(self):
        firehose_cache_key = "firehose-threads"
        cache_connection = cache.Cache()
        cached_threads = cache_connection.get(firehose_cache_key)
        if cached_threads:
            deserialized_threads = json.loads(cached_threads)
            for thread in deserialized_threads:
                thread["last_updated"] = datetime.datetime.utcfromtimestamp(thread["last_updated"])
            return deserialized_threads
        firehose_limit = app.config["FIREHOSE_LENGTH"]
        raw_threads = db.session.query(Thread).order_by(desc(Thread.last_updated)).limit(firehose_limit).all()
        threads = BoardCatalog()._to_json(raw_threads)
        for thread in threads:
            db_thread = db.session.query(Thread).get(thread["id"])
            thread["board"] = db_thread.board
        cache_friendly = json.dumps(threads, default=_datetime_handler)
        cache_connection.set(firehose_cache_key, cache_friendly)
        return threads
