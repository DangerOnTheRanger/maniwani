from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from model.Session import Session
from model.Slip import Slip, gen_slip, make_session, get_slip, slip_from_id
from shared import db


slip_blueprint = Blueprint('slip', __name__, template_folder='template')
slip_blueprint.add_app_template_global(get_slip)
slip_blueprint.add_app_template_global(slip_from_id)


@slip_blueprint.route("/")
def landing():
    return render_template("slip.html")


@slip_blueprint.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    password = request.form["password"]
    slip = gen_slip(name, password)
    make_session(slip)
    return redirect(url_for("slip.landing"))


@slip_blueprint.route("/login", methods=["POST"])
def login():
    form_name = request.form["name"]
    password = request.form["password"]
    slip = db.session.query(Slip).filter(Slip.name == form_name).one_or_none()
    if slip:
        if check_password_hash(slip.pass_hash, password):
            make_session(slip)
        else:
            flash("Incorrect username or password!")
    else:
        flash("Incorrect username or password!")
    return redirect(url_for("slip.landing"))


@slip_blueprint.route("/unset")
def unset():
    if session.get("session-id"):
        session_id = session["session-id"]
        user_session = db.session.query(Session).filter(Session.id.like(session_id)).one()
        db.session.delete(user_session)
        db.session.commit()
        session.pop("session-id")
    return redirect(url_for("slip.landing"))
