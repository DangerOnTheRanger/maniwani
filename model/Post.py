import datetime as _datetime
from flask import url_for

from bleach import clean
from markdown import markdown
from werkzeug.utils import escape

import cache
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
CONTEXT_CATALOG, CONTEXT_THREAD = range(2)


def post_render_cache_key(context, post_id):
    return "post-render-%d-%d" % (context, post_id)


def render_post_collection(posts, context, extensions):
    cache_connection = cache.Cache()
    for post in posts:
        cache_key = post_render_cache_key(context, post["id"])
        cached_render = cache_connection.get(cache_key)
        if cached_render:
            post["body"] = cached_render
            continue
        rendered_markdown = clean(markdown(post["body"], extensions=extensions),
                             ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
        cache_connection.set(cache_key, rendered_markdown)
        post["body"] = rendered_markdown


def render_for_catalog(posts):
    render_post_collection(posts, CONTEXT_CATALOG, [PostReplyExtension(),
                                                    SpoilerExtension(),
                                                    SpacingExtension()])
                           

def render_for_threads(posts):
    render_post_collection(posts, CONTEXT_THREAD, [ThreadRootExtension(), PostReplyExtension(),
                                                   SpoilerExtension(),
                                                   SpacingExtension()])


class Post(OutputMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4096), nullable=False)
    subject = db.Column(db.String(64), nullable=True)
    thread = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=_datetime.datetime.utcnow)
    poster = db.Column(db.Integer, db.ForeignKey("poster.id"), nullable=False)
    media = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="CASCADE"), nullable=True)
    spoiler = db.Column(db.Boolean, nullable=True)

