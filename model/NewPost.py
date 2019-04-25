from typing import Union

from flask import request
from flask_restful import reqparse, inputs

from model.Thread import Thread
from model.Post import Post

from cooldown import on_captcha_cooldown, refresh_captcha_cooldown
from post import create_post
from shared import app, db

def get_request_data() -> reqparse.Namespace:
    "Returns data about a new post request."

    parser = reqparse.RequestParser()
    parser.add_argument("subject", type=str)
    parser.add_argument("body", type=str, required=True)
    parser.add_argument("useslip", type=inputs.boolean)
    parser.add_argument("spoiler", type=inputs.boolean)

    if not on_captcha_cooldown():
        captcha_method = app.config.get("CAPTCHA_METHOD")
        if captcha_method == "RECAPTCHA":
            parser.add_argument("recaptcha-token", type=str, required=True)
        elif captcha_method == "CAPTCHOULI":
            parser.add_argument("captchouli-id", type=str, required=True)
            for i in range(9):
                # For each image square
                parser.add_argument(f"captchouli-{i}", type=str, default=False)

    return parser.parse_args()


def get_thread(thread_id: int) -> Thread:
    "Returns a thread by its ID."
    return (
        db.session.query(Thread)
        .filter_by(id=thread_id)
        .one()
    )


class NewPost:
    def post(self, thread: Union[Thread, int]) -> Post:
        if isinstance(thread, int):
            thread = get_thread(thread)
        args = dict(get_request_data())
        return create_post(thread, args)
