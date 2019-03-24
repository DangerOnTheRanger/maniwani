import json
import os
import re
import string

from PIL import Image
from flask import current_app, request
from flask_restful import reqparse, inputs
import requests

import captchouli
import cooldown
import keystore
from model.Board import Board
from model.Media import Media, storage
from model.Poster import Poster
from model.Post import Post
from model.Reply import Reply, REPLY_REGEXP
from model.Thread import Thread
from model.Slip import get_slip
from shared import app, db, gen_poster_id


class NewPost:
    def post(self, thread_id):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("useslip", type=inputs.boolean)
        parser.add_argument("spoiler", type=inputs.boolean)
        # check captcha cooldown
        on_cooldown = cooldown.on_captcha_cooldown()
        # only check of captcha if the client is not on cooldown
        if on_cooldown is False:
            if app.config.get("CAPTCHA_METHOD") == "RECAPTCHA":
                parser.add_argument("recaptcha-token", type=str, required=True)
            elif app.config.get("CAPTCHA_METHOD") == "CAPTCHOULI":
                parser.add_argument("captchouli-id", type=str, required=True)
                for img_num in range(0, 9):
                    # don't bother validating too closely since captchouli takes care of
                    # that for us
                    parser.add_argument("captchouli-%d" % img_num, type=str, default=False)
        args = parser.parse_args()
        ip = None
        # reverse proxy support
        if 'X-Forwarded-For' in request.headers:
            ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
        else:
            ip = request.environ["REMOTE_ADDR"]
        # check captcha if necessary
        board_id = db.session.query(Thread).filter_by(id=thread_id).one().board
        if on_cooldown is False:
            if app.config.get("CAPTCHA_METHOD") == "RECAPTCHA":
                google_response = requests.post("https://www.google.com/recaptcha/api/siteverify",
                                                data={"secret": app.config["RECAPTCHA_SECRET_KEY"],
                                                      "response": args["recaptcha-token"]}).json()
                if google_response["success"] is False:
                    raise CaptchaError("Problem getting reCAPTCHA", board_id)
                if google_response["score"] < app.config["RECAPTCHA_THRESHOLD"]:
                    raise CaptchaError("reCAPTCHA threshold too low", board_id)
            elif app.config.get("CAPTCHA_METHOD") == "CAPTCHOULI":
                captchouli_form = {"captchouli-id": args["captchouli-id"]}
                for img_num in range(0, 9):
                    key = "captchouli-%d" % img_num
                    captchouli_form[key] = args[key]
                if not captchouli.valid_solution(captchouli_form):
                    raise CaptchaError("Incorrect CAPTCHA response", board_id)
        cooldown.refresh_captcha_cooldown()
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
        else:
            # bump thread if this poster isn't the same as the one who posted last in the thread
            last_post = db.session.query(Post).filter_by(thread=thread_id).order_by(Post.id.desc()).first()
            if last_post.poster != poster.id:
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
            board = db.session.query(Board).filter_by(id=board_id).one()
            expected_mimetypes = board.mimetypes
            if re.match(expected_mimetypes, mimetype) is None:
                db.session.rollback()
                raise InvalidMimeError(mimetype, board_id)
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
                raw_reply_id = match.group(2)
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
        pubsub_client = keystore.Pubsub()
        pubsub_client.publish("new-post", json.dumps({"thread": thread_id, "post": post.id}))
        for reply_id in replies:
            pubsub_client.publish("new-reply", json.dumps({"post": post.id, "thread": post.thread, "reply_to": reply_id}))


class InvalidMimeError(Exception):
    pass


class CaptchaError(Exception):
    pass
