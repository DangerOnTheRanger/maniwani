import os
import re

from PIL import Image
from flask import current_app, request
from flask_restful import reqparse, inputs

from model.Board import Board
from model.Media import Media, storage
from model.Poster import Poster
from model.Post import Post
from model.Reply import Reply, REPLY_REGEXP
from model.Thread import Thread
from model.Slip import get_slip
from shared import db, gen_poster_id


class NewPost:
    def post(self, thread_id):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("useslip", type=inputs.boolean)
        parser.add_argument("spoiler", type=inputs.boolean)
        args = parser.parse_args()
        ip = request.environ["REMOTE_ADDR"]
        poster = db.session.query(Poster).filter_by(thread=thread_id, ip_address=ip).first()
        body = args["body"]
        should_bump = False
        if poster is None:
            poster_hex = gen_poster_id()
            poster = Poster(hex_string=poster_hex, ip_address=ip, thread=thread_id)
            db.session.add(poster)
            db.session.flush()
            # bump thread if the poster hasn't posted in this thread before
            should_bump = True
        if args.get("useslip") is True:
            slip = get_slip()
            if slip and (slip.is_admin or slip.is_mod):
                poster.slip = slip.id
                db.session.add(poster)
        media_id = None
        if "media" in request.files and request.files["media"].filename:
            uploaded_file = request.files["media"]
            mimetype = uploaded_file.content_type
            board_id = db.session.query(Thread).filter_by(id=thread_id).one().board
            board = db.session.query(Board).filter_by(id=board_id).one()
            expected_mimetypes = board.mimetypes
            if re.match(expected_mimetypes, mimetype) is None:
                db.session.rollback()
                raise InvalidMimeError(mimetype)
            media = storage.save_attachment(uploaded_file)
            media_id = media.id
        post = Post(body=body, subject=args["subject"], thread=thread_id, poster=poster.id, media=media_id,
                    spoiler=args["spoiler"])
        db.session.add(post)
        db.session.flush()
        replying = re.finditer(REPLY_REGEXP, body)
        replies = set()
        if replying:
            for match in replying:
                for raw_reply_id in match.groups():
                    reply_id = int(raw_reply_id)
                    replies.add(reply_id)
            for reply_id in replies:
                reply = Reply(reply_from=post.id, reply_to=reply_id)
                db.session.add(reply)
        if should_bump:
            thread = db.session.query(Thread).filter_by(id=thread_id).one()
            thread.last_updated = post.datetime
            db.session.add(thread)
        db.session.flush()
        db.session.commit()


class InvalidMimeError(Exception):
    pass

