import os
import random
from customjsonencoder import CustomJSONEncoder
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__, static_url_path='')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["THUMB_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "thumbs")
app.config["SERVE_STATIC"] = True
if os.getenv("MANIWANI_CFG"):
    app.config.from_envvar("MANIWANI_CFG")
app.url_map.strict_slashes = False
app.json_encoder = CustomJSONEncoder
db = SQLAlchemy(app)
migrate = Migrate (app, db)
rest_api = Api(app)


def get_secret():
    return open("secret").read()

if os.path.exists("secret"):
    app.secret_key = get_secret()


def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)


def ip_to_int(ip_str):
    # TODO: IPv6 support
    segments = [int(s) for s in ip_str.split(".")]
    segments.reverse()
    ip_num = 0
    for segment in segments:
        ip_num = ip_num | segment
        ip_num = ip_num << 8
    return ip_num
