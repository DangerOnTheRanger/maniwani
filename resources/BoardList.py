from flask_restful import Resource

from model.BoardList import BoardList


class BoardListResource(BoardList, Resource):
    pass
