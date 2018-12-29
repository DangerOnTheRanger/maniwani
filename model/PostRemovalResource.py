from flask_restful import Resource
from model.PostRemoval import PostRemoval
from restauth import mod_required

class PostRemovalResource(PostRemoval, Resource):
    @mod_required
    def delete(self, post_id):
        super().delete(post_id)
