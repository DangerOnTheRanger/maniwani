import time

from flask import Blueprint, render_template, redirect, url_for, flash, request, copy_current_request_context, session, make_response
from werkzeug.http import parse_etags

import cache
import captchouli
import cooldown
from model.Media import upload_size, storage
from model.Board import Board
from model.NewPost import NewPost
from model.NewThread import NewThread
from model.Post import Post, render_for_threads
from model.PostRemoval import PostRemoval
from model.PostReplyPattern import url_for_post
from model.Poster import Poster
from model.Slip import get_slip, get_slip_bitmask
from model.SubmissionError import SubmissionError
from model.Thread import Thread
from model.ThreadPosts import ThreadPosts
from post import InvalidMimeError, CaptchaError
import renderer
from shared import db, app
from thread import invalidate_board_cache


threads_blueprint = Blueprint('threads', __name__, template_folder='template')
threads_blueprint.add_app_template_global(url_for_post)


@app.context_processor
def get_captchouli():
    def _get_captchouli():
        return captchouli.request_captcha()
    return dict(get_captchouli=_get_captchouli)


@threads_blueprint.route("/new/<int:board_id>")
def new(board_id):
    extra_data = {}
    if app.config.get("CAPTCHA_METHOD") == "CAPTCHOULI":
        extra_data = renderer.captchouli_to_json(captchouli.request_captcha())
    return renderer.render_new_thread_form(board_id, extra_data)


@threads_blueprint.route("/new", methods=["POST"])
def submit():
    try:
        thread = NewThread().post()
        return redirect(url_for("threads.view", thread_id=thread.id))
    except SubmissionError as e:
        flash(str(e.args[0]))
        return redirect(url_for("threads.new", board_id=e.args[1]))
    except InvalidMimeError as e:
        flash("Can't post attachment with MIME type \"%s\" on this board!" % e.args[0])
        return redirect(url_for("threads.new", board_id=e.args[1]))
    except CaptchaError as e:
        flash("CAPTCHA error: %s" % e.args[0])
        return redirect(url_for("threads.new", board_id=e.args[1]))


@threads_blueprint.route("/<int:thread_id>")
def view(thread_id):
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    thread.views += 1
    db.session.add(thread)
    db.session.commit()
    current_theme = session.get("theme") or app.config.get("DEFAULT_THEME") or "stock"
    response_cache_key = "thread-%d-%d-%s-render" % (thread_id, get_slip_bitmask(), current_theme)
    cache_connection = cache.Cache()
    view_key = "thread-%d-views" % thread_id
    cached_views = cache_connection.get(view_key)
    fetch_from_cache = True
    if cached_views is None:
        fetch_from_cache = False
    else:
        cached_views = int(cached_views)
    if fetch_from_cache and (thread.views / cached_views) >= app.config.get("CACHE_VIEW_RATIO", 0):
        fetch_from_cache = False
    etag_value = "%s-%f" % (response_cache_key, time.time())
    etag_cache_key = "%s-etag" % response_cache_key
    if fetch_from_cache:
        etag_header = request.headers.get("If-None-Match")
        current_etag = cache_connection.get(etag_cache_key)
        if etag_header:
            parsed_etag = parse_etags(etag_header)
            if parsed_etag.contains_weak(current_etag):
                 return make_response("", 304)
        cache_response_body = cache_connection.get(response_cache_key)
        if cache_response_body is not None:
            cached_response = make_response(cache_response_body)
            cached_response.set_etag(current_etag, weak=True)
            cached_response.headers["Cache-Control"] = "public,must-revalidate"
            return cached_response
    posts = ThreadPosts().retrieve(thread_id)
    render_for_threads(posts)
    board = db.session.query(Board).get(thread.board)
    num_posters = db.session.query(Poster).filter(Poster.thread == thread_id).count()
    num_media = thread.num_media()
    reply_urls = _get_reply_urls(posts)
    thread_data = {}
    for post in posts:
        post["datetime"] = post["datetime"].strftime("%a, %d %b %Y %H:%M:%S UTC")
        if post["media"]:
            post["media_url"] = storage.get_media_url(post["media"], post["media_ext"])
            post["thumb_url"] = storage.get_thumb_url(post["media"])
    thread_data["posts"] = posts
    extra_data = {}
    if app.config.get("CAPTCHA_METHOD") == "CAPTCHOULI":
        extra_data = renderer.captchouli_to_json(captchouli.request_captcha())
    template = renderer.render_thread(thread_data, thread_id, extra_data)
    uncached_response = make_response(template)
    uncached_response.set_etag(etag_value, weak=True)
    uncached_response.headers["Cache-Control"] = "public,must-revalidate"
    cache_connection.set(view_key, str(thread.views))
    cache_connection.set(response_cache_key, template)
    cache_connection.set(etag_cache_key, etag_value)
    return uncached_response


@threads_blueprint.route("/<int:thread_id>/delete")
def delete(thread_id):
    if not get_slip() or not (get_slip().is_admin or get_slip().is_mod):
        flash("Only moderators and admins can delete threads!")
        return redirect(url_for("threads.view", thread_id=thread_id))
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    board_id = thread.board
    ThreadPosts().delete(thread_id)
    invalidate_board_cache(board_id)
    flash("Thread deleted!")
    return redirect(url_for("boards.catalog", board_id=board_id))


@threads_blueprint.route("/<int:thread_id>/move")
def move(thread_id):
    if not get_slip() or not (get_slip().is_admin or get_slip().is_mod):
        flash("Only moderators and admins can move threads!")
        return redirect(url_for("threads.view", thread_id=thread_id))
    return render_template("thread-move.html", thread_id=thread_id)


@threads_blueprint.route("/<int:thread_id>/move", methods=["POST"])
def move_submit(thread_id):
    if not get_slip() or not (get_slip().is_admin or get_slip().is_mod):
        flash("Only moderators and admins can move threads!")
        return redirect(url_for("threads.view", thread_id=thread_id))
    thread = Thread.query.get(thread_id)
    old_board = thread.board
    new_board = Board.query.filter(Board.name == request.form["board"]).one()
    thread.board = new_board.id
    db.session.add(thread)
    db.session.commit()
    invalidate_board_cache(old_board)
    invalidate_board_cache(new_board)
    flash("Thread moved!")
    return redirect(url_for("threads.view", thread_id=thread_id))
    

@threads_blueprint.route("/<int:thread_id>/new")
def new_post(thread_id):
    return render_template("new-post.html", thread_id=thread_id)


@threads_blueprint.route("/<int:thread_id>/new", methods=["POST"])
def post_submit(thread_id):
    try:
        NewPost().post(thread_id)
    except InvalidMimeError as e:
        flash("Can't post attachment with MIME type \"%s\" on this board!" % e.args[0])
        return redirect(url_for("threads.new_post", thread_id=thread_id))
    except CaptchaError as e:
        flash("CAPTCHA error: %s" % e.args[0])
        return redirect(url_for("threads.new_post", thread_id=thread_id))
    return redirect(url_for("threads.view", thread_id=thread_id) + "#thread-bottom")


@threads_blueprint.route("/post/<int:post_id>/delete")
def delete_post(post_id):
    if not get_slip() or not (get_slip().is_admin or get_slip().is_mod):
        flash("Only moderators and admins can delete posts!")
        return redirect(url_for_post(post_id))
    thread = db.session.query(Thread).filter(Thread.posts.any(Post.id == post_id)).one()
    thread_id = thread.id
    PostRemoval().delete(post_id)
    flash("Post deleted!")
    return redirect(url_for("threads.view", thread_id=thread_id))


@threads_blueprint.route("/post/<int:post_id>")
def render_post(post_id):
    raw_post = db.session.query(Post).get(post_id)
    thread_id = raw_post.thread
    thread = db.session.query(Thread).get(thread_id)
    dummy_array = ThreadPosts()._json_friendly([raw_post], thread)
    render_for_threads(dummy_array)
    post = dummy_array[0]
    reply_urls = _get_reply_urls([post])
    # TODO: properly set is_op, will be False most times, so set to that for now
    is_op = False
    return render_template("post-view-single.html", post=post, thread_id=thread_id, is_op=is_op, reply_urls=reply_urls)


@threads_blueprint.route("/<int:thread_id>/gallery")
def view_gallery(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    for post in posts:
        # TODO: either streamline what gets sent to the frontend
        # or automatically serialize datetimes so the below isn't necessary
        del post["datetime"]
        post["thumb_url"] = storage.get_thumb_url(post["media"])
        post["media_url"] = storage.get_media_url(post["media"], post["media_ext"])
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    board = db.session.query(Board).get(thread.board)
    return renderer.render_thread_gallery(board, thread_id, posts)


def _get_reply_urls(posts):
    reply_ids = set()
    for post in posts:
        for reply in post["replies"]:
            reply_ids.add(reply)
    reply_urls = dict(map(lambda i: (i, url_for_post(i)), reply_ids))
    return reply_urls
