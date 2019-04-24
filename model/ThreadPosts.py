import datetime
import json

import gevent
import gevent.queue
from flask.json import jsonify

import cache
from model.Media import Media
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
        greenlet_pool = []
        result_queue = gevent.queue.PriorityQueue()
        post_queue = gevent.queue.Queue()
        for index, post in enumerate(posts):
            post_queue.put((index, post))
        # TODO: allow worker pool size to be configurable
        for x in range(5):
            worker = gevent.spawn(post_denormalize_worker, thread, post_queue, result_queue)
            greenlet_pool.append(worker)
        gevent.joinall(greenlet_pool)
        sorted_results = list()
        while not result_queue.empty():
            _, post = result_queue.get()
            sorted_results.append(post)
        return sorted_results


def post_denormalize_worker(thread, post_queue, result_queue):
    while not post_queue.empty():
        index, post = post_queue.get()
        p_dict = dict()
        p_dict["body"] = post.body
        p_dict["datetime"] = post.datetime
        p_dict["id"] = post.id
        if index == 0:
            p_dict["tags"] = thread.tags
        session = db.session
        poster = session.query(Poster).filter(Poster.id == post.poster).one()
        p_dict["poster"] = poster.hex_string
        p_dict["subject"] = post.subject
        p_dict["media"] = post.media
        if post.media:
            media = session.query(Media).filter(Media.id == post.media).one()
            p_dict["media_ext"] = media.ext
            p_dict["mimetype"] = media.mimetype
            p_dict["is_animated"] = media.is_animated
        p_dict["spoiler"] = post.spoiler
        p_dict["slip"] = poster.slip
        p_dict["replies"] = []
        replies = session.query(Reply).filter(Reply.reply_to == post.id).all()
        for reply in replies:
            p_dict["replies"].append(reply.reply_from)
        result_queue.put((index, p_dict))
