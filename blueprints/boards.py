import time

from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, session
from flask_restful import reqparse
from markdown import markdown
from werkzeug.http import parse_etags

import cache
import captchouli
import renderer
from model.Media import storage
from model.Board import Board
from model.BoardList import BoardList
from model.BoardListCatalog import BoardCatalog
from model.Post import render_for_catalog
from model.Slip import get_slip, get_slip_bitmask
from model.Tag import Tag
from shared import db, app


def get_tags(threads):
    tag_names = set()
    for thread in threads:
        for tag in thread["tags"]:
            tag_names.add(tag)
    tag_styles = {}
    found_tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
    for tag in found_tags:
        tag_styles[tag.name] = {}
        if tag.bg_style:
            tag_styles[tag.name]["bg_style"] = tag.bg_style
        if tag.text_style:
            tag_styles[tag.name]["text_style"] = tag.text_style
    return tag_styles


boards_blueprint = Blueprint('boards', __name__, template_folder='template')


@boards_blueprint.route("/")
def list():
    boards = BoardList().get()
    for board in boards:
        board["catalog_url"] = url_for("boards.catalog", board_id=board["id"])
        if board["media"]:
            board["thumb_url"] = storage.get_thumb_url(board["media"])
    return renderer.render_board_index(boards)


@boards_blueprint.route("/<int:board_id>")
def catalog(board_id):
    current_theme = session.get("theme") or app.config.get("DEFAULT_THEME") or "stock"
    response_cache_key = "board-%d-%d-%s-render" % (board_id, get_slip_bitmask(), current_theme)
    cache_connection = cache.Cache()
    cached_response_body = cache_connection.get(response_cache_key)
    etag_value = "%s-%f" % (response_cache_key, time.time())
    etag_cache_key = "%s-etag" % response_cache_key
    if cached_response_body:
        etag_header = request.headers.get("If-None-Match")
        current_etag = cache_connection.get(etag_cache_key)
        if etag_header:
            parsed_etag = parse_etags(etag_header)
            if parsed_etag.contains_weak(current_etag):
                return make_response("", 304)
        cached_response = make_response(cached_response_body)
        cached_response.set_etag(current_etag, weak=True)
        cached_response.headers["Cache-Control"] = "public,must-revalidate"
        return cached_response
    threads = BoardCatalog().retrieve(board_id)
    board = db.session.query(Board).get(board_id)
    board_name = board.name
    render_for_catalog(threads)
    tag_styles = get_tags(threads)
    catalog_data = {}
    catalog_data["tag_styles"] = tag_styles
    for thread in threads:
        del thread["last_updated"]
    catalog_data["threads"] = threads
    extra_data = {}
    if app.config.get("CAPTCHA_METHOD") == "CAPTCHOULI":
        extra_data = renderer.captchouli_to_json(captchouli.request_captcha())
    template = renderer.render_catalog(catalog_data, board_name, board_id, extra_data)
    uncached_response = make_response(template)
    uncached_response.set_etag(etag_value, weak=True)
    uncached_response.headers["Cache-Control"] = "public,must-revalidate"
    cache_connection.set(response_cache_key, template)
    cache_connection.set(etag_cache_key, etag_value)
    return uncached_response


@boards_blueprint.route("/rules", defaults={'board_id': None})
@boards_blueprint.route("/rules/<int:board_id>")
def rules(board_id):
    if board_id is None:
        return redirect(url_for('main.rules'))
    board = db.session.query(Board).filter(Board.id == board_id).one()
    return render_template("rules.html", board=board, markdown=markdown)


@boards_blueprint.route("/admin/<int:board_id>")
def admin(board_id):
    if get_slip() and get_slip().is_admin:
        board = db.session.query(Board).filter(Board.id == board_id).one()
        return render_template("board-admin.html", board=board)
    else:
        flash("Only admins can access board administration!")
        return redirect(url_for("boards.catalog", board_id=board_id))


@boards_blueprint.route("/admin/<int:board_id>", methods=["POST"])
def admin_update(board_id):
    if get_slip() is None or get_slip().is_admin is False:
        flash("Only admins can access board administration!")
        return redirect(url_for("boards.catalog", board_id=board_id))
    board = db.session.query(Board).filter(Board.id == board_id).one()
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True)
    parser.add_argument("rules", type=str, required=True)
    parser.add_argument("max-threads", type=int, required=True)
    parser.add_argument("mimetypes", type=str, required=True)
    args = parser.parse_args()
    board.name = args["name"]
    board.rules = args["rules"]
    board.max_threads = args["max-threads"]
    board.mimetypes = args["mimetypes"]
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("boards.catalog", board_id=board_id))
