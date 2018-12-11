import datetime as _datetime
from flask import url_for

from markdown import markdown

from model.PostReplyExtension import PostReplyExtension
from model.Spoiler import SpoilerExtension
from model.ThreadRootExtension import ThreadRootExtension
from outputmixin import OutputMixin
from shared import db

def render_for_catalog(posts):
    for post in posts:
        post["body"] = markdown(post["body"],
                                extensions=[PostReplyExtension(),
                                            SpoilerExtension()])


def render_for_threads(posts):
    for post in posts:
        post["body"] = markdown(post["body"],
                                extensions=[ThreadRootExtension(), PostReplyExtension(),
                                            SpoilerExtension()])


class Post(OutputMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4096), nullable=False)
    subject = db.Column(db.String(64), nullable=True)
    thread = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=_datetime.datetime.utcnow)
    poster = db.Column(db.Integer, db.ForeignKey("poster.id"), nullable=False)
    media = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="CASCADE"), nullable=True)
    spoiler = db.Column(db.Boolean, nullable=True)

