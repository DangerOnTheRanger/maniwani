from functools import wraps

from flask import request
from werkzeug.security import check_password_hash

from model.Slip import Slip
from shared import db


def _slip_check():
    if request.authorization is None:
        return None
    username = request.authorization.username
    slip = db.session.query(Slip).filter(Slip.name == username).one_or_none()
    if slip is None:
        return None
    password = request.authorization.password
    if check_password_hash(slip.pass_hash, password) is False:
        return None
    return slip


def slip_required(endpoint):
    @wraps(endpoint)
    def auth_decorator(*args, **kwargs):
        slip = _slip_check()
        if slip is None:
            return {"error": "Authentication failed"}, 401
        return endpoint(*args, **kwargs)
    return auth_decorator


def admin_required(endpoint):
    @wraps(endpoint)
    def auth_decorator(*args, **kwargs):
        slip = _slip_check()
        if slip is None:
            return {"error": "Authentication failed"}, 401
        if slip.is_admin is False:
            return {"error": "Authentication failed"}, 401
        return endpoint(*args, **kwargs)
    return auth_decorator


def mod_required(endpoint):
    @wraps(endpoint)
    def auth_decorator(*args, **kwargs):
        slip = _slip_check()
        if slip is None:
            return {"error": "Authentication failed"}, 401
        if slip.is_admin is False and slip.is_mod is False:
            return {"error": "Authentication failed"}, 401
        return endpoint(*args, **kwargs)
    return auth_decorator
