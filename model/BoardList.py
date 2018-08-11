from model.Board import Board
from shared import db


class BoardList:
    def get(self):
        board_query = db.session.query(Board).all()
        boards = []
        for board in board_query:
            b_dict = {}
            b_dict["id"] = board.id
            b_dict["name"] = board.name
            b_dict["media"] = None
            for thread in board.threads:
                op = thread.posts[0]
                if op.media != None:
                    b_dict["media"] = op.media
                    break
            boards.append(b_dict)
        return boards
