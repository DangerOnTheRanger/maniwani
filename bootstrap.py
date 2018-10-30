import json
import os
from model.Board import Board
from model.Slip import gen_slip
from model.Tag import Tag
from model.Media import storage
from shared import db


BOOTSTRAP_SETTINGS = "./build-helpers/bootstrap-config.json"
SECRET_FILE = "./secret"


def initialize_db():
    db.create_all()


def grab_settings():
    settings_file = open(BOOTSTRAP_SETTINGS)
    return json.load(settings_file)


def setup_boards(json_settings):
    for board_info in json_settings["boards"]:
        name = board_info["name"]
        threadlimit = board_info.get("threadlimit") or json_settings["default_threadlimit"]
        board = Board(name=name, max_threads=threadlimit)
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


def setup_tags(json_settings):
    for tag_info in json_settings["tags"]:
        tag_name = tag_info["tag"]
        bg_style = tag_info["bgstyle"]
        text_style = tag_info["textstyle"]


def write_secret():
    if os.path.exists(SECRET_FILE):
        os.remove(SECRET_FILE)
    open("secret", "w+").write(str(os.urandom(16)))


def setup_storage():
    storage.bootstrap()


def save_db():
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
