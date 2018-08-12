import os

from flask import Flask
from flask_restful import Api

from customjsonencoder import CustomJSONEncoder
from model.Board import Board
from model.Slip import gen_slip
from model.Tag import Tag
import model.Media
import model.Poster
from shared import db


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["THUMB_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "thumb")
app.json_encoder = CustomJSONEncoder
rest_api = Api(app)

db.create_all()
# set up some boards
for board_name in ("anime", "tech", "meta", "politics", "gaming", "music"):
    board = Board(name=board_name)
    db.session.add(board)
# admin credentials generation
admin = gen_slip("admin", "admin")
admin.is_admin = True
db.session.add(admin)
# special tags
for tag_name, bg_style, text_style in (("general", "bg-secondary", "text-light"),):
    tag = Tag(name=tag_name, bg_style=bg_style, text_style=text_style)
    db.session.add(tag)
db.session.commit()
# write a secret so we can have session support
open("secret", "w").write(str(os.urandom(16)))
# create upload and thumbnail directory if necessary
if not os.path.exists("uploads/thumb"):
    os.makedirs("uploads/thumb")
