import pickle

from flask.json import jsonify

import cache
from shared import db
from model.Board import Board


class BoardCatalog:
    def get(self, board_id):
        return jsonify(self.retrieve(board_id))

    def retrieve(self, board_id):
        session = db.session
        cache_connection = cache.Cache()
        board_cache_key = "board-%d-threads" % board_id
        cached_threads = cache_connection.get(board_cache_key)
        if cached_threads:
            deserialized_threads = pickle.loads(bytes(cached_threads))
            return deserialized_threads
        board = session.query(Board).filter(Board.id == board_id).one()
        thread_list = board.threads
        json_friendly = self._to_json(thread_list)
        cache_friendly = str(pickle.dumps(json_friendly))
        cache_connection.set(board_cache_key, cache_friendly)
        return json_friendly

    def _to_json(self, threads):
        result = []
        for thread in threads:
            t_dict = dict()
            op = thread.posts[0]
            t_dict["subject"] = op.subject
            t_dict["last_updated"] = thread.last_updated
            t_dict["body"] = op.body
            t_dict["id"] = thread.id
            t_dict["media"] = op.media
            t_dict["spoiler"] = op.spoiler
            t_dict["tags"] = thread.tags
            t_dict["views"] = thread.views
            t_dict["num_replies"] = len(thread.posts) - 1
            t_dict["num_media"] = thread.num_media()
            t_dict["admin_post"] = thread.admin_is_op()
            result.append(t_dict)
        return result
