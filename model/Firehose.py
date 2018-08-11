from flask.json import jsonify
from sqlalchemy import desc

from shared import db
from model.BoardListCatalog import BoardCatalog
from model.Post import render_for_catalog
from model.Thread import Thread


class Firehose:
    def get(self):
        return jsonify(self._get_threads())

    def get_impl(self):
        threads = self._get_threads()
        render_for_catalog(threads)
        return threads

    def _get_threads(self):
        raw_threads = db.session.query(Thread).order_by(desc(Thread.last_updated)).limit(10).all()
        threads = BoardCatalog()._to_json(raw_threads)
        return threads
