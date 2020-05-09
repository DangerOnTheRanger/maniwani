import json

from flask import render_template
import requests

from shared import app


CATALOG_TEMPLATE = "react-catalog.html"
CATALOG_RENDER_URL = "/render/catalog"
THREAD_TEMPLATE = "react-thread.html"
THREAD_RENDER_URL = "/render/thread"


def render_react_template(template, renderer_path, data):
    renderer_url = app.config["RENDERER_HOST"] + renderer_path
    payload = {"template": template, "data": data}
    response = requests.post(renderer_url, json=payload)
    return response.text


def render_catalog(catalog, board_name, board_id):
    base_template = render_template(CATALOG_TEMPLATE, board_name=board_name, board_id=board_id)
    return render_react_template(base_template, CATALOG_RENDER_URL, catalog)


def render_thread(thread, thread_id):
    base_template = render_template(THREAD_TEMPLATE, subject=thread["posts"][0].get("subject") or "", thread_id=thread_id) 
    return render_react_template(base_template, THREAD_RENDER_URL, thread)
