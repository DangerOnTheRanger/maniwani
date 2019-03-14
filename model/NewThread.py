import json

from flask import request
from flask_restful import reqparse
from sqlalchemy import desc

import keystore
from model.Board import Board
from model.NewPost import NewPost
from model.SubmissionError import SubmissionError
from model.Tag import Tag
from model.Thread import Thread
from shared import db


class NewThread:
    def post(self):
        self.post_impl()

    def post_impl(self):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("board", type=int, required=True)
        parser.add_argument("tags", type=str)
        args = parser.parse_args()
        if "media" not in request.files or not request.files["media"].filename:
            raise SubmissionError("A file is required to post a thread!", args["board"])
        tags = []
        if args["tags"]:
            tag_list = args["tags"].replace(" ", "").split(",")
            for tag_name in tag_list:
                tag = db.session.query(Tag).filter(Tag.name == tag_name).one_or_none()
                if tag is None:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tags.append(tag)
        db.session.flush()
        num_threads = db.session.query(Thread).filter(Thread.board == args["board"]).count()
        board = db.session.query(Board).filter(Board.id == args["board"]).one()
        if num_threads >= board.max_threads:
            dead_thread = db.session.query(Thread).filter(Thread.board == args["board"]).order_by(Thread.last_updated.asc()).first()
            db.session.delete(dead_thread)
        thread = Thread(board=args["board"], views=0, tags=tags)
        db.session.add(thread)
        db.session.flush()
        NewPost().post(thread_id=thread.id)
        pubsub_client = keystore.Pubsub()
        pubsub_client.publish("new-thread", json.dumps({"thread": thread.id, "board": thread.board}))
        return thread
