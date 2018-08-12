from sqlalchemy import and_
from sqlalchemy.orm import relationship

from model.Post import Post
from shared import db

tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('thread_id', db.Integer, db.ForeignKey('thread.id'), primary_key=True)
                )


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.Integer, db.ForeignKey("board.id"), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    posts = relationship("Post", order_by=Post.datetime)
    last_updated = db.Column(db.DateTime)
    tags = relationship("Tag", secondary=tags, lazy='subquery',
                        backref=db.backref('threads', lazy=True))

    def num_media(self):
        return db.session.query(Post).filter(and_(Post.thread == self.id, Post.media != None)).count()
