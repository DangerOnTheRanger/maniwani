from flask import request
from flask_restful import reqparse

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
        thread = Thread(board=args["board"], views=0, tags=tags)
        # FIXME: use one transaction for all of this, the current state defeats
        # the purpose of having transactions in the first place
        db.session.add(thread)
        db.session.commit()
        NewPost().post(thread_id=thread.id)
        return thread
