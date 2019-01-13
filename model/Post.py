import datetime as _datetime
from flask import url_for

from bleach import clean
from markdown import markdown
from werkzeug.utils import escape

from model.PostReplyExtension import PostReplyExtension
from model.SpacingExtension import SpacingExtension
from model.Spoiler import SpoilerExtension
from model.ThreadRootExtension import ThreadRootExtension
from outputmixin import OutputMixin
from shared import db


# adapted from https://github.com/Wenzil/mdx_bleach
ALLOWED_TAGS = [
    "ul",
    "ol",
    "li",
    "p",
    "pre",
    "code",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "br",
    "strong",
    "em",
    "a",
    "img",
    "div",
    "span"
]
# TODO: strip inline images, remove need to not strip div
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "class", "data-post-id", "data-toggle", "data-placement", "data-html",
          "data-loaded"],
    "img": ["src", "title", "alt"],
    "div": ["class"],
    "span": ["class"]
}


def render_for_catalog(posts):
    for post in posts:
        post["body"] = clean(markdown(post["body"],
                                      extensions=[PostReplyExtension(),
                                                  SpoilerExtension(),
                                                  SpacingExtension()]),
                             ALLOWED_TAGS, ALLOWED_ATTRIBUTES)


def render_for_threads(posts):
    for post in posts:
        post["body"] = clean(markdown(post["body"],
                                      extensions=[ThreadRootExtension(), PostReplyExtension(),
                                                  SpoilerExtension(),
                                                  SpacingExtension()]),
                             ALLOWED_TAGS, ALLOWED_ATTRIBUTES)


class Post(OutputMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4096), nullable=False)
    subject = db.Column(db.String(64), nullable=True)
    thread = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=_datetime.datetime.utcnow)
    poster = db.Column(db.Integer, db.ForeignKey("poster.id"), nullable=False)
    media = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="CASCADE"), nullable=True)
    spoiler = db.Column(db.Boolean, nullable=True)

