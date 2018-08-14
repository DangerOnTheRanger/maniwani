import datetime

from flask import Blueprint, current_app, send_from_directory

from model.Media import Media, storage
from shared import db


upload_blueprint = Blueprint('upload', __name__, template_folder='template')


@upload_blueprint.route("/<int:media_id>")
def file(media_id):
    return storage.get_attachment(media_id)


@upload_blueprint.route("/thumb/<int:media_id>")
def thumb(media_id):
    return storage.get_thumbnail(media_id)
