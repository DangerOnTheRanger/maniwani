"""
This module is responsible for creating posts out of post data.
"""

import json
import re
from typing import Tuple, Set, List

from flask import request
from flask_restful import reqparse, inputs
import requests

from cache import Cache
import captchouli
from cooldown import on_captcha_cooldown, refresh_captcha_cooldown
import keystore
from model.Board import Board
from model.Media import storage
from model.Poster import Poster
from model.Post import Post
from model.Reply import Reply, REPLY_REGEXP
from model.Thread import Thread
from model.ThreadPosts import thread_posts_cache_key
from model.Slip import get_slip
from shared import app, db, gen_poster_id


class InvalidMimeError(Exception):
    "Error to be thrown when the mimetype is invalid for an attachment."


class CaptchaError(Exception):
    "Error to be thrown when captcha is invalid."


GOOGLE_RECAPTCHA_PATH = "https://www.google.com/recaptcha/api/siteverify"


def get_ip_address() -> str:
    "Returns the current IP address of the user."

    if "X-Forwarded-For" in request.headers:
        return request.headers.getlist("X-Forwarded-For")[0].split()[-1]
    return request.environ["REMOTE_ADDR"]


def validate_captcha(board_id: int, args: dict) -> None:
    "Validates the authenticity of the current user with a captcha."

    if on_captcha_cooldown():
        return

    captcha_method = app.config.get("CAPTCHA_METHOD")
    if captcha_method == "RECAPTCHA":
        google_response = requests.post(
            GOOGLE_RECAPTCHA_PATH,
            data={
                "secret": app.config.get("RECAPTCHA_SECRET_KEY"),
                "response": args["recaptcha-token"]
            }
        ).json()

        if not google_response["success"]:
            raise CaptchaError("reCAPTCHA response failed", board_id)

        if google_response["score"] < app.config["RECAPTCHA_THRESHOLD"]:
            raise CaptchaError("reCAPTCHA score below threshold", board_id)
    elif captcha_method == "CAPTCHOULI":
        captchouli_args = {
            k: v for k, v in args.items()
            if k.startswith("captchouli")
        }
        if not captchouli.valid_solution(captchouli_args):
            raise CaptchaError("Incorrect CAPTCHA solution", board_id)
    else:
        # TODO is this supposed to be nothing at all? raise exception?
        pass

    refresh_captcha_cooldown()


def get_or_update_poster(thread_id: int, ip: str) -> Tuple[Poster, bool]:
    """
    Returns the current poster (creating one if it doesn't exist) and whether
    this poster is the last poster in the current thread.
    """

    poster = (
        db.session.query(Poster)
        .filter_by(thread=thread_id, ip_address=ip)
        .first()
    )

    if poster is None:
        poster_hex = gen_poster_id()
        poster = Poster(hex_string=poster_hex, ip_address=ip, thread=thread_id)
        db.session.add(poster)
        db.session.flush()

        return (poster, False)

    last_post = (
        db.session.query(Post)
        .filter_by(thread=thread_id)
        .order_by(Post.id.desc())
        .first()
    )

    if last_post is None or last_post.poster != poster.id:
        return (poster, False)
    return (poster, True)


def update_poster_slip(poster: Poster, args: dict) -> None:
    "Updates the current poster with a slip if necessary."

    if args.get("useslip") is True:
        slip = get_slip()
        if slip and (slip.is_admin or slip.is_mod):
            poster.slip = slip.id
            db.session.add(poster)


def get_media_id(board_id: int) -> int:
    "Get the media ID for this request, or None if no media was uploaded."

    f = request.files.get("media")
    if not f or not f.filename:
        return None

    # Check the mimetype
    mimetype = f.content_type
    allowed_mimes = (
        db.session.query(Board)
        .filter_by(id=board_id)
        .one()
    ).mimetypes

    if re.match(allowed_mimes, mimetype) is None:
        db.session.rollback()
        raise InvalidMimeError(mimetype, board_id)

    return storage.save_attachment(f).id


def get_replies(post_id: int, body: str) -> Set[Reply]:
    "Returns a list of Reply objects for this post (unique IDs)."

    ids = set()
    iterator = re.finditer(REPLY_REGEXP, body)

    if not iterator:
        return []

    for match in iterator:
        # match.group(2) == the post ID
        ids.add(int(match.group(2)))
    return list(map(lambda id: Reply(reply_from=post_id, reply_to=id), ids))

def publish_thread(thread: Thread, post: Post, replies: List[Reply]) -> None:
    """
    Publish a new post to the pub-sub system, also invalidating the cache in
    the process.
    """

    client = keystore.Pubsub()
    client.publish("new-post", json.dumps({
        "thread": thread.id,
        "post": post.id,
    }))
    for reply in replies:
        client.publish("new-reply", json.dumps({
            "thread": post.thread,
            "post": post.id,
            "reply_to": reply.reply_to,
        }))


def invalidate_posts(thread: Thread, replies: List[Reply]):
    "Invalidates the respective cache pages after a post has been created."

    cache = Cache()
    cache.invalidate(thread_posts_cache_key(thread.id))
    slip_bitmasks = 0, 1, 3, 7
    theme_list = app.config.get("THEME_LIST") or ("stock", "harajuku", "wildride")
    for bitmask in slip_bitmasks:
        for theme in theme_list:
            render_cache_key = "thread-%d-%d-%s-render" % (thread.id, bitmask, theme)
            cache.invalidate(render_cache_key)

    reply_ids = list(map(lambda r: r.reply_to, replies))
    thread_ids = (
        db.session.query(Post.thread)
        .filter(Post.id.in_(reply_ids))
        .all()
    )
    for thread_id in thread_ids:
        cache.invalidate(thread_posts_cache_key(thread_id))


def create_post(thread: Thread, args: dict) -> Post:
    "Creates a new post from the given data."

    board_id = thread.board
    validate_captcha(board_id, args)

    ip = get_ip_address()
    poster, flooding = get_or_update_poster(thread.id, ip)

    update_poster_slip(poster, args)

    media_id = get_media_id(board_id)

    post = Post(
        body=args["body"],
        subject=args["subject"],
        thread=thread.id,
        poster=poster.id,
        media=media_id,
        spoiler=args["spoiler"],
    )
    db.session.add(post)
    db.session.flush()

    replies = get_replies(post.id, post.body)
    for reply in replies:
        db.session.add(reply)

    if not flooding:
        # bump the thread if the last poster isn't the same
        thread.last_updated = post.datetime
        db.session.add(thread)

    db.session.flush()
    db.session.commit()

    publish_thread(thread, post, replies)
    invalidate_posts(thread, replies)
    # import here to prevent a circular import
    # TODO: fix circular import with NewPost
    from thread import invalidate_board_cache
    invalidate_board_cache(board_id)

    return post
