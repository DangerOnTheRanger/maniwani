import os
import random
import ipaddress
from customjsonencoder import CustomJSONEncoder
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from werkzeug.datastructures import ImmutableDict

import jinja_cache


class ManiwaniApp(Flask):
    jinja_options = ImmutableDict(extensions=["jinja2.ext.autoescape", "jinja2.ext.with_"],
                                  bytecode_cache=jinja_cache.KeystoreCache())

    
app = ManiwaniApp(__name__, static_url_path='')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["THUMB_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "thumbs")
app.config["SERVE_STATIC"] = True
app.config["SERVE_REST"] = True
app.config["USE_RECAPTCHA"] = False
app.config["FIREHOSE_LENGTH"] = 10
if os.getenv("MANIWANI_CFG"):
    app.config.from_envvar("MANIWANI_CFG")
app.url_map.strict_slashes = False
app.json_encoder = CustomJSONEncoder
db = SQLAlchemy(app)
migrate = Migrate(app, db)
rest_api = Api(app)

SECRET_FILE = "./deploy-configs/secret"
def get_secret():
    return open(SECRET_FILE).read()

if os.path.exists(SECRET_FILE):
    app.secret_key = get_secret()


def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)


def ip_to_int(ip_str):
    # The old version of ip_to_int had a logical bug where it would always shift the
    # final result to the left by 8. This is preserved with the `<< 8`.
    return int.from_bytes(
        ipaddress.ip_address(ip_str).packed,
        byteorder="little"
    ) << 8
