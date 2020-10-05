import json

from flask import render_template
import requests

from shared import app


FIREHOSE_TEMPLATE = "react-index.html"
FIREHOSE_RENDER_URL = "/render/firehose"
CATALOG_TEMPLATE = "react-catalog.html"
CATALOG_RENDER_URL = "/render/catalog"
THREAD_TEMPLATE = "react-thread.html"
THREAD_RENDER_URL = "/render/thread"
NEW_THREAD_TEMPLATE ="react-new-thread.html"
NEW_THREAD_RENDER_URL = "/render/new-thread"
GALLERY_TEMPLATE = "react-gallery.html"
GALLERY_RENDER_URL = "/render/gallery"


def captchouli_to_json(captchouli):
    return {"captcha_method": "CAPTCHOULI",
            "captchouli": {
                "captcha_id": captchouli.captcha_id,
                "character": captchouli.character,
                "images": captchouli.images}}


def render_react_template(template, renderer_path, data):
    renderer_url = app.config["RENDERER_HOST"] + renderer_path
    payload = {"template": template, "data": data}
    response = requests.post(renderer_url, json=payload)
    return response.text


def render_firehose(firehose, greeting, extra_data=None):
    base_template = render_template(FIREHOSE_TEMPLATE, greeting=greeting)
    return render_react_template(base_template, FIREHOSE_RENDER_URL, {"firehose": firehose})


def render_catalog(catalog, board_name, board_id, extra_data=None):
    data = {"catalog": catalog, "board_id": board_id}
    if extra_data:
        data.update(extra_data)
    base_template = render_template(CATALOG_TEMPLATE, board_name=board_name, board_id=board_id)
    return render_react_template(base_template, CATALOG_RENDER_URL, data)


def render_thread(thread, thread_id, extra_data=None):
    data = {"thread": thread, "thread_id": thread_id}
    if extra_data:
        data.update(extra_data)
    base_template = render_template(THREAD_TEMPLATE, subject=thread["posts"][0].get("subject") or "", thread_id=thread_id) 
    return render_react_template(base_template, THREAD_RENDER_URL, data)


def render_new_thread_form(board_id, extra_data=None):
    data = {"board_id": board_id}
    if extra_data:
        data.update(extra_data)
    base_template = render_template(NEW_THREAD_TEMPLATE)
    return render_react_template(base_template, NEW_THREAD_RENDER_URL, data)


def render_thread_gallery(board, thread_id, posts):
    base_template = render_template(GALLERY_TEMPLATE, board=board, thread_id=thread_id)
    data = {"posts": posts}
    return render_react_template(base_template, GALLERY_RENDER_URL, data)
