import datetime
import os
import random

from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, flash
from flask_restful import Api, reqparse
from markdown import markdown
from werkzeug.security import check_password_hash

from customjsonencoder import CustomJSONEncoder
from model.Board import Board
from model.BoardCatalogResource import BoardCatalogResource
from model.BoardList import BoardList
from model.BoardListCatalog import BoardCatalog
from model.BoardListResource import BoardListResource
from model.Firehose import Firehose
from model.FirehoseResource import FirehoseResource
from model.Media import Media
from model.NewPost import NewPost
from model.NewPostResource import NewPostResource
from model.NewThread import NewThread
from model.NewThreadResource import NewThreadResource
from model.Post import render_for_catalog, render_for_threads
from model.PostReplyPattern import url_for_post
from model.Poster import Poster
from model.Session import Session
from model.Slip import Slip, gen_slip, make_session, get_slip, slip_from_id
from model.SubmissionError import SubmissionError
from model.Tag import Tag
from model.Thread import Thread
from model.ThreadPosts import ThreadPosts
from model.ThreadPostsResource import ThreadPostsResource
from shared import db, app, rest_api

rest_api.add_resource(NewPostResource, "/api/v1/thread/<int:thread_id>/new")


@app.route("/thread/<int:thread_id>/new")
def new_post(thread_id):
    return render_template("new-post.html", thread_id=thread_id)


@app.route("/thread/<int:thread_id>/new", methods=["POST"])
def post_submit(thread_id):
    NewPost().post(thread_id)
    return redirect(url_for("view_thread", thread_id=thread_id) + "#thread-bottom")


app.jinja_env.globals["get_slip"] = get_slip

app.jinja_env.globals["slip_from_id"] = slip_from_id


@app.route("/slip")
def slip_landing():
    return render_template("slip.html")


@app.route("/slip-request", methods=["POST"])
def slip_request():
    name = request.form["name"]
    password = request.form["password"]
    slip = gen_slip(name, password)
    make_session(slip)
    return redirect(url_for("slip_landing"))


@app.route("/slip-login", methods=["POST"])
def slip_login():
    form_name = request.form["name"]
    password = request.form["password"]
    slip = db.session.query(Slip).filter(Slip.name == form_name).one_or_none()
    if slip:
        if check_password_hash(slip.pass_hash, password):
            make_session(slip)
        else:
            flash("Incorrect username or password!")
    else:
        flash("Incorrect username or password!")
    return redirect(url_for("slip_landing"))


@app.route("/unset-slip")
def unset_slip():
    if session.get("session-id"):
        session_id = session["session-id"]
        user_session = db.session.query(Session).filter(Session.id.like(session_id)).one()
        db.session.delete(user_session)
        db.session.commit()
        session.pop("session-id")
    return redirect(url_for("slip_landing"))


@app.route("/upload/<int:media_id>")
def uploaded_file(media_id):
    media = db.session.query(Media).filter(Media.id == media_id).one()
    return send_from_directory(app.config["UPLOAD_FOLDER"], "%d.%s" % (media.id, media.ext),
                               last_modified=datetime.datetime.now())


@app.route("/upload/thumb/<int:media_id>")
def uploaded_thumb(media_id):
    thumb_dir = app.config["THUMB_FOLDER"]
    return send_from_directory(thumb_dir, "%d.jpg" % media_id,
                               last_modified=datetime.datetime.now())


def style_for_tag(tag_name):
    tag = db.session.query(Tag).filter(Tag.name == tag_name).one()
    return {"bg_style": tag.bg_style, "text_style": tag.text_style}


app.jinja_env.globals["style_for_tag"] = style_for_tag

rest_api.add_resource(ThreadPostsResource, "/api/v1/thread/<int:thread_id>")

app.jinja_env.globals["url_for_post"] = url_for_post


@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    render_for_threads(posts)
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    thread.views += 1
    db.session.add(thread)
    db.session.commit()
    board_id = thread.board
    num_posters = db.session.query(Poster).filter(Poster.thread == thread_id).count()
    num_media = thread.num_media()
    return render_template("thread.html", thread_id=thread_id, board_id=board_id, posts=posts, num_views=thread.views,
                           num_media=num_media, num_posters=num_posters)


@app.route("/thread/<int:thread_id>/gallery")
def view_gallery(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    board_id = thread.board
    return render_template("gallery.html", thread_id=thread_id, board_id=board_id, posts=posts)


rest_api.add_resource(NewThreadResource, "/api/v1/thread/new")


@app.route("/thread/new/<int:board_id>")
def new_thread(board_id):
    return render_template("new-thread.html", board_id=board_id)


@app.route("/thread/new", methods=["POST"])
def thread_submit():
    try:
        thread = NewThread().post_impl()
        return redirect(url_for("view_thread", thread_id=thread.id))
    except SubmissionError as e:
        flash(str(e.args[0]))
        return redirect(url_for("new_thread", board_id=e.args[1]))


def gen_poster_id():
    id_chars = "ABCDEF0123456789"
    return ''.join(random.sample(id_chars, 4))


rest_api.add_resource(BoardListResource, "/api/v1/boards/")


@app.route("/boards")
def list_boards():
    return render_template("board-index.html", boards=BoardList().get())


rest_api.add_resource(BoardCatalogResource, "/api/v1/board/<int:board_id>/catalog")


@app.route("/board/<int:board_id>")
def view_catalog(board_id):
    threads = BoardCatalog().retrieve(board_id)
    board_name = db.session.query(Board).filter(Board.id == board_id).one().name
    render_for_catalog(threads)
    return render_template("catalog.html", threads=threads, board_id=board_id, board_name=board_name)


@app.route("/rules")
@app.route("/board/<int:board_id>/rules")
def view_rules(board_id=None):
    if board_id:
        board = db.session.query(Board).filter(Board.id == board_id).one()
        return render_template("rules.html", board=board, markdown=markdown)
    return render_template("rules.html", markdown=markdown)


@app.route("/board/<int:board_id>/admin")
def board_admin(board_id):
    if get_slip() and get_slip().is_admin:
        board = db.session.query(Board).filter(Board.id == board_id).one()
        return render_template("board-admin.html", board=board)
    else:
        flash("Only admins can access board administration!")
        return redirect(url_for("view_catalog", board_id=board_id))


@app.route("/board/<int:board_id>/admin", methods=["POST"])
def board_admin_update(board_id):
    if get_slip() is None or get_slip().is_admin is False:
        flash("Only admins can access board administration!")
        return redirect(url_for("view_catalog", board_id=board_id))
    board = db.session.query(Board).filter(Board.id == board_id).one()
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True)
    parser.add_argument("rules", type=str, required=True)
    args = parser.parse_args()
    board.name = args["name"]
    board.rules = args["rules"]
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("view_catalog", board_id=board_id))


@app.route("/faq")
def faq():
    return render_template("faq.html")


rest_api.add_resource(FirehoseResource, "/api/v1/firehose")


@app.route("/")
def index():
    return render_template("index.html", threads=Firehose().get_impl())
