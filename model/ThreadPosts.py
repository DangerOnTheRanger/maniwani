import datetime
import json

from flask.json import jsonify

import cache
from model.Media import Media
from model.Post import Post
from model.Poster import Poster
from model.Reply import Reply
from model.Thread import Thread
from shared import db


def thread_posts_cache_key(thread_id):
    return "thread-posts-%d" % thread_id


def _datetime_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.timestamp()


class ThreadPosts:
    def get(self, thread_id):
        session = db.session
        thread = session.query(Thread).filter(Thread.id == thread_id).one()
        thread.views += 1
        session.add(thread)
        session.commit()
        return jsonify(self.retrieve(thread_id))

    def delete(self, thread_id):
        thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
        from model.PostRemoval import PostRemoval
        for post in thread.posts:
            PostRemoval().delete_impl(post.id)
        db.session.delete(thread)
        db.session.commit()

    def retrieve(self, thread_id):
        session = db.session
        thread = session.query(Thread).filter(Thread.id == thread_id).one()
        cache_connection = cache.Cache()
        cache_key = thread_posts_cache_key(thread_id)
        cached_posts = cache_connection.get(cache_key)
        if cached_posts:
            deserialized_posts = json.loads(cached_posts)
            for post in deserialized_posts:
                post["datetime"] = datetime.datetime.utcfromtimestamp(post["datetime"])
            return deserialized_posts
        posts = self._json_friendly(thread.posts, thread)
        cache_connection.set(cache_key, json.dumps(posts, default=_datetime_handler))
        return posts

    def _json_friendly(self, posts, thread):
        poster_subquery = db.session.query(Post.poster).filter(Post.thread == thread.id).subquery()
        unkeyed_posters = db.session.query(Poster).filter(Poster.id.in_(poster_subquery)).all()
        keyed_posters = {p.id: p for p in unkeyed_posters}
        media_subquery = db.session.query(Post.media).filter(Post.thread == thread.id).subquery()
        unkeyed_media = db.session.query(Media).filter(Media.id.in_(media_subquery)).all()
        keyed_media = {m.id: m for m in unkeyed_media}
        reply_subquery = db.session.query(Post.id).filter(Post.thread == thread.id).subquery()
        unkeyed_replies = db.session.query(Reply).filter(Reply.reply_to.in_(reply_subquery)).all()
        keyed_replies = {}
        for reply in unkeyed_replies:
            if keyed_replies.get(reply.reply_to) is None:
                keyed_replies[reply.reply_to] = []
            keyed_replies[reply.reply_to].append(reply.reply_from)
        denormalized_posts = []
        for index, post in enumerate(posts):
            p_dict = dict()
            p_dict["body"] = post.body
            p_dict["datetime"] = post.datetime
            p_dict["id"] = post.id
            if index == 0:
                p_dict["tags"] = thread.tags
            poster = keyed_posters[post.poster]
            p_dict["poster"] = poster.hex_string
            p_dict["subject"] = post.subject
            p_dict["media"] = post.media
            if post.media:
                media = keyed_media[post.media]
                p_dict["media_ext"] = media.ext
                p_dict["mimetype"] = media.mimetype
            p_dict["is_animated"] = media.is_animated
            p_dict["spoiler"] = post.spoiler
            p_dict["slip"] = poster.slip
            replies = keyed_replies.get(post.id)
            p_dict["replies"] = replies or list()
            denormalized_posts.append(p_dict)
        return denormalized_posts
