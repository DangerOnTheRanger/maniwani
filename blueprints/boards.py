from flask import Blueprint, render_template, redirect, url_for, flash
from flask_restful import reqparse
from markdown import markdown

from model.Board import Board
from model.BoardList import BoardList
from model.BoardListCatalog import BoardCatalog
from model.Post import render_for_catalog
from model.Slip import get_slip
from model.Tag import Tag
from shared import db


def style_for_tag(tag_name):
    tag = db.session.query(Tag).filter(Tag.name == tag_name).one()
    return {"bg_style": tag.bg_style, "text_style": tag.text_style}


boards_blueprint = Blueprint('boards', __name__, template_folder='template')
boards_blueprint.add_app_template_global(style_for_tag)


@boards_blueprint.route("/")
def list():
    return render_template("board-index.html", boards=BoardList().get())


@boards_blueprint.route("/<int:board_id>")
def catalog(board_id):
    threads = BoardCatalog().retrieve(board_id)
    board_name = db.session.query(Board).filter(Board.id == board_id).one().name
    render_for_catalog(threads)
    return render_template("catalog.html", threads=threads, board_id=board_id, board_name=board_name)


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
    args = parser.parse_args()
    board.name = args["name"]
    board.rules = args["rules"]
    board.max_threads = args["max-threads"]
    board.mimetypes = args["mimetypes"]
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("boards.catalog", board_id=board_id))
