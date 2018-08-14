from flask.json import jsonify
from model.Media import Media
from model.Poster import Poster
from model.Reply import Reply
from model.Thread import Thread
from shared import db


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
        board_id = thread.board
        db.session.delete(thread)
        db.session.commit()

    def retrieve(self, thread_id):
        session = db.session
        thread = session.query(Thread).filter(Thread.id == thread_id).one()
        return self._to_json(thread.posts, thread)

    def _to_json(self, posts, thread):
        result = []
        for index, post in enumerate(posts):
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
                p_dict["media_ext"] = session.query(Media).filter(Media.id == post.media).one().ext
            else:
                p_dict["media_ext"] = None
            p_dict["spoiler"] = post.spoiler
            p_dict["slip"] = poster.slip
            p_dict["replies"] = []
            replies = session.query(Reply).filter(Reply.reply_to == post.id).all()
            for reply in replies:
                p_dict["replies"].append(reply.reply_from)
            result.append(p_dict)
        return result
