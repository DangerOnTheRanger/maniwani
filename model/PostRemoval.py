from sqlalchemy import or_

from model.Media import Media
from model.Post import Post
from model.Reply import Reply
from shared import db


class PostRemoval:
    def delete(self, post_id):
        self.delete_impl(post_id)
        db.session.commit()
    def delete_impl(self, post_id):
        post = db.session.query(Post).filter(Post.id == post_id).one()
        for reply in db.session.query(Reply).filter(or_(Reply.reply_from == post_id, Reply.reply_to == post_id)):
            db.session.delete(reply)
        media = db.session.query(Media).filter(Media.id == post.media).first()
        if media:
            media.delete_attachment()
            db.session.delete(media)
        db.session.delete(post)
