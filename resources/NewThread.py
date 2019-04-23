from flask_restful import Resource

from model.NewThread import NewThread


class NewThreadResource(NewThread, Resource):
    pass
