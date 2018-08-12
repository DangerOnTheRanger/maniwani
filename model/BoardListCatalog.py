from flask.json import jsonify
from shared import db
from model.Board import Board


class BoardCatalog:
    def get(self, board_id):
        return jsonify(self.retrieve(board_id))

    def retrieve(self, board_id):
        session = db.session
        board = session.query(Board).filter(Board.id == board_id).one()
        thread_list = board.threads
        return self._to_json(thread_list)

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
            t_dict["tags"] = thread.tags
            t_dict["views"] = thread.views
            t_dict["num_replies"] = len(thread.posts) - 1
            t_dict["num_media"] = thread.num_media()
            result.append(t_dict)
        return result
