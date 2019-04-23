from flask_restful import Resource

from model.NewPost import NewPost
from restauth import slip_required

class NewPostResource(NewPost, Resource):
    @slip_required
    def post(self, thread_id):
        super().post(thread_id)
