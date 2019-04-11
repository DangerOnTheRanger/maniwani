from flask import Blueprint, session, redirect, request


theme_blueprint = Blueprint('theme', __name__, template_folder='template')


@theme_blueprint.route("/set-theme", methods=["POST"])
def set_theme():
    theme_name = request.form["selected-theme"]
    session["theme"] = theme_name
    return redirect(request.referrer)
