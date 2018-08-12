import uuid

from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from model.Session import Session
from shared import db


def gen_slip(name, password):
    pass_hash = generate_password_hash(password)
    slip = Slip(name=name, pass_hash=pass_hash)
    db.session.add(slip)
    db.session.commit()
    return slip


def get_slip():
    session_id = session.get("session-id")
    if session_id:
        user_session = db.session.query(Session).filter(Session.id.like(session_id)).one_or_none()
        if user_session is None:
            session.pop("session-id")
            return None
        slip = db.session.query(Slip).filter(Slip.id == user_session.slip_id).one()
        return slip
    return None


def slip_from_id(slip_id):
    return db.session.query(Slip).filter(Slip.id == slip_id).one()


def make_session(slip):
    session_id = uuid.uuid4().hex
    user_session = Session(id=session_id, slip_id=slip.id)
    session["session-id"] = user_session.id
    db.session.add(user_session)
    db.session.commit()
    return user_session


class Slip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    pass_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_mod = db.Column(db.Boolean, nullable=False, default=False)
