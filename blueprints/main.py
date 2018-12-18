from flask import Blueprint, render_template
from markdown import markdown

from model.Firehose import Firehose


main_blueprint = Blueprint('main', __name__, template_folder='template')


@main_blueprint.route("/")
def index():
    greeting = open("deploy-configs/index-greeting.html").read()
    return render_template("index.html", greeting=greeting, threads=Firehose().get_impl())


@main_blueprint.route("/rules")
def rules():
    return render_template("rules.html", markdown=markdown)


@main_blueprint.route("/faq")
def faq():
    return render_template("faq.html")
