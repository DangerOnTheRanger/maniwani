import datetime

from flask import Blueprint, current_app, send_from_directory

from model.Media import Media
from shared import db


upload_blueprint = Blueprint('upload', __name__, template_folder='template')


@upload_blueprint.route("/<int:media_id>")
def file(media_id):
    media = db.session.query(Media).filter(Media.id == media_id).one()
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], "%d.%s" % (media.id, media.ext),
                               last_modified=datetime.datetime.now())


@upload_blueprint.route("/thumb/<int:media_id>")
def thumb(media_id):
    thumb_dir = current_app.config["THUMB_FOLDER"]
    return send_from_directory(thumb_dir, "%d.jpg" % media_id,
                               last_modified=datetime.datetime.now())
