import random
import string
import time

from flask import session

import keystore
from shared import app


def _gen_cooldown_id():
    return "captcha_cooldown_" + "".join(random.choices(string.hexdigits, k=10))


@app.context_processor
def cooldown_processor():
    kwargs = {"on_captcha_cooldown": on_captcha_cooldown}
    return dict(**kwargs)


def on_captcha_cooldown():
    captcha_cooldown = False
    cooldown_id = session.get("cooldown_id")
    if app.config.get("CAPTCHA_COOLDOWN") and cooldown_id:
        key_client = keystore.Keystore()
        if key_client.exists(cooldown_id):
            current_timestamp = int(time.time())
            cooldown_timestamp = int(key_client.get(cooldown_id))
            if current_timestamp - cooldown_timestamp < app.config["CAPTCHA_COOLDOWN"]:
                captcha_cooldown = True
    return captcha_cooldown


def refresh_captcha_cooldown():
    if app.config.get("CAPTCHA_COOLDOWN"):
        cooldown_id = session.get("cooldown_id")
        if cooldown_id is None:
            cooldown_id = _gen_cooldown_id()
        current_timestamp = str(int(time.time()))
        key_client = keystore.Keystore()
        key_client.set(cooldown_id, current_timestamp)
        session["cooldown_id"] = cooldown_id
