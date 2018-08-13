from model.Post import Post
from shared import db


class PostRemoval:
    def delete(self, post_id):
        post = db.session.query(Post).filter(Post.id == post_id).one()
        thread_id = post.thread
        # TODO: clean up attachments
        db.session.delete(post)
        db.session.commit()
