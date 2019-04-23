import gevent.monkey
#gevent.monkey.patch_all()
import sys
import traceback

from flask import render_template, send_from_directory

from blueprints.boards import boards_blueprint
from blueprints.main import main_blueprint
from blueprints.slip import slip_blueprint
from blueprints.theme import theme_blueprint
from blueprints.threads import threads_blueprint
from blueprints.upload import upload_blueprint
from blueprints.live import live_blueprint
from resources import (
    BoardCatalogResource, BoardListResource, FirehoseResource,
    NewPostResource, NewThreadResource, PostRemovalResource,
    ThreadPostsResource,
)
from shared import app, rest_api

app.register_blueprint(main_blueprint, url_prefix="/")
app.register_blueprint(boards_blueprint, url_prefix="/boards")
app.register_blueprint(theme_blueprint, url_prefix="/theme")
app.register_blueprint(threads_blueprint, url_prefix="/threads")
app.register_blueprint(upload_blueprint, url_prefix="/upload")
app.register_blueprint(slip_blueprint, url_prefix="/slip")
if app.config["SERVE_STATIC"]:
    app.register_blueprint(slip_blueprint, url_prefix="/static")

if app.config["SERVE_REST"]:
    rest_api.add_resource(BoardListResource, "/api/v1/boards/")
    rest_api.add_resource(BoardCatalogResource, "/api/v1/board/<int:board_id>/catalog")
    rest_api.add_resource(ThreadPostsResource, "/api/v1/thread/<int:thread_id>")
    rest_api.add_resource(NewThreadResource, "/api/v1/thread/new")
    rest_api.add_resource(PostRemovalResource, "/api/v1/thread/post/<int:post_id>")
    rest_api.add_resource(NewPostResource, "/api/v1/thread/<int:thread_id>/new")
    rest_api.add_resource(FirehoseResource, "/api/v1/firehose")
    app.register_blueprint(live_blueprint, url_prefix="/api/v1")
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template("not-found.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(traceback.format_exc())
    return render_template("internal-error.html"), 500


@app.context_processor
def get_instance_name():
    def instance_name():
        return app.config["INSTANCE_NAME"]
    return dict(instance_name=instance_name)


@app.context_processor
def share_config():
    return dict(config=app.config)


if app.config["SERVE_STATIC"]:
    @app.route("/static/<path:path>")
    def serve_static(path):
        return send_from_directory("static", path)
