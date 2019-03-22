import json
import os

from alembic import command
from alembic.config import Config
from flask.cli import with_appcontext

from model.Board import Board
from model.Slip import gen_slip
from model.Tag import Tag
from model.Media import storage
from shared import app, db


MIGRATION_DIR = "./migrations"
BOOTSTRAP_SETTINGS = "./deploy-configs/bootstrap-config.json"
SECRET_FILE = "./deploy-configs/secret"


def initialize_db():
    db.create_all()


def grab_settings():
    settings_file = open(BOOTSTRAP_SETTINGS)
    return json.load(settings_file)


def setup_boards(json_settings):
    for board_info in json_settings["boards"]:
        name = board_info["name"]
        threadlimit = board_info.get("threadlimit") or json_settings["default_threadlimit"]
        mimetypes = board_info.get("mimetypes")
        if mimetypes is None:
            mimetypes = json_settings["default_mimetypes"]
            extra_mimetypes = board_info.get("extra_mimetypes")
            if extra_mimetypes:
                mimetypes = mimetypes + "|" + extra_mimetypes
        rule_file = board_info.get("rules")
        rules = ""
        if rule_file:
            rules = open(os.path.join("deploy-configs", rule_file)).read()
        board = Board(name=name, max_threads=threadlimit, mimetypes=mimetypes, rules=rules)
        db.session.add(board)


def setup_slips(json_settings):
    for slip_info in json_settings["slips"]:
        username = slip_info["username"]
        password = slip_info["password"]
        is_admin = slip_info.get("is_admin") or False
        is_mod = slip_info.get("is_mod") or False
        slip = gen_slip(username, password)
        slip.is_admin = is_admin
        slip.is_mod = is_mod
        db.session.add(slip)
        db.session.commit()


def setup_tags(json_settings):
    for tag_info in json_settings["tags"]:
        tag_name = tag_info["tag"]
        bg_style = tag_info["bgstyle"]
        text_style = tag_info["textstyle"]
        tag = Tag(name=tag_name, bg_style=bg_style, text_style=text_style)
        db.session.add(tag)


def write_secret():
    if os.path.exists(SECRET_FILE):
        os.remove(SECRET_FILE)
    open(SECRET_FILE, "w+").write(str(os.urandom(16)))


def setup_storage():
    storage.bootstrap()


def save_db():
    if os.path.exists(MIGRATION_DIR):
        alembic_config = Config(os.path.join(MIGRATION_DIR, "alembic.ini"))
        alembic_config.set_main_option("script_location", MIGRATION_DIR)
        with app.app_context():
            # mark the database as being up to date migration-wise since
            # it was just created
            command.stamp(config=alembic_config, revision="head")
    db.session.commit()


def main():
    initialize_db()
    settings = grab_settings()
    setup_boards(settings)
    setup_slips(settings)
    setup_tags(settings)
    setup_storage()
    write_secret()
    save_db()


if __name__ == "__main__":
    main()
