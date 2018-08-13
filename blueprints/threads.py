from flask import Blueprint, render_template, redirect, url_for, flash

from model.NewPost import NewPost
from model.NewThread import NewThread
from model.Post import render_for_threads
from model.PostReplyPattern import url_for_post
from model.Poster import Poster
from model.SubmissionError import SubmissionError
from model.Thread import Thread
from model.ThreadPosts import ThreadPosts
from shared import db


threads_blueprint = Blueprint('threads', __name__, template_folder='template')
threads_blueprint.add_app_template_global(url_for_post)


@threads_blueprint.route("/new/<int:board_id>")
def new(board_id):
    return render_template("new-thread.html", board_id=board_id)


@threads_blueprint.route("/new", methods=["POST"])
def submit():
    try:
        thread = NewThread().post_impl()
        return redirect(url_for("threads.view", thread_id=thread.id))
    except SubmissionError as e:
        flash(str(e.args[0]))
        return redirect(url_for("threads.new", board_id=e.args[1]))


@threads_blueprint.route("/<int:thread_id>")
def view(thread_id):
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


@threads_blueprint.route("/<int:thread_id>/new")
def new_post(thread_id):
    return render_template("new-post.html", thread_id=thread_id)


@threads_blueprint.route("/<int:thread_id>/new", methods=["POST"])
def post_submit(thread_id):
    NewPost().post(thread_id)
    return redirect(url_for("threads.view", thread_id=thread_id) + "#thread-bottom")


@threads_blueprint.route("/<int:thread_id>/gallery")
def view_gallery(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    board_id = thread.board
    return render_template("gallery.html", thread_id=thread_id, board_id=board_id, posts=posts)
