import re
from html.parser import HTMLParser

import requests

from shared import app


def request_captcha():
    response = requests.get(app.config["CAPTCHOULI_URL"])
    parser = FormParser()
    parser.feed(response.text)
    return parser.get_captcha()
def valid_solution(captcha_form):
    response = requests.post(app.config["CAPTCHOULI_URL"], data=captcha_form)
    return response.text == captcha_form["captchouli-id"]


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._captcha_id = ""
        self._images = {}
        self._current_image = ""
        self._target_character = ""
        self._processing_character = False
    def get_captcha(self):
        return CaptchouliCaptcha(self._captcha_id, self._target_character, self._images)
    def handle_starttag(self, tag, attrs):
        dict_attrs = dict(attrs)
        if tag == "input":
            if dict_attrs.get("name") == "captchouli-id":
                self._captcha_id = dict_attrs["value"]
            elif dict_attrs.get("class") == "captchouli-checkbox":
                self._current_image = dict_attrs["name"]
        elif tag == "img":
            self._images[self._current_image] = dict_attrs["src"]
        elif tag == "b":
            self._processing_character = True
    def handle_data(self, data):
        if self._processing_character:
            self._target_character = data
            self._processing_character = False


class CaptchouliCaptcha:
    def __init__(self, captcha_id, character, images):
        self.captcha_id = captcha_id
        self.character = character
        self.images = images
