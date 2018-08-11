from flask_restful import Resource

from model.NewPost import NewPost


class NewPostResource(NewPost, Resource):
    pass
