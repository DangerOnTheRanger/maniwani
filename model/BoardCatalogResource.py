from flask_restful import Resource

from model.BoardListCatalog import BoardCatalog


class BoardCatalogResource(BoardCatalog, Resource):
    pass
