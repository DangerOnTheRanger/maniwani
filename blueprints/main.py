import time

from flask import Blueprint, render_template, make_response, request, session
from markdown import markdown
from werkzeug.http import parse_etags

import cache
from blueprints.boards import get_tags
from model.Firehose import Firehose
from model.Slip import get_slip_bitmask
from shared import app

main_blueprint = Blueprint('main', __name__, template_folder='template')


@main_blueprint.route("/")
def index():
    cache_connection = cache.Cache()
    current_theme = session.get("theme") or app.config.get("DEFAULT_THEME") or "stock"
    response_cache_key = "firehose-%d-%s-render" % (get_slip_bitmask(), current_theme)
    cached_response_body = cache_connection.get(response_cache_key)
    etag_value = "%s-%f"  % (response_cache_key, time.time())
    etag_cache_key = "%s-etag" % response_cache_key
    if cached_response_body:
        etag_header = request.headers.get("If-None-Match")
        current_etag = cache_connection.get(etag_cache_key)
        if etag_header:
            parsed_etag = parse_etags(etag_header)
            if parsed_etag.contains_weak(current_etag):
                return make_response("", 304)
        cached_response = make_response(cached_response_body)
        cached_response.set_etag(current_etag, weak=True)
        cached_response.headers["Cache-Control"] = "public,must-revalidate"
        return cached_response
    greeting = open("deploy-configs/index-greeting.html").read()
    threads = Firehose().get_impl()
    tag_styles = get_tags(threads)
    template = render_template("index.html", greeting=greeting, threads=threads, tag_styles=tag_styles)
    uncached_response = make_response(template)
    uncached_response.set_etag(etag_value, weak=True)
    uncached_response.headers["Cache-Control"] = "public,must-revalidate"
    cache_connection.set(response_cache_key, template)
    cache_connection.set(etag_cache_key, etag_value)
    return uncached_response


@main_blueprint.route("/rules")
def rules():
    return render_template("rules.html", markdown=markdown)


@main_blueprint.route("/faq")
def faq():
    return render_template("faq.html")
