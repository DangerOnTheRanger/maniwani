import json
from typing import List

from flask import request
from flask_restful import reqparse
from sqlalchemy import desc

import cache
import keystore
from model.Board import Board
from model.NewPost import NewPost
from model.SubmissionError import SubmissionError
from model.Tag import Tag
from model.Thread import Thread
from shared import app, db


def get_tags(args: dict) -> List[Tag]:
    "Returns a list of Tag objects from the given tag list."
    if not args["tags"]:
        return []

    tags = list(map(lambda s: s.strip(), args["tags"].split(",")))
    ret = []

    # add all the tags that already exist in the database
    for row in db.session.query(Tag, Tag.name).filter(Tag.name.in_(tags)):
        tags.remove(row.name)
        ret.append(row.Tag)

    # create the remaining tabs and add them to the transaction
    # (the above loop removes all tags that already exist in the database
    # from the list, # therefore simply looping over the tags list should
    # suffice)
    for tag in tags:
        ret.append(Tag(name=tag))

    return ret



def slide_last_thread(board_id: int):
    """
    If the maximum amount of threads have been reached on the board, slides
    off the last thread on the board.
    """

    num_threads = (
        db.session.query(Thread)
        .filter(Thread.board == board_id)
        .count()
    )
    board_max_threads = (
        db.session.query(Board.max_threads)
        .filter(Board.id == board_id)
        .one()
    ).max_threads

    if num_threads >= board_max_threads:
        dead_thread = (
            db.session.query(Thread)
            .filter(Thread.board == board_id)
            .order_by(Thread.last_updated.asc())
            .first()
        )
        db.session.delete(dead_thread)


def publish_new_thread(thread: Thread):
    "Publishes the new thread to the pub-sub system."

    client = keystore.Pubsub()
    client.publish("new-thread", json.dumps({
        "thread": thread.id,
        "board": thread.board,
    }))


def create_thread(args: dict) -> Thread:
    "Creates a new thread out of the given arguments."

    if "media" not in request.files or not request.files["media"].filename:
        raise SubmissionError(
            "A file is required to post a thread!", args["board"])

    tags = get_tags(args)
    for tag in tags:
        db.session.add(tag)
    db.session.flush()

    slide_last_thread(args["board"])

    thread = Thread(board=args["board"], views=0, tags=tags)
    db.session.add(thread)
    db.session.flush()
    NewPost().post(thread)

    publish_new_thread(thread)

    return thread


def invalidate_board_cache(board_id: int):
    """Invalidates the cache for the given board in addition to the firehose."""
    cache_connection = cache.Cache()
    slip_bitmasks = 0, 1, 3, 7
    theme_list = app.config.get("THEME_LIST") or ("stock", "harajuku", "wildride")
    # invalidate full-page renders
    for bitmask in slip_bitmasks:
        for theme in theme_list:
            catalog_render_key = "board-%d-%d-%s-render" % (board_id, bitmask, theme)
            cache_connection.invalidate(catalog_render_key)
            firehose_render_key = "firehose-%d-%s-render" % (bitmask, theme)
            cache_connection.invalidate(firehose_render_key)
    # invalidate retrieved thread listings
    catalog_thread_key = "board-%d-threads" % board_id
    cache_connection.invalidate(catalog_thread_key)
    # invalidate firehose listing
    firehose_thread_key = "firehose-threads"
    cache_connection.invalidate(firehose_thread_key)
