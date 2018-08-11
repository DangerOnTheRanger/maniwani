import datetime
import os
import random
import re
import uuid

from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory, make_response, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, inputs
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
from sqlalchemy.orm import relationship
from sqlalchemy import desc, and_
from markdown import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.postprocessors import Postprocessor
from markdown.util import etree
from markdown.treeprocessors import Treeprocessor

from nocache import nocache
from customjsonencoder import CustomJSONEncoder
from outputmixin import OutputMixin

REPLY_REGEXP = r">>([0-9]+)"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["THUMB_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "thumb")
app.json_encoder = CustomJSONEncoder
db = SQLAlchemy(app)
rest_api = Api(app)
def get_secret():
    return open("secret").read()
app.secret_key = get_secret()


class Post(OutputMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4096), nullable=False)
    subject = db.Column(db.String(64), nullable=True)
    thread = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    poster = db.Column(db.Integer, db.ForeignKey("poster.id"), nullable=False)
    media = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=True)
    spoiler = db.Column(db.Boolean, nullable=True)
class SubmissionError(Exception): pass

class NewPost:
    def post(self, thread_id):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("useslip", type=inputs.boolean)
        parser.add_argument("spoiler", type=inputs.boolean)
        args = parser.parse_args()
        ip = ip_to_int(request.environ["REMOTE_ADDR"])
        poster = db.session.query(Poster).filter_by(thread=thread_id, ip_address=ip).first()
        body = args["body"]
        should_bump = False
        if poster is None:
            poster_hex = gen_poster_id()
            poster = Poster(hex_string=poster_hex, ip_address=ip, thread=thread_id)
            db.session.add(poster)
            db.session.commit()
            # bump thread if the poster hasn't posted in this thread before
            should_bump = True
        if args.get("useslip") is True:
            slip = get_slip()
            if slip:
                poster.slip = slip.id
                db.session.add(poster)
                db.session.commit()
        media_id = None
        if "media" in request.files and request.files["media"].filename:
            uploaded_file = request.files["media"]
            file_ext = uploaded_file.filename.rsplit('.', 1)[1].lower()
            media = Media(ext=file_ext)
            db.session.add(media)
            db.session.commit()
            media_id = media.id
            full_path = os.path.join(app.config["UPLOAD_FOLDER"],"%d.%s" % (media_id, file_ext))
            uploaded_file.save(full_path)
            if file_ext != "webm":
                # non-webm thumbnail generation
                thumb = Image.open(full_path)
                if thumb.mode in ("RGBA", "LA"):
                    background = Image.new(thumb.mode[:-1], thumb.size, (255, 255, 255))
                    background.paste(thumb, thumb.split()[-1])
                    thumb = background
                size = thumb.size
                scale_factor = 0
                # width > height
                if size[0] > size[1]:
                    scale_factor = 500 / size[0]
                else:
                    scale_factor = 500 / size[1]
                new_width = int(thumb.width * scale_factor)
                new_height = int(thumb.height * scale_factor)
                thumb = thumb.resize((new_width, new_height), Image.LANCZOS)
                thumb.convert("RGB").save(os.path.join(app.config["THUMB_FOLDER"], "%d.jpg" % media_id), "JPEG")
            else:
                # FIXME: webm thumbnail generation
                pass
        post = Post(body=body, subject=args["subject"], thread=thread_id, poster=poster.id, media=media_id, spoiler=args["spoiler"])
        db.session.add(post)
        db.session.commit()
        replying = re.finditer(REPLY_REGEXP, body)
        if replying:
            for match in replying:
                for raw_reply_id in match.groups():
                    reply_id = int(raw_reply_id)
                    reply = Reply(reply_from=post.id, reply_to=reply_id)
                    db.session.add(reply)
                    db.session.commit()
        if should_bump:
            thread = db.session.query(Thread).filter_by(id=thread_id).one()
            thread.last_updated = post.datetime
            db.session.commit()
class NewPostResource(NewPost, Resource): pass
rest_api.add_resource(NewPostResource, "/api/v1/thread/<int:thread_id>/new")


@app.route("/thread/<int:thread_id>/new")
def new_post(thread_id):
    return render_template("new-post.html", thread_id=thread_id)


@app.route("/thread/<int:thread_id>/new", methods=["POST"])
def post_submit(thread_id):
    NewPost().post(thread_id)
    return redirect(url_for("view_thread", thread_id=thread_id) + "#thread-bottom")
        

class Poster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hex_string = db.Column(db.String(4), nullable=False)
    ip_address = db.Column(db.Integer, nullable=False)
    thread = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)
    slip = db.Column(db.Integer, db.ForeignKey("slip.id"), nullable=True)

    
class Slip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    pass_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_mod = db.Column(db.Boolean, nullable=False, default=False)
class Session(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    slip_id = db.Column(db.Integer, db.ForeignKey("slip.id"), nullable=False)
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
app.jinja_env.globals["get_slip"] = get_slip
def slip_from_id(slip_id):
    return db.session.query(Slip).filter(Slip.id == slip_id).one()
app.jinja_env.globals["slip_from_id"] = slip_from_id
def make_session(slip):
    session_id = uuid.uuid4().hex
    user_session = Session(id=session_id, slip_id=slip.id)
    session["session-id"] = user_session.id
    db.session.add(user_session)
    db.session.commit()
    return user_session


@app.route("/slip")
def slip_landing():
    return render_template("slip.html")
@app.route("/slip-request", methods=["POST"])
def slip_request():
    name = request.form["name"]
    password = request.form["password"]
    slip = gen_slip(name, password)
    make_session(slip)
    return redirect(url_for("slip_landing"))
@app.route("/slip-login", methods=["POST"])
def slip_login():
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
    return redirect(url_for("slip_landing"))
@app.route("/unset-slip")
def unset_slip():
    if session.get("session-id"):
        session_id = session["session-id"]
        user_session = db.session.query(Session).filter(Session.id.like(session_id)).one()
        db.session.delete(user_session)
        db.session.commit()
        session.pop("session-id")
    return redirect(url_for("slip_landing"))

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext = db.Column(db.String(3), nullable=False)


class Reply(db.Model):
    reply_from = db.Column(db.Integer,
                           db.ForeignKey("post.id"),
                           nullable=False, primary_key=True)
    reply_to = db.Column(db.Integer,
                         db.ForeignKey("post.id"),
                         nullable=False,
                         primary_key=True)

    
@app.route("/upload/<int:media_id>")
def uploaded_file(media_id):
    media = db.session.query(Media).filter(Media.id == media_id).one()
    return send_from_directory(app.config["UPLOAD_FOLDER"], "%d.%s" % (media.id, media.ext),
                               last_modified=datetime.datetime.now())

@app.route("/upload/thumb/<int:media_id>")
def uploaded_thumb(media_id):
    thumb_dir = app.config["THUMB_FOLDER"]
    return send_from_directory(thumb_dir, "%d.jpg" % media_id,
                               last_modified=datetime.datetime.now())


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('thread_id', db.Integer, db.ForeignKey('thread.id'), primary_key=True)
)   
class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.Integer, db.ForeignKey("board.id"), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    posts = relationship("Post", order_by=Post.datetime)
    last_updated = db.Column(db.DateTime)
    tags = relationship("Tag", secondary=tags, lazy='subquery',
        backref=db.backref('threads', lazy=True))

    def num_media(self):
        return db.session.query(Post).filter(and_(Post.thread == self.id, Post.media != None)).count()
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    bg_style = db.Column(db.String, nullable=True)
    text_style = db.Column(db.String, nullable=True)
    def to_dict(self):
        return {"name" : self.name}
def style_for_tag(tag_name):
    tag = db.session.query(Tag).filter(Tag.name == tag_name).one()
    return {"bg_style" : tag.bg_style, "text_style" : tag.text_style}
app.jinja_env.globals["style_for_tag"] = style_for_tag
    
class ThreadPosts:
    def get(self, thread_id):
        session = db.session
        thread = session.query(Thread).filter(Thread.id == thread_id).one()
        thread.views += 1
        session.add(thread)
        session.commit()
        return jsonify(self.retrieve(thread_id))

    def retrieve(self, thread_id):
        session = db.session
        thread = session.query(Thread).filter(Thread.id == thread_id).one()
        return self._to_json(thread.posts, thread)

    def _to_json(self, posts, thread):
        result = []
        for index, post in enumerate(posts):
            p_dict = dict()
            p_dict["body"] = post.body
            p_dict["datetime"] = post.datetime
            p_dict["id"] = post.id
            if index == 0:
                p_dict["tags"] = thread.tags
            session = db.session
            poster = session.query(Poster).filter(Poster.id == post.poster).one()
            p_dict["poster"] = poster.hex_string
            p_dict["subject"] = post.subject
            p_dict["media"] = post.media
            if post.media:
                p_dict["media_ext"] = session.query(Media).filter(Media.id == post.media).one().ext
            else:
                p_dict["media_ext"] = None
            p_dict["spoiler"] = post.spoiler
            p_dict["slip"] = poster.slip
            p_dict["replies"] = []
            replies = session.query(Reply).filter(Reply.reply_to == post.id).all()
            for reply in replies:
                p_dict["replies"].append(reply.reply_from)
            result.append(p_dict)
        return result
class ThreadPostsResource(ThreadPosts, Resource): pass
rest_api.add_resource(ThreadPostsResource, "/api/v1/thread/<int:thread_id>")

# TODO: Enable \r\n to <br /> support (no more reddit spacing)
class ThreadRootExtension(Extension):
    def extendMarkdown(self, md, _):
        md.postprocessors.add("threadroot", ThreadPostprocessor(), "_end")
class ThreadPostprocessor(Postprocessor):
    def run(self, text):
        return '<div class="col text-left mw-50">%s</div>' % text

def url_for_post(post_id):
    thread = Thread.query.filter(Thread.posts.any(id=post_id)).one()
    return url_for("view_thread", thread_id=thread.id) + "#" + str(post_id)
app.jinja_env.globals["url_for_post"] = url_for_post


class PostReplyExtension(Extension):
    def extendMarkdown(self, md, _):
        postreply = PostReplyPattern()
        md.inlinePatterns.add("postreply", postreply, "_begin")
        # modify the built-in blockquote regexp to only match
        # when one angle bracket is present
        # monkey patching was a mistake
        md.parser.blockprocessors["quote"].RE = re.compile(r"(^|\n)[ ]{0,3}>(?!>)[ ]?(.*)")
class PostReplyPattern(Pattern):
    def __init__(self, markdown_instance=None):
        super().__init__(REPLY_REGEXP, markdown_instance)
    def handleMatch(self, match):
        link = etree.Element("a")
        reply_id = int(match.group(2))
        link.attrib["href"] = url_for_post(reply_id)
        link.text = "&gt;&gt;%s" % reply_id
        return link

def render_for_threads(posts):
    for post in posts:
        post["body"] = markdown(post["body"],
                                extensions=[ThreadRootExtension(), PostReplyExtension()])


@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    render_for_threads(posts)
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    thread.views += 1
    db.session.add(thread)
    db.session.commit()
    board_id = thread.board
    num_posters = db.session.query(Poster).filter(Poster.thread == thread_id).count()
    num_media = thread.num_media()
    return render_template("thread.html", thread_id=thread_id, board_id=board_id, posts=posts, num_views=thread.views, num_media=num_media, num_posters=num_posters)

@app.route("/thread/<int:thread_id>/gallery")
def view_gallery(thread_id):
    posts = ThreadPosts().retrieve(thread_id)
    thread = db.session.query(Thread).filter(Thread.id == thread_id).one()
    board_id = thread.board
    return render_template("gallery.html", thread_id=thread_id, board_id=board_id, posts=posts)


class NewThread:
    def post(self):
        self.post_impl()
    def post_impl(self):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("board", type=int, required=True)
        parser.add_argument("tags", type=str)
        args = parser.parse_args()
        if "media" not in request.files or not request.files["media"].filename:
            raise SubmissionError("A file is required to post a thread!", args["board"])
        tags = []
        if args["tags"]:
            tag_list = args["tags"].replace(" ", "").split(",")
            for tag_name in tag_list:
                tag = db.session.query(Tag).filter(Tag.name == tag_name).one_or_none()
                if tag is None:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tags.append(tag)
        db.session.flush()
        thread = Thread(board=args["board"], views=0, tags=tags)
        # FIXME: use one transaction for all of this, the current state defeats
        # the purpose of having transactions in the first place
        db.session.add(thread)
        db.session.commit()
        NewPost().post(thread_id=thread.id)
        return thread
class NewThreadResource(NewThread, Resource): pass
rest_api.add_resource(NewThreadResource, "/api/v1/thread/new")

@app.route("/thread/new/<int:board_id>")
def new_thread(board_id):
    return render_template("new-thread.html", board_id=board_id)

@app.route("/thread/new", methods=["POST"])
def thread_submit():
    try:
        thread = NewThread().post_impl()
        return redirect(url_for("view_thread", thread_id=thread.id))
    except SubmissionError as e:
        flash(str(e.args[0]))
        return redirect(url_for("new_thread", board_id=e.args[1]))

def gen_poster_id():
    id_chars = "ABCDEF0123456789"
    return ''.join(random.sample(id_chars, 4))
def ip_to_int(ip_str):
    # TODO: IPv6 support
    segments = [int(s) for s in ip_str.split(".")]
    segments.reverse()
    ip_num = 0
    for segment in segments:
        ip_num = ip_num | segment
        ip_num = ip_num << 8
    return ip_num


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    rules = db.Column(db.String, nullable=True)
    threads = relationship("Thread", order_by=desc(Thread.last_updated))


class BoardList:
    def get(self):
        board_query = db.session.query(Board).all()
        boards = []
        for board in board_query:
            b_dict = {}
            b_dict["id"] = board.id
            b_dict["name"] = board.name
            b_dict["media"] = None
            for thread in board.threads:
                op = thread.posts[0]
                if op.media != None:
                    b_dict["media"] = op.media
                    break
            boards.append(b_dict)
        return boards
class BoardListResource(BoardList, Resource): pass
rest_api.add_resource(BoardListResource, "/api/v1/boards/")


@app.route("/boards")
def list_boards():
    return render_template("board-index.html", boards=BoardList().get())


class BoardCatalog:
    def get(self, board_id):
        return jsonify(self.retrieve(board_id))
    def retrieve(self, board_id):
        session = db.session
        board = session.query(Board).filter(Board.id == board_id).one()
        thread_list = board.threads
        return self._to_json(thread_list)
    def _to_json(self, threads):
        result = []
        for thread in threads:
            t_dict = dict()
            op = thread.posts[0]
            t_dict["subject"] = op.subject
            t_dict["last_updated"] = thread.last_updated
            t_dict["body"] = op.body
            t_dict["id"] = thread.id
            t_dict["media"] = op.media
            t_dict["tags"] = thread.tags
            t_dict["views"] = thread.views
            t_dict["num_replies"] = len(thread.posts) - 1
            t_dict["num_media"] = thread.num_media()
            result.append(t_dict)
        return result
class BoardCatalogResource(BoardCatalog, Resource): pass
rest_api.add_resource(BoardCatalogResource, "/api/v1/board/<int:board_id>/catalog")


def render_for_catalog(posts):
    for post in posts:
        post["body"] = markdown(post["body"],
                                extensions=[PostReplyExtension()])

        
@app.route("/board/<int:board_id>")
def view_catalog(board_id):
    threads = BoardCatalog().retrieve(board_id)
    board_name = db.session.query(Board).filter(Board.id == board_id).one().name
    render_for_catalog(threads)
    return render_template("catalog.html", threads=threads, board_id=board_id, board_name=board_name)
@app.route("/rules")
@app.route("/board/<int:board_id>/rules")
def view_rules(board_id=None):
    if board_id:
        board = db.session.query(Board).filter(Board.id == board_id).one()
        return render_template("rules.html", board=board, markdown=markdown)
    return render_template("rules.html", markdown=markdown)

@app.route("/board/<int:board_id>/admin")
def board_admin(board_id):
    if get_slip() and get_slip().is_admin:
        board = db.session.query(Board).filter(Board.id == board_id).one()
        return render_template("board-admin.html", board=board)
    else:
        flash("Only admins can access board administration!")
        return redirect(url_for("view_catalog", board_id=board_id))
@app.route("/board/<int:board_id>/admin", methods=["POST"])
def board_admin_update(board_id):
    if get_slip() is None or get_slip().is_admin is False:
        flash("Only admins can access board administration!")
        return redirect(url_for("view_catalog", board_id=board_id))
    board = db.session.query(Board).filter(Board.id == board_id).one()
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True)
    parser.add_argument("rules", type=str, required=True)
    args = parser.parse_args()
    board.name = args["name"]
    board.rules = args["rules"]
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("view_catalog", board_id=board_id))


@app.route("/faq")
def faq():
    return render_template("faq.html")


class Firehose:
    def get(self):
        return jsonify(self._get_threads())
    def get_impl(self):
        threads = self._get_threads()
        render_for_catalog(threads)
        return threads
    def _get_threads(self):
        raw_threads = db.session.query(Thread).order_by(desc(Thread.last_updated)).limit(10).all()
        threads = BoardCatalog()._to_json(raw_threads)
        return threads
class FirehoseResource(Firehose, Resource): pass
rest_api.add_resource(FirehoseResource, "/api/v1/firehose")

@app.route("/")
def index():
    return render_template("index.html", threads=Firehose().get_impl())
