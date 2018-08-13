from flask_restful import Resource
from model.PostRemoval import PostRemoval


class PostRemovalResource(PostRemoval, Resource):
    pass
